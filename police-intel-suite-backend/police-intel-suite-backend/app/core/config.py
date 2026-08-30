"""
Central configuration. All infra endpoints default to values that let the
API boot in "dev/demo mode" with zero external services running:

  - NEO4J_URI unset / unreachable  -> app.graph.store falls back to an
    in-memory NetworkX graph seeded from data/seed.py
  - QDRANT_URL unset               -> qdrant-client runs embedded/in-memory
  - KAFKA_BOOTSTRAP_SERVERS unset  -> CDR producer logs instead of publishing

Set the real values in a .env file (see .env.example) for production.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- General ---
    APP_NAME: str = "MHA Police Intelligence Suite API"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # --- Auth ---
    SECRET_KEY: str = "dev-only-change-me-before-any-real-deployment"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Encryption (AES-256, evidence-at-rest) ---
    EVIDENCE_ENCRYPTION_KEY: str = ""  # 32-byte urlsafe-base64 Fernet key; generated at
                                        # startup if left blank (dev mode only)

    # --- Neo4j ---
    NEO4J_URI: str = ""
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""

    # --- Qdrant ---
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    FACE_MATCH_THRESHOLD: float = 0.85

    # --- Kafka ---
    KAFKA_BOOTSTRAP_SERVERS: str = ""
    KAFKA_RAW_CRIMES_TOPIC: str = "raw-crimes-stream"

    # --- LLM (agents / text-to-cypher) ---
    ANTHROPIC_API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
