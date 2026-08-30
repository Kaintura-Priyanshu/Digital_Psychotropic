"""
Agent 3 — Graph Query & Analytics Agent.

Serves the investigator-facing natural language search: translates a
free-text (or Hinglish) question into Cypher, executes it against whichever
graph store is active, and triggers background GDS runs (Louvain/PageRank)
when the question implies a network-level analysis rather than a point
lookup.
"""
from __future__ import annotations

from app.graph import gds
from app.graph.store import GraphStore, get_graph_store
from app.graph.text_to_cypher import translate
from app.models.schemas import SearchHit, SearchResponse


_NETWORK_LEVEL_KEYWORDS = ("syndicate", "kingpin", "broker", "cluster", "network")


class GraphQueryAgent:
    name = "graph_query_agent"

    def __init__(self, store: GraphStore | None = None) -> None:
        self._store = store or get_graph_store()

    def answer(self, text: str) -> SearchResponse:
        translation = translate(text)

        hits: list[SearchHit] = []
        try:
            rows = self._store.run_cypher(translation.cypher, translation.params)
            hits = self._rows_to_hits(rows)
        except NotImplementedError:
            # In-memory fallback store — approximate the same query via
            # substring match over node labels instead of raw Cypher.
            nodes, _ = self._store.get_graph()
            needle = (translation.params.get("name") or translation.params.get("text") or text).lower()
            hits = [
                SearchHit(uip_id=n.id, name=n.label, score=1.0, matched_on="label")
                for n in nodes
                if needle and needle.lower() in n.label.lower()
            ]

        if any(kw in text.lower() for kw in _NETWORK_LEVEL_KEYWORDS):
            self._maybe_trigger_gds(text.lower())

        return SearchResponse(query_echo=text, hits=hits, cypher=translation.cypher)

    def _maybe_trigger_gds(self, lowered: str) -> None:
        if "kingpin" in lowered:
            gds.run_pagerank(self._store)
        if "syndicate" in lowered or "cluster" in lowered:
            gds.run_louvain(self._store)
        if "broker" in lowered:
            gds.run_betweenness_centrality(self._store)

    @staticmethod
    def _rows_to_hits(rows: list[dict]) -> list[SearchHit]:
        hits = []
        for row in rows:
            for value in row.values():
                if isinstance(value, dict) and "id" in value:
                    hits.append(SearchHit(uip_id=value["id"], name=value.get("label", value["id"]), score=1.0, matched_on="cypher"))
        return hits
