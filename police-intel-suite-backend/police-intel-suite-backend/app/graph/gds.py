"""
Phase 4 Graph Data Science jobs. When the app is backed by real Neo4j, these
should be swapped for `CALL gds.louvain.stream(...)` etc. via
`store.run_cypher(...)` for graphs too large to pull into memory. The
NetworkX versions here are used automatically against the in-memory fallback
store, and are perfectly fine for exploratory runs against graphs that do
fit in memory (tens of thousands of nodes).
"""
from __future__ import annotations

import networkx as nx

from app.graph.store import GraphStore, InMemoryGraphStore
from app.models.schemas import GdsRunResult


def _as_undirected_weighted(store: GraphStore) -> nx.Graph:
    if isinstance(store, InMemoryGraphStore):
        return store.nx_graph.to_undirected()
    nodes, edges = store.get_graph()
    g = nx.Graph()
    g.add_nodes_from(n.id for n in nodes)
    g.add_weighted_edges_from((e.source, e.target, e.weight) for e in edges)
    return g


def run_louvain(store: GraphStore) -> GdsRunResult:
    """Community detection — surfaces likely syndicates / cells."""
    g = _as_undirected_weighted(store)
    try:
        from networkx.algorithms.community import louvain_communities

        communities = louvain_communities(g, weight="weight", seed=42)
    except Exception:
        # networkx < 3.0 fallback: greedy modularity communities
        from networkx.algorithms.community import greedy_modularity_communities

        communities = greedy_modularity_communities(g, weight="weight")

    result = {f"syndicate_{i}": sorted(list(c)) for i, c in enumerate(communities)}
    return GdsRunResult(algorithm="louvain", communities=result)


def run_pagerank(store: GraphStore) -> GdsRunResult:
    """Identifies likely kingpins — highest-influence nodes in the network."""
    if isinstance(store, InMemoryGraphStore):
        g = store.nx_graph
    else:
        nodes, edges = store.get_graph()
        g = nx.DiGraph()
        g.add_nodes_from(n.id for n in nodes)
        g.add_weighted_edges_from((e.source, e.target, e.weight) for e in edges)

    scores = nx.pagerank(g, weight="weight")
    ranked = dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))
    return GdsRunResult(algorithm="pagerank", scores=ranked)


def run_betweenness_centrality(store: GraphStore) -> GdsRunResult:
    """Identifies likely hawala brokers — nodes that bridge otherwise
    disconnected clusters (high betweenness = a chokepoint for flows)."""
    g = _as_undirected_weighted(store)
    scores = nx.betweenness_centrality(g, weight="weight", normalized=True)
    ranked = dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))
    return GdsRunResult(algorithm="betweenness_centrality", scores=ranked)
