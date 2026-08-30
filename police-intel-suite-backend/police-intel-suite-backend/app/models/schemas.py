from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ThreatTier(str, Enum):
    KINGPIN = "kingpin"
    BROKER = "broker"
    OPERATIVE = "operative"
    INACTIVE = "inactive"


class NodeType(str, Enum):
    SUSPECT = "suspect"
    PHONE = "phone"
    VEHICLE = "vehicle"
    BANK = "bank"


class RelationType(str, Enum):
    CALLED = "CALLED"
    ACCOMPLICE_OF = "ACCOMPLICE_OF"
    HAWALA_TRANSFER = "HAWALA_TRANSFER"
    OWNS = "OWNS"


# ---- Graph ----
class GraphNode(BaseModel):
    id: str
    label: str
    tier: ThreatTier
    type: NodeType
    centrality: float = Field(ge=0, le=1, default=0.0)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: RelationType
    weight: float = Field(ge=0, le=1, default=0.5)


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class GdsRunResult(BaseModel):
    algorithm: str
    communities: Optional[dict] = None
    scores: Optional[dict] = None


# ---- GIS / CDR ----
class CdrTower(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    intensity: float = Field(ge=0, le=1)
    pings: int = 0


# ---- UIP / Dossier ----
class ContactSummary(BaseModel):
    label: str
    count: int


class FinancialTrail(BaseModel):
    account: str
    flagged: bool = False


class UipProfile(BaseModel):
    id: str
    name: str
    alias: List[str] = []
    tier: ThreatTier
    face_match_confidence: float = Field(ge=0, le=1, default=0.0)
    ipc_sections: List[str] = []
    last_known_location: str = ""
    contacts: List[ContactSummary] = []
    vehicles: List[str] = []
    financial_trails: List[FinancialTrail] = []


class DossierExportResult(BaseModel):
    uip_id: str
    sha256: str
    filename: str
    generated_at: str


# ---- Search ----
class SearchQuery(BaseModel):
    text: Optional[str] = None
    face_vector: Optional[List[float]] = None
    filters: dict = {}


class SearchHit(BaseModel):
    uip_id: str
    name: str
    score: float
    matched_on: str


class SearchResponse(BaseModel):
    query_echo: str
    hits: List[SearchHit]
    cypher: Optional[str] = None  # the Text-to-Cypher translation, for transparency


# ---- Ingestion ----
class ExtractedEntity(BaseModel):
    entity_type: str  # ACCUSED | ALIAS | IPC_SECTION | WEAPON | LOCATION | PHONE
    value: str
    confidence: float = Field(ge=0, le=1, default=0.0)


class IngestionResult(BaseModel):
    document_id: str
    raw_text: str
    language_detected: str
    entities: List[ExtractedEntity]
    evidence_sha256: str


class CdrRecord(BaseModel):
    caller: str
    callee: str
    timestamp: str
    duration_seconds: int
    tower_id: Optional[str] = None
    carrier: str  # Airtel | Jio | Vi | ...
