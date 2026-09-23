import json
import re
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel, ValidationError

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.services.llm.base import BaseLLMProvider, LLMException

logger = get_logger(__name__)
T = TypeVar("T", bound=BaseModel)


class OllamaProvider(BaseLLMProvider):
    """
    Local Ollama Provider (e.g. gemma2:9b, gemma2:2b, llama3.2).
    Runs completely on-device with zero internet connectivity and zero API costs.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 120.0,
    ):
        self.base_url = (base_url or getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or getattr(settings, "OLLAMA_MODEL", "gemma2")
        self.timeout = timeout

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
            raise LLMException(f"Failed to decode Ollama response as JSON: {e}\nRaw: {raw_text[:200]}")

    def is_available(self) -> bool:
        """Check if local Ollama daemon is running."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": settings.LLM_TEMPERATURE},
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/api/chat", json=payload)
                if res.status_code != 200:
                    raise LLMException(f"Ollama error ({res.status_code}): {res.text}")
                data = res.json()
                return data["message"]["content"]
        except httpx.RequestError as e:
            raise LLMException(f"Could not connect to local Ollama daemon at {self.base_url}: {e}")

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        schema = response_model.model_json_schema()
        augmented_prompt = (
            f"{prompt}\n\n"
            f"You MUST reply ONLY with valid JSON strictly conforming to this schema:\n"
            f"{json.dumps(schema)}"
        )

        messages = []
        sys_msg = (system_prompt or "") + "\nRespond strictly in valid JSON matching the schema."
        messages.append({"role": "system", "content": sys_msg})
        messages.append({"role": "user", "content": augmented_prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "format": "json",
            "stream": False,
            "options": {"temperature": settings.LLM_TEMPERATURE},
        }

        last_error = None
        for attempt in range(settings.LLM_MAX_RETRIES):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    res = client.post(f"{self.base_url}/api/chat", json=payload)
                    if res.status_code != 200:
                        raise LLMException(f"Ollama error ({res.status_code}): {res.text}")
                    data = res.json()
                    raw_text = data["message"]["content"]
                    parsed = self._extract_json(raw_text)
                    return response_model.model_validate(parsed)
            except (LLMException, ValidationError, json.JSONDecodeError, httpx.RequestError) as err:
                last_error = err
                logger.warning(f"Ollama retry {attempt + 1}/{settings.LLM_MAX_RETRIES} due to: {err}")

        raise LLMException(f"Ollama failed to generate structured data: {last_error}")
