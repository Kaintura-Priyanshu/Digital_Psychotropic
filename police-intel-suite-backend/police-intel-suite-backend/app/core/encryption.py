"""
Evidence integrity utilities:

  - `hash_evidence`   SHA-256 digest of any evidence payload, used to prove
                       a dossier / record hasn't been tampered with post-export
                       (chain-of-custody, court admissibility).
  - `EvidenceCipher`  AES-256 (via Fernet, which is AES-128-CBC + HMAC by
                       default in `cryptography`'s simple API — for a strict
                       AES-256-GCM requirement, swap in `AESGCM` from
                       `cryptography.hazmat.primitives.ciphers.aead`, wired
                       the same way) for encrypting evidence at rest.
"""
from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet

from app.core.config import get_settings


def hash_evidence(payload: bytes) -> str:
    """Return a hex SHA-256 digest, for chain-of-custody logs and dossier headers."""
    return hashlib.sha256(payload).hexdigest()


def _resolve_key() -> bytes:
    settings = get_settings()
    if settings.EVIDENCE_ENCRYPTION_KEY:
        return settings.EVIDENCE_ENCRYPTION_KEY.encode()
    # Dev-mode fallback: generate an ephemeral key so the app still boots.
    # Every restart invalidates previously "encrypted" demo records —
    # set EVIDENCE_ENCRYPTION_KEY in .env for anything persistent.
    return base64.urlsafe_b64encode(os.urandom(32))


class EvidenceCipher:
    def __init__(self) -> None:
        self._fernet = Fernet(_resolve_key())

    def encrypt(self, plaintext: bytes) -> bytes:
        return self._fernet.encrypt(plaintext)

    def decrypt(self, token: bytes) -> bytes:
        return self._fernet.decrypt(token)


evidence_cipher = EvidenceCipher()
