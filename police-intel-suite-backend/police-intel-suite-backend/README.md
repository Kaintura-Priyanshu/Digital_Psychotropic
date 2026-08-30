# MHA Police Intelligence Suite — Backend

FastAPI backend for the Command Center Workbench (SIH-26189): FIR ingestion,
NLP/biometric entity extraction, cross-modal entity resolution, a Neo4j
knowledge graph, and the four agents described in the brief. Pairs with the
`police-intel-suite-frontend` Next.js dashboard.

## Quick start (dev/demo mode — no external services required)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000/docs for interactive Swagger UI.

**This has been run and verified end-to-end** — install, boot, auth, and
every route below were exercised against a live server during development.

Demo login: `insp.sharma` / `changeme123` (investigator role), or
`admin` / `changeme123` (admin role).

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token \
  -d "username=insp.sharma&password=changeme123"
```

## Why it boots with zero infra

Every heavyweight or infra-backed dependency degrades gracefully instead of
crashing the app:

| Component | Real backend | Dev/demo fallback |
|---|---|---|
| Graph store | Neo4j (set `NEO4J_URI`) | In-memory NetworkX, seeded from `data/seed.py` |
| Vector search | Qdrant server (set `QDRANT_URL`) | Embedded in-memory Qdrant |
| CDR streaming | Kafka (set `KAFKA_BOOTSTRAP_SERVERS`) | Logs each record instead of publishing |
| NER (Indic-BERT) | `transformers` model | Regex/gazetteer rules (IPC/BNS sections, phone numbers, weapons) |
| OCR | Tesseract + EasyOCR | Returns a clear 503 if neither is installed |
| Face embeddings | ArcFace (`insightface`) | Deterministic pseudo-embedding (not biometrically meaningful — dev only) |

Install `requirements.txt` (the full stack) instead of `requirements-dev.txt`,
and set the corresponding env vars from `.env.example`, to switch each of
these to the real thing. Nothing else in the app needs to change — swap the
backing service and the same endpoints start returning real results.

## Endpoints (verified working)

| Method | Path | Notes |
|---|---|---|
| POST | `/api/auth/token` | OAuth2 password flow, returns a JWT |
| GET | `/api/graph` | Full graph — feeds the frontend's Cytoscape canvas |
| GET | `/api/graph/node/{id}/neighborhood?hops=N` | Multi-hop expansion (double-click on a node) |
| POST | `/api/graph/gds/louvain` | Community detection → likely syndicates |
| POST | `/api/graph/gds/pagerank` | Influence ranking → likely kingpins |
| POST | `/api/graph/gds/betweenness` | Bridge nodes → likely hawala brokers |
| GET | `/api/gis/towers` | CDR tower points — feeds the Leaflet map |
| GET | `/api/dossier/{uip_id}` | UIP profile — feeds the slide-out drawer |
| POST | `/api/dossier/{uip_id}/export` | Renders PDF, returns SHA-256 + filename |
| GET | `/api/dossier/{uip_id}/export/download` | Streams the actual PDF bytes |
| GET | `/api/search?q=...` | Text-to-Cypher search (Graph Query Agent) |
| POST | `/api/search/face` | Photo upload → ArcFace embed → Qdrant similarity |
| POST | `/api/ingestion/document` | FIR photo/scan → OpenCV → dual OCR → entities |
| POST | `/api/ingestion/cdr` | Carrier CSV (Airtel/Jio/Vi) → normalized → Kafka |

All routes except `/health` and `/api/auth/token` require a bearer token;
most require `investigator` role or higher (see `app/core/security.py`).

Try the search agent's Hinglish-aware routing:

```bash
curl -G http://127.0.0.1:8000/api/search \
  --data-urlencode "q=Show Malhotra's hawala contacts" \
  -H "Authorization: Bearer $TOKEN"
```

## Structure

```
app/
  main.py              FastAPI app, router wiring, CORS, startup logging
  core/                config, JWT auth + RBAC, AES/SHA-256 evidence utils, Kafka wrapper
  api/                 route handlers — one file per resource
  ingestion/           OpenCV preprocessing, dual OCR, CDR normalizer     (Phase 1)
  nlp/                 Indic-BERT entity extraction, phonetic/semantic disambiguation (Phase 2/3)
  biometrics/          ArcFace embeddings, Qdrant vector store            (Phase 2/3)
  graph/               Neo4j/NetworkX store, GDS jobs, text-to-Cypher     (Phase 4)
  agents/               the four specialist agents + Master Controller router
  models/schemas.py    shared Pydantic domain models
data/seed.py            mock graph/towers/profiles — mirrors the frontend's mockData.ts
```

## Full stack via Docker Compose

```bash
docker compose up --build
```

Brings up the backend plus Neo4j (with the Graph Data Science plugin),
Qdrant, and Kafka+Zookeeper. Set `NEO4J_PASSWORD` etc. for anything beyond
local testing — the compose file's defaults are for local dev only.

## Known gaps / next steps

- The in-memory `InMemoryGraphStore.run_cypher` raises `NotImplementedError`
  by design — raw Cypher needs a real Neo4j connection; the Graph Query
  Agent falls back to a substring match in dev mode, which is why the
  `search` response above returns a real hit even without Neo4j running.
- `ResolutionAgent` compares a candidate name against every existing suspect
  node in the graph — fine for the demo graph, but swap in a proper
  candidate-generation step (e.g. a Qdrant/Elasticsearch pre-filter) before
  pointing this at a graph with thousands of nodes.
- Demo users live in `app/core/security.py`'s `DEMO_USERS` dict — replace
  with a real user store before any non-local deployment.
