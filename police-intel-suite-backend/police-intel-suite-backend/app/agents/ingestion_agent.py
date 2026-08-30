"""
Agent 1 — Ingestion & Multi-Lingual Parsing Agent.

Detects document type, routes through OpenCV preprocessing + dual OCR, then
Indic-BERT/rule-based entity extraction, and hands back a validated
`IngestionResult`. This is the automated first read of every incoming FIR.
"""
from __future__ import annotations

from app.core.encryption import hash_evidence
from app.ingestion.image_preprocess import preprocess_document
from app.ingestion.ocr import run_ocr
from app.models.schemas import IngestionResult
from app.nlp.entity_extraction import extract_entities


class IngestionAgent:
    name = "ingestion_agent"

    def process_document(self, document_id: str, image_bytes: bytes) -> IngestionResult:
        cleaned = preprocess_document(image_bytes)
        ocr_result = run_ocr(cleaned)
        entities = extract_entities(ocr_result["text"])

        return IngestionResult(
            document_id=document_id,
            raw_text=ocr_result["text"],
            language_detected=ocr_result["language_detected"],
            entities=entities,
            evidence_sha256=hash_evidence(image_bytes),
        )
