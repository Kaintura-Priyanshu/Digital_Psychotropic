"""
Agent 2 — Entity Resolution & Disambiguation Agent (NED).

Given a newly extracted name (and, optionally, a face embedding), decides
whether it should MERGE into an existing Unified Intelligence Profile or
CREATE a new one — then applies that decision to the graph store.
"""
from __future__ import annotations

from typing import Optional

from app.graph.store import GraphStore, get_graph_store
from app.models.schemas import GraphNode, NodeType, ThreatTier
from app.nlp.disambiguation import resolve_identity


class ResolutionAgent:
    name = "resolution_agent"

    def __init__(self, store: Optional[GraphStore] = None) -> None:
        self._store = store or get_graph_store()

    def resolve_and_upsert(
        self,
        candidate_id: str,
        candidate_name: str,
        face_similarity: Optional[float] = None,
    ) -> dict:
        nodes, _ = self._store.get_graph()
        best_match = None
        best_decision = None

        for node in nodes:
            if node.type != NodeType.SUSPECT:
                continue
            decision = resolve_identity(candidate_name, node.label, face_similarity)
            if best_decision is None or decision.confidence > best_decision.confidence:
                best_match, best_decision = node, decision

        if best_decision is not None and best_decision.action == "MERGE":
            return {
                "action": "MERGE",
                "matched_uip_id": best_match.id,
                "confidence": best_decision.confidence,
                "signals": [s.__dict__ for s in best_decision.signals],
            }

        new_node = GraphNode(
            id=candidate_id,
            label=candidate_name,
            tier=ThreatTier.INACTIVE,  # newly created profiles start unranked
            type=NodeType.SUSPECT,
            centrality=0.0,
        )
        self._store.upsert_node(new_node)
        return {
            "action": "CREATE",
            "new_uip_id": candidate_id,
            "confidence": best_decision.confidence if best_decision else 0.0,
        }
