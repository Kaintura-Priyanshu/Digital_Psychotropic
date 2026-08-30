"""
Qdrant wrapper for the biometric similarity index (Phase 2/3). Runs in
embedded/in-memory mode with zero config (`QdrantClient(location=":memory:")`),
and against a real server once QDRANT_URL is set — same API either way.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.biometrics.face_embedding import EMBEDDING_DIM
from app.core.config import get_settings

logger = logging.getLogger("vector_store")

COLLECTION = "face_embeddings"


class FaceVectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        if settings.QDRANT_URL:
            self._client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)
            logger.info("Connected to Qdrant at %s", settings.QDRANT_URL)
        else:
            self._client = QdrantClient(location=":memory:")
            logger.info("Using embedded in-memory Qdrant instance (dev/demo mode)")

        existing = [c.name for c in self._client.get_collections().collections]
        if COLLECTION not in existing:
            self._client.create_collection(
                collection_name=COLLECTION,
                vectors_config=qmodels.VectorParams(size=EMBEDDING_DIM, distance=qmodels.Distance.COSINE),
            )

    def upsert(self, uip_id: str, vector, payload: Optional[dict] = None) -> None:
        self._client.upsert(
            collection_name=COLLECTION,
            points=[qmodels.PointStruct(id=_id_to_point_id(uip_id), vector=list(map(float, vector)), payload={"uip_id": uip_id, **(payload or {})})],
        )

    def search(self, vector, top_k: int = 5, score_threshold: Optional[float] = None) -> List[dict]:
        hits = self._client.search(
            collection_name=COLLECTION,
            query_vector=list(map(float, vector)),
            limit=top_k,
            score_threshold=score_threshold,
        )
        return [{"uip_id": h.payload.get("uip_id"), "score": h.score} for h in hits]


def _id_to_point_id(uip_id: str) -> int:
    # Qdrant point IDs must be int or UUID; derive a stable int from the UIP id.
    import zlib

    return zlib.crc32(uip_id.encode())


_store: Optional[FaceVectorStore] = None


def get_face_vector_store() -> FaceVectorStore:
    global _store
    if _store is None:
        _store = FaceVectorStore()
    return _store
