from typing import Type, TypeVar, Optional
from pydantic import BaseModel

from backend.app.core.logging import get_logger
from backend.app.services.llm.base import BaseLLMProvider, LLMException

logger = get_logger(__name__)
T = TypeVar("T", bound=BaseModel)


class FallbackLLMProvider(BaseLLMProvider):
    """
    Hybrid Resilient LLM Provider:
    Attempts the Primary Provider (e.g. Google Gemini 1.5 Flash Free Tier).
    If it fails due to rate limits (HTTP 429), quota limits, billing restrictions,
    or network connectivity issues, it automatically falls back to the Local Provider
    (e.g. Local Gemma via Ollama, or deterministic local engine) without interrupting the review.
    """

    def __init__(self, primary_provider: BaseLLMProvider, fallback_provider: BaseLLMProvider):
        self.primary = primary_provider
        self.fallback = fallback_provider
        self.last_active_provider = primary_provider

    @property
    def provider_name(self) -> str:
        return self.last_active_provider.provider_name

    @property
    def model_name(self) -> str:
        return getattr(self.last_active_provider, "model", getattr(self.last_active_provider, "model_name", "unknown"))

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            res = self.primary.generate_text(prompt, system_prompt=system_prompt)
            self.last_active_provider = self.primary
            return res
        except Exception as e:
            self.last_active_provider = self.fallback
            logger.warning(
                f"[FALLBACK TRIGGERED] Primary LLM provider ({self.primary.__class__.__name__}) failed: {e}. "
                f"Switching automatically to fallback provider ({self.fallback.__class__.__name__})."
            )
            return self.fallback.generate_text(prompt, system_prompt=system_prompt)

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        try:
            res = self.primary.generate_structured(
                prompt, response_model=response_model, system_prompt=system_prompt
            )
            self.last_active_provider = self.primary
            return res
        except Exception as e:
            self.last_active_provider = self.fallback
            logger.warning(
                f"[FALLBACK TRIGGERED] Primary LLM provider ({self.primary.__class__.__name__}) failed: {e}. "
                f"Switching automatically to fallback provider ({self.fallback.__class__.__name__})."
            )
            return self.fallback.generate_structured(
                prompt, response_model=response_model, system_prompt=system_prompt
            )

