from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini", "ollama", "openai", or "mock"
    LLM_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Google Gemini Settings (Free Tier)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Local Ollama Settings (Gemma 2 / Llama 3)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma2"

    # Enable automatic fallback to local if primary fails
    USE_FALLBACK: bool = True

    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_RETRIES: int = 3
    LLM_TIMEOUT: float = 60.0

    # Embedding Settings
    EMBEDDING_PROVIDER: str = "sentence-transformers"  # "sentence-transformers" or "tfidf"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Storage paths
    DATA_DIR: str = "data"

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def base_data_dir(self) -> Path:
        base = Path(__file__).resolve().parent.parent.parent / self.DATA_DIR
        base.mkdir(parents=True, exist_ok=True)
        return base

    @property
    def uploads_dir(self) -> Path:
        p = self.base_data_dir / "uploads"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def extracted_dir(self) -> Path:
        p = self.base_data_dir / "extracted"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def vector_store_dir(self) -> Path:
        p = self.base_data_dir / "vector_store"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def reviews_dir(self) -> Path:
        p = self.base_data_dir / "reviews"
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
