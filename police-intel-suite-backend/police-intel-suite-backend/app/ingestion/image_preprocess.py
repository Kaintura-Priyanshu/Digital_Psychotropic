"""
Phase 1 image preprocessing for poor-quality paper FIR scans/photos, ahead
of OCR. Pure OpenCV — no model downloads, so this always runs (opencv-python
still needs to be `pip install`-ed; import is lazy/optional so the rest of
the app works even if it isn't).
"""
from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("image_preprocess")


def _require_cv2():
    try:
        import cv2

        return cv2
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "opencv-python-headless is not installed. `pip install opencv-python-headless` "
            "to enable image preprocessing."
        ) from exc


def preprocess_document(image_bytes: bytes) -> bytes:
    """Grayscale -> Gaussian blur -> adaptive threshold -> deskew.
    Returns PNG-encoded bytes of the cleaned image, ready for OCR."""
    cv2 = _require_cv2()

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes — unsupported or corrupt format")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binarized = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    deskewed = _deskew(binarized, cv2)

    ok, encoded = cv2.imencode(".png", deskewed)
    if not ok:
        raise RuntimeError("Failed to encode preprocessed image")
    return encoded.tobytes()


def _deskew(binarized: np.ndarray, cv2) -> np.ndarray:
    coords = np.column_stack(np.where(binarized < 255))
    if coords.size == 0:
        return binarized
    angle = cv2.minAreaRect(coords)[-1]
    # cv2.minAreaRect angle convention: normalize to [-45, 45]
    angle = -(90 + angle) if angle < -45 else -angle
    (h, w) = binarized.shape
    center = (w // 2, h // 2)
    rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        binarized, rot_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
