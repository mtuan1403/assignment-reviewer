from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.api.router import api_router
from backend.app.services.parser.base import ParsingException, EmptyDocumentException, ScannedDocumentException

logger = get_logger("main")

app = FastAPI(
    title="AI Assignment Reviewer",
    description="A local-first academic assignment review system using multi-stage RAG and evidence grounding.",
    version="1.0.0",
)

# CORS configuration for local React Vite UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.exception_handler(EmptyDocumentException)
async def empty_document_handler(request: Request, exc: EmptyDocumentException):
    return JSONResponse(
        status_code=400,
        content={"error": "EmptyDocumentError", "message": str(exc)},
    )


@app.exception_handler(ScannedDocumentException)
async def scanned_document_handler(request: Request, exc: ScannedDocumentException):
    return JSONResponse(
        status_code=400,
        content={"error": "ScannedDocumentError", "message": str(exc)},
    )


@app.exception_handler(ParsingException)
async def parsing_exception_handler(request: Request, exc: ParsingException):
    return JSONResponse(
        status_code=400,
        content={"error": "ParsingError", "message": str(exc)},
    )


@app.on_event("startup")
def startup_event():
    logger.info("==================================================")
    logger.info("  AI Assignment Reviewer Backend Initialized")
    logger.info(f"  Mode: Local Development Only ({settings.APP_ENV})")
    logger.info(f"  LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"  Embedding Provider: {settings.EMBEDDING_PROVIDER}")
    logger.info(f"  Data Directory: {settings.base_data_dir}")
    logger.info("==================================================")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
