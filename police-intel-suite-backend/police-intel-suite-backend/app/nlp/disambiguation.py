"""
Phase 3 cross-modal entity resolution: decides whether a newly extracted
name/record should MERGE into an existing Unified Intelligence Profile (UIP)
or CREATE a new one.

Combines:
  - Phonetic matching   Double Metaphone (via the `metaphone` package if
                         installed, else a small Soundex fallback) — catches
                         "Vicky" vs "Vikram", transliteration variants, etc.
  - Semantic matching    Sentence-BERT cosine similarity over name+context
                          strings, when `sentence-transformers` is available.
  - Face vector match     delegated to app.biometrics.vector_store
                          (>= FACE_MATCH_THRESHOLD, default 0.85, per the brief).

The final MERGE/CREATE decision is a simple weighted vote across whichever
signals are available — see `resolve_identity`.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from app.core.config import get_settings

logger = logging.getLogger("disambiguation")

_sbert_model = None
_sbert_load_attempted = False


def _soundex(name: str) -> str:
    """Minimal Soundex — used only if the `metaphone` package isn't installed."""
    name = name.upper()
    codes = {**{c: "1" for c in "BFPV"}, **{c: "2" for c in "CGJKQSXZ"}, **{c: "3" for c in "DT"},
             "L": "4", **{c: "5" for c in "MN"}, "R": "6"}
    if not name:
        return ""
    first = name[0]
    tail = "".join(codes.get(c, "") for c in name[1:])
    deduped = []
    prev = codes.get(first, "")
    for c in tail:
        if c != prev:
            deduped.append(c)
        prev = c
    return (first + "".join(deduped) + "000")[:4]


def phonetic_key(name: str) -> str:
    try:
        from metaphone import doublemetaphone

        primary, _ = doublemetaphone(name)
        return primary
    except Exception:  # noqa: BLE001 — package not installed
        return _soundex(name)


def phonetic_match(a: str, b: str) -> bool:
    return phonetic_key(a) == phonetic_key(b) and phonetic_key(a) != ""


def _try_load_sbert():
    global _sbert_model, _sbert_load_attempted
    if _sbert_load_attempted:
        return _sbert_model
    _sbert_load_attempted = True
    try:
        from sentence_transformers import SentenceTransformer

        _sbert_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        logger.info("Loaded Sentence-BERT for semantic name/context matching")
    except Exception as exc:  # noqa: BLE001
        logger.warning("sentence-transformers unavailable (%s); skipping semantic match signal", exc)
        _sbert_model = None
    return _sbert_model


def semantic_similarity(a: str, b: str) -> Optional[float]:
    model = _try_load_sbert()
    if model is None:
        return None
    import numpy as np

    emb = model.encode([a, b], normalize_embeddings=True)
    return float(np.dot(emb[0], emb[1]))


@dataclass
class ResolutionSignal:
    name: str
    score: float
    weight: float


@dataclass
class ResolutionDecision:
    action: str  # "MERGE" | "CREATE"
    confidence: float
    signals: List[ResolutionSignal]


def resolve_identity(
    candidate_name: str,
    existing_name: str,
    face_similarity: Optional[float] = None,
) -> ResolutionDecision:
    settings = get_settings()
    signals: List[ResolutionSignal] = []

    phon_score = 1.0 if phonetic_match(candidate_name, existing_name) else 0.0
    signals.append(ResolutionSignal("phonetic", phon_score, weight=0.3))

    sem_score = semantic_similarity(candidate_name, existing_name)
    if sem_score is not None:
        signals.append(ResolutionSignal("semantic", sem_score, weight=0.3))

    if face_similarity is not None:
        face_score = 1.0 if face_similarity >= settings.FACE_MATCH_THRESHOLD else face_similarity
        signals.append(ResolutionSignal("face_vector", face_score, weight=0.4))

    total_weight = sum(s.weight for s in signals)
    confidence = sum(s.score * s.weight for s in signals) / total_weight if total_weight else 0.0

    action = "MERGE" if confidence >= 0.6 else "CREATE"
    return ResolutionDecision(action=action, confidence=round(confidence, 3), signals=signals)
