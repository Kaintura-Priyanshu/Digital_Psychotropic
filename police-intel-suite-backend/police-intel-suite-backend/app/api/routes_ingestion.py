import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.agents.ingestion_agent import IngestionAgent
from app.core.security import Role, require_role
from app.ingestion.cdr_normalizer import normalize_and_stream
from app.models.schemas import IngestionResult

router = APIRouter(prefix="/ingestion", tags=["ingestion"])
_ingestion_agent = IngestionAgent()


@router.post("/document", response_model=IngestionResult)
async def ingest_document(file: UploadFile = File(...), _=Depends(require_role(Role.INVESTIGATOR))):
    """Runs Agent 1: OpenCV preprocessing -> dual OCR -> entity extraction.

    Accepts a photographed/scanned FIR (PNG/JPG). Requires opencv-python and
    at least one of pytesseract/easyocr to be installed — see requirements.txt.
    """
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file upload")

    document_id = f"DOC-{uuid.uuid4().hex[:10]}"
    try:
        return _ingestion_agent.process_document(document_id, image_bytes)
    except RuntimeError as exc:
        # OCR/image deps not installed — a clear 503 beats a stack trace.
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/cdr")
async def ingest_cdr(
    file: UploadFile = File(...),
    carrier: str | None = Form(default=None, description="airtel | jio | vi — auto-detected if omitted"),
    _=Depends(require_role(Role.INVESTIGATOR)),
):
    """Normalizes a carrier CDR CSV export and streams each row to Kafka
    (`raw-crimes-stream`), per the Phase 1 CDR stream processor."""
    csv_bytes = await file.read()
    try:
        streamed = normalize_and_stream(csv_bytes, carrier=carrier)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"records_streamed": streamed, "topic": "raw-crimes-stream"}
