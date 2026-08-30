"""
Phase 2 NLP pipeline: pulls structured entities (accused names, aliases,
IPC/BNS sections, weapons, locations, phone numbers) out of raw
(often code-mixed Hinglish) FIR text.

Real path: a HuggingFace `transformers` NER pipeline over an Indic-BERT
checkpoint (e.g. `ai4bharat/indic-bert` fine-tuned for NER), imported
lazily so the app boots without a multi-GB model download.

Fallback path: regex/gazetteer rules for the structured fields that have a
reliable surface pattern (IPC/BNS sections, phone numbers) plus a small
weapons gazetteer — good enough to exercise the ingestion pipeline and API
contract in dev/demo mode. Free-text name/location extraction genuinely
needs the model; the fallback returns nothing for those rather than
guessing.
"""
from __future__ import annotations

import logging
import re
from typing import List

from app.models.schemas import ExtractedEntity

logger = logging.getLogger("entity_extraction")

_IPC_BNS_PATTERN = re.compile(r"\b(?:IPC|BNS)\s?\d{1,3}[A-Za-z]?(?:\(\d+\))?\b", re.IGNORECASE)
_PHONE_PATTERN = re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b")
_WEAPON_GAZETTEER = ["knife", "pistol", "revolver", "rifle", "chaku", "katta", "sword", "gun"]

_ner_pipeline = None
_ner_load_attempted = False


def _try_load_indic_bert():
    global _ner_pipeline, _ner_load_attempted
    if _ner_load_attempted:
        return _ner_pipeline
    _ner_load_attempted = True
    try:
        from transformers import pipeline

        _ner_pipeline = pipeline("ner", model="ai4bharat/indic-bert", aggregation_strategy="simple")
        logger.info("Loaded Indic-BERT NER pipeline")
    except Exception as exc:  # noqa: BLE001
        logger.warning("transformers/Indic-BERT unavailable (%s); using rule-based entity extraction", exc)
        _ner_pipeline = None
    return _ner_pipeline


def extract_entities(text: str) -> List[ExtractedEntity]:
    entities: List[ExtractedEntity] = []

    for match in _IPC_BNS_PATTERN.finditer(text):
        entities.append(ExtractedEntity(entity_type="IPC_SECTION", value=match.group(0).upper(), confidence=0.95))

    for match in _PHONE_PATTERN.finditer(text):
        entities.append(ExtractedEntity(entity_type="PHONE", value=match.group(0), confidence=0.9))

    lowered = text.lower()
    for weapon in _WEAPON_GAZETTEER:
        if weapon in lowered:
            entities.append(ExtractedEntity(entity_type="WEAPON", value=weapon, confidence=0.7))

    ner = _try_load_indic_bert()
    if ner is not None:
        for ent in ner(text):
            entities.append(
                ExtractedEntity(
                    entity_type=_map_ner_label(ent["entity_group"]),
                    value=ent["word"],
                    confidence=float(ent["score"]),
                )
            )
    else:
        logger.debug("Skipping ACCUSED/ALIAS/LOCATION extraction — requires the Indic-BERT model")

    return entities


def _map_ner_label(label: str) -> str:
    return {
        "PER": "ACCUSED",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "MISC": "ALIAS",
    }.get(label.upper(), label.upper())
