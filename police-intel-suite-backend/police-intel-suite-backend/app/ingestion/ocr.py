"""
Phase 1 dual-OCR: Tesseract handles English/Latin script, EasyOCR handles
Devanagari/Hindi, so code-mixed Hinglish FIRs get both scripts read
correctly and merged into one text block.

Both engines are optional, heavy system/model dependencies (tesseract-ocr
binary; EasyOCR's torch-backed model download) — imported lazily. If
neither is available, `run_ocr` raises a clear error rather than silently
returning empty text, since OCR output feeding directly into NLP/entity
extraction with no visibility into a silent failure would be worse than
failing loudly.
"""
from __future__ import annotations

import io
import logging

logger = logging.getLogger("ocr")


def _run_tesseract(image_bytes: bytes) -> str:
    import pytesseract
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(img, lang="eng")


def _run_easyocr(image_bytes: bytes) -> str:
    import easyocr
    import numpy as np

    reader = _get_easyocr_reader()
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    import cv2

    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    results = reader.readtext(img, detail=0, paragraph=True)
    return "\n".join(results)


_easyocr_reader = None


def _get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr

        _easyocr_reader = easyocr.Reader(["hi", "en"], gpu=False)
    return _easyocr_reader


def run_ocr(image_bytes: bytes) -> dict:
    """Runs both engines where available and merges output.

    Returns: {"text": str, "engines_used": [str], "language_detected": str}
    """
    text_parts: list[str] = []
    engines_used: list[str] = []

    try:
        english_text = _run_tesseract(image_bytes)
        if english_text.strip():
            text_parts.append(english_text.strip())
            engines_used.append("tesseract")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Tesseract unavailable/failed (%s)", exc)

    try:
        hindi_text = _run_easyocr(image_bytes)
        if hindi_text.strip():
            text_parts.append(hindi_text.strip())
            engines_used.append("easyocr")
    except Exception as exc:  # noqa: BLE001
        logger.warning("EasyOCR unavailable/failed (%s)", exc)

    if not engines_used:
        raise RuntimeError(
            "No OCR engine available. Install `pytesseract` + the tesseract-ocr "
            "system package, and/or `easyocr`, to enable document ingestion."
        )

    merged = "\n".join(text_parts)
    language_detected = "hi+en" if "easyocr" in engines_used and "tesseract" in engines_used else (
        "hi" if "easyocr" in engines_used else "en"
    )
    return {"text": merged, "engines_used": engines_used, "language_detected": language_detected}
