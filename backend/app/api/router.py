from fastapi import APIRouter
from backend.app.api.endpoints import health, review

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(review.router, prefix="/reviews", tags=["Reviews"])
