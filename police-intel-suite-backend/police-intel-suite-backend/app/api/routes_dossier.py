import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.dossier_agent import DossierAgent
from app.core.security import Role, require_role
from app.models.schemas import DossierExportResult, UipProfile
from data.seed import UIP_PROFILES

router = APIRouter(prefix="/dossier", tags=["dossier"])
_dossier_agent = DossierAgent()


@router.get("/{uip_id}", response_model=UipProfile)
async def get_profile(uip_id: str, _=Depends(require_role(Role.VIEWER))):
    """Powers the frontend's slide-out profile drawer."""
    profile = UIP_PROFILES.get(uip_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No UIP found for '{uip_id}'")
    return profile


@router.post("/{uip_id}/export", response_model=DossierExportResult)
async def export_dossier(uip_id: str, _=Depends(require_role(Role.INVESTIGATOR))):
    """Runs Agent 4: compiles the profile into a court-admissible PDF and
    returns its SHA-256 digest + filename. Fetch the bytes via the
    `/export/download` endpoint below, or extend this to persist to S3/blob
    storage and return a signed URL instead."""
    profile = UIP_PROFILES.get(uip_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No UIP found for '{uip_id}'")
    return _dossier_agent.export_pdf(profile)


@router.get("/{uip_id}/export/download")
async def download_dossier(uip_id: str, _=Depends(require_role(Role.INVESTIGATOR))):
    profile = UIP_PROFILES.get(uip_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No UIP found for '{uip_id}'")
    pdf_bytes = _dossier_agent._render_pdf(profile)  # noqa: SLF001 — internal reuse within the same module's agent
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="dossier_{uip_id}.pdf"'},
    )
