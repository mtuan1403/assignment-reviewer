import json
import re
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel, ValidationError

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, sanitize_sensitive_data
from backend.app.services.llm.base import BaseLLMProvider, LLMException

logger = get_logger(__name__)
T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.LLM_MODEL
        self.base_url = (base_url or settings.OPENAI_BASE_URL).rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            logger.warning("OpenAIProvider initialized without an OPENAI_API_KEY.")

    def _extract_json(self, raw_text: str) -> dict:
        raw_text = raw_text.strip()
        # Handle markdown code blocks
        if "```" in raw_text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
            if match:
                raw_text = match.group(1).strip()
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as e:
            # Fallback: search for first '{' and last '}'
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(raw_text[start : end + 1])
            raise LLMException(f"Failed to decode LLM response as JSON: {e}\nRaw response: {raw_text[:200]}...")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            raise LLMException("OPENAI_API_KEY is not set. Please set it in .env or switch to LLM_PROVIDER=mock.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.LLM_TEMPERATURE,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                if response.status_code != 200:
                    err_body = sanitize_sensitive_data(response.text)
                    raise LLMException(f"OpenAI API error ({response.status_code}): {err_body}")

                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.RequestError as e:
            raise LLMException(f"Network error connecting to OpenAI API: {e}")

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        augmented_prompt = (
            f"{prompt}\n\n"
            f"You MUST respond ONLY with valid JSON matching the following JSON Schema:\n"
            f"```json\n{schema_json}\n```\n"
            f"Do not include any conversational filler, markdown intro, or explanations outside the JSON."
        )

        sys_prompt = (system_prompt or "") + "\nYou are an expert academic evaluator. Always return strictly valid JSON."

        last_error = None
        for attempt in range(settings.LLM_MAX_RETRIES):
            try:
                raw_response = self.generate_text(augmented_prompt, system_prompt=sys_prompt)
                parsed_dict = self._extract_json(raw_response)
                return response_model.model_validate(parsed_dict)
            except (LLMException, ValidationError, json.JSONDecodeError) as err:
                last_error = err
                logger.warning(f"Retry {attempt + 1}/{settings.LLM_MAX_RETRIES} due to error: {err}")

        raise LLMException(f"Failed to generate structured data after {settings.LLM_MAX_RETRIES} attempts: {last_error}")
