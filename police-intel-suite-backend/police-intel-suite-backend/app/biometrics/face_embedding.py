"""
Phase 2 biometric pipeline: turns a face crop into a 512-D embedding.

Real path: `insightface`'s ArcFace (buffalo_l) model — heavy (ONNX + model
download), imported lazily so the app boots without it.

Fallback path (no insightface installed / no model cache available): a
deterministic pseudo-embedding derived from simple pixel statistics. This is
NOT biometrically meaningful — it exists purely so `/api/ingestion/face`
and the Qdrant indexing/search code path are exercisable in dev/demo mode
without a multi-hundred-MB model download. Swap in real ArcFace before any
production or evaluative use.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Optional

import numpy as np

logger = logging.getLogger("face_embedding")

EMBEDDING_DIM = 512

_arcface_app = None
_arcface_load_attempted = False


def _try_load_arcface():
    global _arcface_app, _arcface_load_attempted
    if _arcface_load_attempted:
        return _arcface_app
    _arcface_load_attempted = True
    try:
        import insightface

        app = insightface.app.FaceAnalysis(name="buffalo_l")
        app.prepare(ctx_id=-1)  # CPU
        _arcface_app = app
        logger.info("Loaded ArcFace (insightface buffalo_l) for face embeddings")
    except Exception as exc:  # noqa: BLE001
        logger.warning("insightface unavailable (%s); using stub face embeddings", exc)
        _arcface_app = None
    return _arcface_app


def _stub_embedding(image_bytes: bytes) -> np.ndarray:
    """Deterministic, seeded pseudo-embedding — same input always yields the
    same vector, so similarity search over stub data is at least consistent,
    even though it carries no real biometric signal."""
    digest = hashlib.sha256(image_bytes).digest()
    seed = int.from_bytes(digest[:8], "big")
    rng = np.random.default_rng(seed)
    vec = rng.normal(size=EMBEDDING_DIM).astype(np.float32)
    return vec / np.linalg.norm(vec)


def embed_face(image_bytes: bytes) -> np.ndarray:
    """Return a unit-normalized 512-D embedding for the given image bytes."""
    app = _try_load_arcface()
    if app is not None:
        import cv2

        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        faces = app.get(img)
        if faces:
            emb = faces[0].normed_embedding.astype(np.float32)
            return emb
        logger.info("No face detected by ArcFace; falling back to stub embedding")

    return _stub_embedding(image_bytes)
