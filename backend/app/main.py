from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# Load backend/.env before other imports read os.environ
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.repositories.faiss_repository import FaissIndexDimensionMismatchError


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="MVP backend for AI-assisted code understanding (Python repos first).",
    )

    @app.exception_handler(FaissIndexDimensionMismatchError)
    async def _faiss_dimension_mismatch(
        _request: Request, exc: FaissIndexDimensionMismatchError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
