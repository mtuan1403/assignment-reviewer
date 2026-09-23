import pytest
from pydantic import BaseModel
from backend.app.services.llm.base import BaseLLMProvider, LLMException
from backend.app.services.llm.fallback_provider import FallbackLLMProvider


class SampleModel(BaseModel):
    title: str
    score: int


class FailingPrimaryProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        raise LLMException("HTTP 429: Resource has been exhausted (rate limit exceeded).")

    def generate_structured(self, prompt: str, response_model, system_prompt: str = None):
        raise LLMException("HTTP 429: Resource has been exhausted (rate limit exceeded).")


class WorkingFallbackProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        return "fallback response text"

    def generate_structured(self, prompt: str, response_model, system_prompt: str = None):
        return response_model(title="Fallback Model", score=95)


def test_fallback_on_primary_failure():
    primary = FailingPrimaryProvider()
    fallback = WorkingFallbackProvider()
    hybrid = FallbackLLMProvider(primary_provider=primary, fallback_provider=fallback)

    # 1. Text generation should fall back smoothly without throwing
    text_out = hybrid.generate_text("Evaluate this draft")
    assert text_out == "fallback response text"

    # 2. Structured generation should fall back smoothly without throwing
    struct_out = hybrid.generate_structured("Evaluate rubric", SampleModel)
    assert struct_out.title == "Fallback Model"
    assert struct_out.score == 95
