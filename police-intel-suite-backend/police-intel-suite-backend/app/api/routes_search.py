from fastapi import APIRouter, Depends, File, UploadFile

from app.agents.graph_agent import GraphQueryAgent
from app.biometrics.face_embedding import embed_face
from app.biometrics.vector_store import get_face_vector_store
from app.core.config import get_settings
from app.core.security import Role, require_role
from app.models.schemas import SearchHit, SearchResponse

router = APIRouter(prefix="/search", tags=["search"])
_graph_agent = GraphQueryAgent()


@router.get("", response_model=SearchResponse)
async def search_text(q: str, _=Depends(require_role(Role.VIEWER))):
    """Powers the universal search bar's text/voice-transcript path.

    Runs the request through the Graph Query Agent's Text-to-Cypher
    translation and returns matches plus the Cypher used, for transparency.
    """
    return _graph_agent.answer(q)


@router.post("/face", response_model=SearchResponse)
async def search_face(file: UploadFile = File(...), _=Depends(require_role(Role.VIEWER))):
    """Powers the universal search bar's photo-upload path — ArcFace embed
    + Qdrant cosine similarity, filtered at FACE_MATCH_THRESHOLD."""
    settings = get_settings()
    image_bytes = await file.read()
    vector = embed_face(image_bytes)

    store = get_face_vector_store()
    matches = store.search(vector, top_k=5, score_threshold=settings.FACE_MATCH_THRESHOLD)

    hits = [SearchHit(uip_id=m["uip_id"], name=m["uip_id"], score=m["score"], matched_on="face_vector") for m in matches]
    return SearchResponse(query_echo=f"[photo: {file.filename}]", hits=hits, cypher=None)
