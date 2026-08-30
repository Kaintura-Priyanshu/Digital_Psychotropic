from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import Role, require_role
from app.graph import gds
from app.graph.store import get_graph_store
from app.models.schemas import GdsRunResult, GraphResponse

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", response_model=GraphResponse)
async def get_full_graph(_=Depends(require_role(Role.VIEWER))):
    """Powers the frontend's Cytoscape.js canvas (left panel)."""
    store = get_graph_store()
    nodes, edges = store.get_graph()
    return GraphResponse(nodes=nodes, edges=edges)


@router.get("/node/{node_id}/neighborhood", response_model=GraphResponse)
async def get_neighborhood(
    node_id: str,
    hops: int = Query(default=1, ge=1, le=4),
    _=Depends(require_role(Role.VIEWER)),
):
    """Powers double-click multi-hop expansion on a graph node."""
    store = get_graph_store()
    nodes, edges = store.get_neighborhood(node_id, hops=hops)
    if not nodes:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return GraphResponse(nodes=nodes, edges=edges)


@router.post("/gds/louvain", response_model=GdsRunResult)
async def run_louvain(_=Depends(require_role(Role.INVESTIGATOR))):
    """Community detection — likely syndicates/cells."""
    return gds.run_louvain(get_graph_store())


@router.post("/gds/pagerank", response_model=GdsRunResult)
async def run_pagerank(_=Depends(require_role(Role.INVESTIGATOR))):
    """Influence ranking — likely kingpins."""
    return gds.run_pagerank(get_graph_store())


@router.post("/gds/betweenness", response_model=GdsRunResult)
async def run_betweenness(_=Depends(require_role(Role.INVESTIGATOR))):
    """Bridge-node ranking — likely hawala brokers."""
    return gds.run_betweenness_centrality(get_graph_store())
