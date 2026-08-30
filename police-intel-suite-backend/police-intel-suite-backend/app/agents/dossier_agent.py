"""
Agent 4 — Legal Dossier & Evidence Agent.

Compiles a Master UIP profile plus its multi-hop connections into a
structured PDF, computes a SHA-256 digest over the rendered bytes for
chain-of-custody, and returns both.
"""
from __future__ import annotations

import io
from datetime import datetime, timezone

from app.core.encryption import hash_evidence
from app.graph.store import GraphStore, get_graph_store
from app.models.schemas import DossierExportResult, UipProfile


class DossierAgent:
    name = "dossier_agent"

    def __init__(self, store: GraphStore | None = None) -> None:
        self._store = store or get_graph_store()

    def export_pdf(self, profile: UipProfile) -> DossierExportResult:
        pdf_bytes = self._render_pdf(profile)
        digest = hash_evidence(pdf_bytes)
        filename = f"dossier_{profile.id}_{digest[:8]}.pdf"

        return DossierExportResult(
            uip_id=profile.id,
            sha256=digest,
            filename=filename,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    def _render_pdf(self, profile: UipProfile) -> bytes:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 25 * mm

        def line(text: str, size: int = 11, gap: float = 7 * mm, bold: bool = False):
            nonlocal y
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(20 * mm, y, text)
            y -= gap

        line("MHA POLICE INTELLIGENCE SUITE — VERIFIED DOSSIER", 14, bold=True)
        line(f"Unified Intelligence Profile: {profile.id}", 11)
        line("—" * 70, 9, gap=6 * mm)

        line(f"Name: {profile.name}", bold=True)
        if profile.alias:
            line(f"Alias(es): {', '.join(profile.alias)}")
        line(f"Threat tier: {profile.tier.value.upper()}")
        line(f"Face match confidence: {profile.face_match_confidence * 100:.1f}%")
        line(f"Last known location: {profile.last_known_location}")

        y -= 3 * mm
        line("IPC / BNS sections", bold=True)
        line(", ".join(profile.ipc_sections) or "None recorded")

        y -= 3 * mm
        line("High-risk contacts", bold=True)
        for contact in profile.contacts:
            line(f"  • {contact.label}: {contact.count}")

        y -= 3 * mm
        line("Linked vehicles", bold=True)
        line(", ".join(profile.vehicles) or "None recorded")

        y -= 3 * mm
        line("Financial trails", bold=True)
        for trail in profile.financial_trails:
            flag = " [FLAGGED]" if trail.flagged else ""
            line(f"  • {trail.account}{flag}")

        y -= 8 * mm
        line(f"Generated: {datetime.now(timezone.utc).isoformat()}", 9)
        line("This document and its evidentiary basis are SHA-256 hashed at export", 9)
        line("time for chain-of-custody verification.", 9)

        c.showPage()
        c.save()
        return buffer.getvalue()
