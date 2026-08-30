"""
Graph persistence layer for Phase 4 (Neo4j Knowledge Graph Engine).

`GraphStore` is the interface the rest of the app talks to. Two
implementations:

  - Neo4jGraphStore     real Cypher driver — used when NEO4J_URI is set
                          and reachable.
  - InMemoryGraphStore   NetworkX-backed fallback, seeded from data/seed.py —
                          used automatically otherwise, so `/api/graph` and
                          friends work with zero infra for local dev.

`get_graph_store()` picks the right one once, at import time.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

import networkx as nx

from app.core.config import get_settings
from app.models.schemas import GraphEdge, GraphNode, NodeType, RelationType, ThreatTier
from data.seed import GRAPH_EDGES, GRAPH_NODES

logger = logging.getLogger("graph_store")


class GraphStore(ABC):
    @abstractmethod
    def get_graph(self) -> tuple[List[GraphNode], List[GraphEdge]]:
        ...

    @abstractmethod
    def get_neighborhood(self, node_id: str, hops: int = 1) -> tuple[List[GraphNode], List[GraphEdge]]:
        ...

    @abstractmethod
    def upsert_node(self, node: GraphNode) -> None:
        ...

    @abstractmethod
    def upsert_edge(self, edge: GraphEdge) -> None:
        ...

    @abstractmethod
    def run_cypher(self, query: str, params: Optional[dict] = None) -> list[dict]:
        """Execute a raw Cypher query (Neo4j) — used by the Graph Query Agent's
        Text-to-Cypher output. The in-memory store raises NotImplementedError;
        callers should catch this and fall back to `get_graph`/`get_neighborhood`."""
        ...


class Neo4jGraphStore(GraphStore):
    def __init__(self, uri: str, user: str, password: str) -> None:
        from neo4j import GraphDatabase  # imported lazily — optional dep

        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._driver.verify_connectivity()
        logger.info("Connected to Neo4j at %s", uri)

    def get_graph(self) -> tuple[List[GraphNode], List[GraphEdge]]:
        with self._driver.session() as session:
            node_rows = session.run(
                "MATCH (n) RETURN n.id AS id, n.label AS label, n.tier AS tier, "
                "labels(n)[0] AS type, coalesce(n.centrality, 0.0) AS centrality"
            ).data()
            edge_rows = session.run(
                "MATCH (a)-[r]->(b) RETURN id(r) AS id, a.id AS source, b.id AS target, "
                "type(r) AS relation, coalesce(r.weight, 0.5) AS weight"
            ).data()
        nodes = [GraphNode(**{**row, "type": NodeType(row["type"].lower())}) for row in node_rows]
        edges = [GraphEdge(**{**row, "id": str(row["id"]), "relation": RelationType(row["relation"])}) for row in edge_rows]
        return nodes, edges

    def get_neighborhood(self, node_id: str, hops: int = 1) -> tuple[List[GraphNode], List[GraphEdge]]:
        with self._driver.session() as session:
            rows = session.run(
                f"MATCH (n {{id: $id}})-[r*1..{hops}]-(m) "
                "RETURN n, r, m",
                id=node_id,
            ).data()
        # Flatten Neo4j path results into node/edge lists (left compact —
        # production version should project this via APOC or GDS).
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []
        for row in rows:
            for rec in (row["n"], row["m"]):
                nodes[rec["id"]] = GraphNode(
                    id=rec["id"], label=rec.get("label", rec["id"]),
                    tier=ThreatTier(rec.get("tier", "inactive")),
                    type=NodeType(rec.get("type", "suspect")),
                    centrality=rec.get("centrality", 0.0),
                )
        return list(nodes.values()), edges

    def upsert_node(self, node: GraphNode) -> None:
        with self._driver.session() as session:
            session.run(
                f"MERGE (n:{node.type.value.capitalize()} {{id: $id}}) "
                "SET n.label = $label, n.tier = $tier, n.centrality = $centrality",
                id=node.id, label=node.label, tier=node.tier.value, centrality=node.centrality,
            )

    def upsert_edge(self, edge: GraphEdge) -> None:
        with self._driver.session() as session:
            session.run(
                f"MATCH (a {{id: $source}}), (b {{id: $target}}) "
                f"MERGE (a)-[r:{edge.relation.value}]->(b) SET r.weight = $weight",
                source=edge.source, target=edge.target, weight=edge.weight,
            )

    def run_cypher(self, query: str, params: Optional[dict] = None) -> list[dict]:
        with self._driver.session() as session:
            return session.run(query, params or {}).data()


class InMemoryGraphStore(GraphStore):
    """NetworkX-backed fallback — same shape as Neo4j, zero infra required."""

    def __init__(self) -> None:
        self._g = nx.MultiDiGraph()
        for n in GRAPH_NODES:
            self._g.add_node(n.id, **n.model_dump())
        for e in GRAPH_EDGES:
            self._g.add_edge(e.source, e.target, key=e.id, **e.model_dump())
        logger.info("Using in-memory NetworkX graph store (seeded, %d nodes)", self._g.number_of_nodes())

    def get_graph(self) -> tuple[List[GraphNode], List[GraphEdge]]:
        nodes = [GraphNode(**data) for _, data in self._g.nodes(data=True)]
        edges = [GraphEdge(**data) for _, _, data in self._g.edges(data=True)]
        return nodes, edges

    def get_neighborhood(self, node_id: str, hops: int = 1) -> tuple[List[GraphNode], List[GraphEdge]]:
        if node_id not in self._g:
            return [], []
        undirected = self._g.to_undirected()
        reachable = nx.single_source_shortest_path_length(undirected, node_id, cutoff=hops)
        node_ids = set(reachable.keys())
        nodes = [GraphNode(**self._g.nodes[nid]) for nid in node_ids]
        edges = [
            GraphEdge(**data)
            for u, v, data in self._g.edges(data=True)
            if u in node_ids and v in node_ids
        ]
        return nodes, edges

    def upsert_node(self, node: GraphNode) -> None:
        self._g.add_node(node.id, **node.model_dump())

    def upsert_edge(self, edge: GraphEdge) -> None:
        self._g.add_edge(edge.source, edge.target, key=edge.id, **edge.model_dump())

    def run_cypher(self, query: str, params: Optional[dict] = None) -> list[dict]:
        raise NotImplementedError("Raw Cypher execution requires a live Neo4j connection")

    # Exposed for app.graph.gds, which runs NetworkX algorithms directly
    # against this graph when Neo4j GDS isn't available.
    @property
    def nx_graph(self) -> nx.MultiDiGraph:
        return self._g


def _build_store() -> GraphStore:
    settings = get_settings()
    if settings.NEO4J_URI:
        try:
            return Neo4jGraphStore(settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        except Exception as exc:  # noqa: BLE001 — degrade gracefully in dev
            logger.warning("Neo4j unavailable (%s); falling back to in-memory graph store", exc)
    return InMemoryGraphStore()


_store: Optional[GraphStore] = None


def get_graph_store() -> GraphStore:
    global _store
    if _store is None:
        _store = _build_store()
    return _store
