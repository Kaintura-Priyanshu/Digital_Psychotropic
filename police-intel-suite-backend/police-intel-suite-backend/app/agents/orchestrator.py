"""
Master Controller Agent — routes a request to the right specialist agent
based on intent. The API routers mostly call specialist agents directly
(explicit endpoints beat implicit routing for an operational tool), but this
orchestrator is what a conversational/CLI entry point, or a future single
`/api/agents/dispatch` endpoint, would sit on top of.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.agents.dossier_agent import DossierAgent
from app.agents.graph_agent import GraphQueryAgent
from app.agents.ingestion_agent import IngestionAgent
from app.agents.resolution_agent import ResolutionAgent


class Intent(str, Enum):
    INGEST_DOCUMENT = "ingest_document"
    RESOLVE_IDENTITY = "resolve_identity"
    QUERY_GRAPH = "query_graph"
    EXPORT_DOSSIER = "export_dossier"
    UNKNOWN = "unknown"


_INTENT_KEYWORDS = {
    Intent.INGEST_DOCUMENT: ("fir", "upload", "scan", "ocr", "cdr", "csv"),
    Intent.RESOLVE_IDENTITY: ("merge", "duplicate", "same person", "resolve", "match"),
    Intent.EXPORT_DOSSIER: ("dossier", "export", "pdf", "report"),
    Intent.QUERY_GRAPH: ("show", "who", "contacts", "network", "syndicate", "kingpin", "hawala"),
}


@dataclass
class MasterControllerAgent:
    ingestion_agent: IngestionAgent
    resolution_agent: ResolutionAgent
    graph_agent: GraphQueryAgent
    dossier_agent: DossierAgent

    @classmethod
    def default(cls) -> "MasterControllerAgent":
        return cls(
            ingestion_agent=IngestionAgent(),
            resolution_agent=ResolutionAgent(),
            graph_agent=GraphQueryAgent(),
            dossier_agent=DossierAgent(),
        )

    def classify_intent(self, text: str) -> Intent:
        lowered = text.lower()
        for intent, keywords in _INTENT_KEYWORDS.items():
            if any(kw in lowered for kw in keywords):
                return intent
        return Intent.UNKNOWN

    def route(self, text: str):
        """Dispatch free-text to the right agent. Non-graph-query intents
        need structured input (a file, a UIP id) that free text alone can't
        supply — callers should hit the dedicated REST endpoint for those;
        this mainly exists to answer "which agent handles X" and to serve
        conversational graph queries end-to-end."""
        intent = self.classify_intent(text)
        if intent == Intent.QUERY_GRAPH:
            return intent, self.graph_agent.answer(text)
        return intent, None
