from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.services.llm.base import BaseLLMProvider
from backend.app.services.llm.openai_provider import OpenAIProvider
from backend.app.services.llm.mock_provider import MockProvider
from backend.app.services.llm.gemini_provider import GeminiProvider
from backend.app.services.llm.ollama_provider import OllamaProvider
from backend.app.services.llm.fallback_provider import FallbackLLMProvider

logger = get_logger(__name__)


class LLMProviderFactory:
    _instance: BaseLLMProvider = None

    @classmethod
    def get_local_fallback(cls) -> BaseLLMProvider:
        """Determines best local fallback: Ollama (if running) or MockProvider."""
        ollama = OllamaProvider()
        if ollama.is_available():
            logger.info(f"Ollama local daemon detected at {settings.OLLAMA_BASE_URL} ({settings.OLLAMA_MODEL}). Using as local fallback.")
            return ollama
        logger.info("Ollama daemon not running. Using deterministic MockProvider as local fallback.")
        return MockProvider()

    @classmethod
    def get_provider(cls, force_mock: bool = False) -> BaseLLMProvider:
        if force_mock:
            return MockProvider()

        provider_name = settings.LLM_PROVIDER.lower().strip()

        # 1. Google Gemini (Free Tier) - With automatic Fallback to Local
        if provider_name == "gemini":
            if not settings.GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY is empty. Falling back directly to local provider.")
                return cls.get_local_fallback()

            gemini = GeminiProvider()
            if settings.USE_FALLBACK:
                fallback = cls.get_local_fallback()
                logger.info("Configured GeminiProvider as Primary with FallbackLLMProvider.")
                return FallbackLLMProvider(primary_provider=gemini, fallback_provider=fallback)
            return gemini

        # 2. Local Ollama (Gemma 2 / Llama 3)
        elif provider_name == "ollama":
            ollama = OllamaProvider()
            if not ollama.is_available():
                logger.warning(f"Ollama daemon not reachable at {settings.OLLAMA_BASE_URL}. Falling back to MockProvider.")
                return MockProvider()
            return ollama

        # 3. OpenAI
        elif provider_name == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning("LLM_PROVIDER is set to 'openai' but OPENAI_API_KEY is empty. Falling back to MockProvider.")
                return MockProvider()
            return OpenAIProvider()

        # 4. Mock / Offline testing
        elif provider_name == "mock":
            return MockProvider()
        else:
            logger.warning(f"Unknown LLM_PROVIDER '{provider_name}'. Defaulting to MockProvider.")
            return MockProvider()

