from typing import List

from fastapi import APIRouter, Depends

from app.core.security import Role, require_role
from app.models.schemas import CdrTower
from data.seed import CDR_TOWERS

router = APIRouter(prefix="/gis", tags=["gis"])


@router.get("/towers", response_model=List[CdrTower])
async def list_towers(_=Depends(require_role(Role.VIEWER))):
    """Powers the frontend's Leaflet map — tower markers + heatmap weights.

    Swap this for a real query once towers/pings are ingested via the CDR
    normalizer and persisted (e.g. Postgres/PostGIS or a Neo4j :Tower label).
    """
    return CDR_TOWERS
