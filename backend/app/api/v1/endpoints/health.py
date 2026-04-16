from typing import Dict

from fastapi import APIRouter

from app.embeddings.store import get_embedding_store_config

router = APIRouter()


@router.get("/health")
def health_check() -> Dict[str, str]:
    store = get_embedding_store_config()
    return {
        "status": "ok",
        "embedding_backend": store.backend,
        "embedding_dimension": str(store.provider.dimension),
    }
