"""
Seed data for dev/demo mode. Mirrors `police-intel-suite-frontend/lib/mockData.ts`
node-for-node so the frontend and backend agree on shape while the real
Neo4j / Qdrant / CDR pipelines are being wired up.
"""
from app.models.schemas import (
    CdrTower,
    ContactSummary,
    FinancialTrail,
    GraphEdge,
    GraphNode,
    NodeType,
    RelationType,
    ThreatTier,
    UipProfile,
)

GRAPH_NODES = [
    GraphNode(id="S-1042", label="R. Malhotra", tier=ThreatTier.KINGPIN, type=NodeType.SUSPECT, centrality=0.95),
    GraphNode(id="S-1103", label="V. Iyer", tier=ThreatTier.BROKER, type=NodeType.SUSPECT, centrality=0.72),
    GraphNode(id="S-1187", label="A. Qureshi", tier=ThreatTier.BROKER, type=NodeType.SUSPECT, centrality=0.68),
    GraphNode(id="S-1224", label="D. Fernandes", tier=ThreatTier.OPERATIVE, type=NodeType.SUSPECT, centrality=0.41),
    GraphNode(id="S-1256", label="K. Reddy", tier=ThreatTier.OPERATIVE, type=NodeType.SUSPECT, centrality=0.38),
    GraphNode(id="S-1299", label="P. Sharma", tier=ThreatTier.OPERATIVE, type=NodeType.SUSPECT, centrality=0.33),
    GraphNode(id="S-1310", label="N. Bhatt", tier=ThreatTier.INACTIVE, type=NodeType.SUSPECT, centrality=0.19),
    GraphNode(id="P-7841", label="+91 98\u2022\u2022\u202241", tier=ThreatTier.BROKER, type=NodeType.PHONE, centrality=0.55),
    GraphNode(id="P-7902", label="+91 87\u2022\u2022\u202202", tier=ThreatTier.OPERATIVE, type=NodeType.PHONE, centrality=0.30),
    GraphNode(id="V-2210", label="MH-04 KL 2210", tier=ThreatTier.OPERATIVE, type=NodeType.VEHICLE, centrality=0.27),
    GraphNode(id="B-5561", label="Acct \u2022\u2022\u20225561", tier=ThreatTier.BROKER, type=NodeType.BANK, centrality=0.60),
    GraphNode(id="B-5602", label="Acct \u2022\u2022\u20225602", tier=ThreatTier.INACTIVE, type=NodeType.BANK, centrality=0.22),
]

GRAPH_EDGES = [
    GraphEdge(id="e1", source="S-1042", target="S-1103", relation=RelationType.ACCOMPLICE_OF, weight=0.9),
    GraphEdge(id="e2", source="S-1042", target="S-1187", relation=RelationType.ACCOMPLICE_OF, weight=0.8),
    GraphEdge(id="e3", source="S-1103", target="P-7841", relation=RelationType.OWNS, weight=0.5),
    GraphEdge(id="e4", source="S-1187", target="B-5561", relation=RelationType.HAWALA_TRANSFER, weight=0.85),
    GraphEdge(id="e5", source="B-5561", target="B-5602", relation=RelationType.HAWALA_TRANSFER, weight=0.4),
    GraphEdge(id="e6", source="S-1224", target="P-7841", relation=RelationType.CALLED, weight=0.6),
    GraphEdge(id="e7", source="S-1256", target="P-7841", relation=RelationType.CALLED, weight=0.55),
    GraphEdge(id="e8", source="S-1299", target="P-7902", relation=RelationType.CALLED, weight=0.3),
    GraphEdge(id="e9", source="S-1224", target="V-2210", relation=RelationType.OWNS, weight=0.7),
    GraphEdge(id="e10", source="S-1310", target="P-7902", relation=RelationType.CALLED, weight=0.15),
    GraphEdge(id="e11", source="S-1103", target="S-1224", relation=RelationType.ACCOMPLICE_OF, weight=0.45),
    GraphEdge(id="e12", source="S-1187", target="S-1256", relation=RelationType.ACCOMPLICE_OF, weight=0.4),
]

CDR_TOWERS = [
    CdrTower(id="T-01", name="Andheri East BTS-14", lat=19.1197, lng=72.8697, intensity=0.9, pings=214),
    CdrTower(id="T-02", name="Bandra Kurla BTS-08", lat=19.0662, lng=72.8697, intensity=0.75, pings=168),
    CdrTower(id="T-03", name="Dadar West BTS-22", lat=19.0186, lng=72.8437, intensity=0.6, pings=122),
    CdrTower(id="T-04", name="Powai BTS-05", lat=19.1176, lng=72.9060, intensity=0.45, pings=88),
    CdrTower(id="T-05", name="Chembur BTS-11", lat=19.0522, lng=72.9006, intensity=0.3, pings=54),
    CdrTower(id="T-06", name="Kurla BTS-19", lat=19.0728, lng=72.8826, intensity=0.55, pings=101),
]

UIP_PROFILES = {
    "S-1042": UipProfile(
        id="S-1042",
        name="Rajeev Malhotra",
        alias=["Raja", "RM"],
        tier=ThreatTier.KINGPIN,
        face_match_confidence=0.94,
        ipc_sections=["BNS 111", "BNS 61(2)", "IPC 420"],
        last_known_location="Andheri East, Mumbai",
        contacts=[ContactSummary(label="High-risk contacts", count=6), ContactSummary(label="Verified associates", count=11)],
        vehicles=["MH-02 CX 7743"],
        financial_trails=[FinancialTrail(account="Acct \u2022\u2022\u20225561", flagged=True), FinancialTrail(account="Acct \u2022\u2022\u20229012", flagged=False)],
    ),
    "S-1103": UipProfile(
        id="S-1103",
        name="Vikram Iyer",
        alias=["Vicky"],
        tier=ThreatTier.BROKER,
        face_match_confidence=0.88,
        ipc_sections=["BNS 61(2)"],
        last_known_location="Bandra Kurla Complex, Mumbai",
        contacts=[ContactSummary(label="High-risk contacts", count=3), ContactSummary(label="Verified associates", count=7)],
        vehicles=[],
        financial_trails=[FinancialTrail(account="Acct \u2022\u2022\u20225561", flagged=True)],
    ),
}
