import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_auth,
    routes_dossier,
    routes_gis,
    routes_graph,
    routes_ingestion,
    routes_search,
)
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("mha_intel_api")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "Backend for the MHA Police Intelligence Suite (SIH-26189) — multilingual FIR "
        "ingestion, biometric + NLP entity extraction, cross-modal entity resolution, "
        "a Neo4j knowledge graph, and the Text-to-Cypher / dossier-export agents that "
        "power the tactical workbench frontend."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_graph.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_gis.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_dossier.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_search.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_ingestion.router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.on_event("startup")
async def on_startup():
    logger.info("%s starting in '%s' mode", settings.APP_NAME, settings.ENVIRONMENT)
    if not settings.NEO4J_URI:
        logger.info("NEO4J_URI not set — using in-memory graph store (dev/demo mode)")
    if not settings.QDRANT_URL:
        logger.info("QDRANT_URL not set — using embedded in-memory Qdrant (dev/demo mode)")
    if not settings.KAFKA_BOOTSTRAP_SERVERS:
        logger.info("KAFKA_BOOTSTRAP_SERVERS not set — CDR stream will log instead of publish")
