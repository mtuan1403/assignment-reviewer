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


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini API Provider (e.g. Gemini 1.5 Flash).
    Leverages Google's generous free tier via direct REST API with JSON schema enforcement.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or getattr(settings, "GEMINI_API_KEY", "")
        self.model = model or getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        self.timeout = timeout

        if not self.api_key:
            logger.warning("GeminiProvider initialized without a GEMINI_API_KEY.")

    def _extract_json(self, raw_text: str) -> dict:
        raw_text = raw_text.strip()
        if "```" in raw_text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
            if match:
                raw_text = match.group(1).strip()
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as e:
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(raw_text[start : end + 1])
            raise LLMException(f"Failed to decode Gemini response as JSON: {e}\nResponse: {raw_text[:200]}")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            raise LLMException("GEMINI_API_KEY is not set. Please set it in backend/.env.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
            },
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        headers = {"Content-Type": "application/json"}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    err_msg = sanitize_sensitive_data(response.text)
                    raise LLMException(f"Gemini API error ({response.status_code}): {err_msg}")

                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates or "content" not in candidates[0]:
                    raise LLMException(f"Gemini returned empty candidate list: {data}")

                parts = candidates[0]["content"].get("parts", [])
                if not parts or "text" not in parts[0]:
                    raise LLMException("Gemini returned empty parts")

                return parts[0]["text"]
        except httpx.RequestError as e:
            raise LLMException(f"Network error connecting to Gemini API: {e}")

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        if not self.api_key:
            raise LLMException("GEMINI_API_KEY is not set.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        schema = response_model.model_json_schema()
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"{prompt}\n\n"
                                f"Respond ONLY with valid JSON strictly conforming to this schema:\n"
                                f"{json.dumps(schema)}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
                "responseMimeType": "application/json",
            },
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [
                    {
                        "text": f"{system_prompt}\nYou are an expert academic evaluator. Respond only in valid JSON conforming to the schema."
                    }
                ]
            }

        headers = {"Content-Type": "application/json"}

        logger.info(f"[Gemini API] Requesting structured output for {response_model.__name__} via model '{self.model}'...")

        last_error = None
        for attempt in range(settings.LLM_MAX_RETRIES):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(url, json=payload, headers=headers)
                    if response.status_code != 200:
                        err_msg = sanitize_sensitive_data(response.text)
                        raise LLMException(f"Gemini API error ({response.status_code}): {err_msg}")

                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates or "content" not in candidates[0]:
                        raise LLMException("No candidate content in Gemini response")

                    parts = candidates[0]["content"].get("parts", [])
                    raw_text = parts[0]["text"]

                    parsed = self._extract_json(raw_text)
                    validated = response_model.model_validate(parsed)
                    logger.info(f"[Gemini API] Successfully received & validated structured {response_model.__name__}.")
                    return validated
            except (LLMException, ValidationError, json.JSONDecodeError) as err:
                last_error = err
                logger.warning(f"Gemini retry {attempt + 1}/{settings.LLM_MAX_RETRIES} due to: {err}")

        raise LLMException(f"Gemini failed to generate structured data: {last_error}")
