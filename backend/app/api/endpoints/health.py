from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "storage_dirs": {
            "uploads": str(settings.uploads_dir),
            "vector_store": str(settings.vector_store_dir),
            "reviews": str(settings.reviews_dir),
        },
    }
