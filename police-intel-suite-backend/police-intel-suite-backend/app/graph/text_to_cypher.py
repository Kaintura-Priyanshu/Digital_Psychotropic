"""
Converts investigator natural-language queries into Cypher.

Two modes:
  - LLM mode      if ANTHROPIC_API_KEY is set, delegates to a small
                   Claude-backed chain (see app/agents/graph_agent.py) that
                   understands free-form phrasing.
  - Template mode  a small set of regex-matched patterns covering the
                   common investigative asks from the brief ("show X's
                   contacts", "hawala transfers", "syndicate around X").
                   Used automatically with no API key configured, so the
                   search endpoint always returns *something* runnable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class CypherTranslation:
    cypher: str
    params: dict
    explanation: str


_NAME_PATTERN = re.compile(r"([A-Z][a-z]+(?:'s)?)")


def translate(text: str) -> CypherTranslation:
    lowered = text.lower()

    if "hawala" in lowered:
        name_match = re.search(r"\b([A-Za-z]+)'s\b", text)
        name = name_match.group(1) if name_match else None
        if name:
            return CypherTranslation(
                cypher=(
                    "MATCH (s:Suspect {label: $name})-[:HAWALA_TRANSFER*1..3]-(b:Bank) "
                    "RETURN s, b"
                ),
                params={"name": name},
                explanation=f"Hawala transfer chain reachable from {name}, up to 3 hops.",
            )
        return CypherTranslation(
            cypher="MATCH (a)-[r:HAWALA_TRANSFER]->(b) RETURN a, r, b",
            params={},
            explanation="All hawala transfer edges in the graph.",
        )

    if "syndicate" in lowered or "cluster" in lowered or "network around" in lowered:
        name_match = _NAME_PATTERN.search(text)
        name = name_match.group(1).rstrip("'s") if name_match else None
        return CypherTranslation(
            cypher="MATCH (n {label: $name})-[*1..2]-(m) RETURN n, m",
            params={"name": name},
            explanation=f"Two-hop neighborhood around {name or 'the queried entity'} — approximates their syndicate.",
        )

    if "kingpin" in lowered or "mastermind" in lowered:
        return CypherTranslation(
            cypher="MATCH (n) WHERE n.tier = 'kingpin' RETURN n ORDER BY n.centrality DESC",
            params={},
            explanation="All nodes tagged as kingpin tier, ranked by centrality.",
        )

    if "contact" in lowered or "called" in lowered or "call" in lowered:
        name_match = re.search(r"\b([A-Za-z]+)'s\b", text)
        name = name_match.group(1) if name_match else None
        return CypherTranslation(
            cypher="MATCH (s {label: $name})-[:CALLED]-(p:Phone) RETURN s, p",
            params={"name": name},
            explanation=f"Phones called by / calling {name or 'the queried entity'}.",
        )

    # Generic fallback: substring match on label
    return CypherTranslation(
        cypher="MATCH (n) WHERE toLower(n.label) CONTAINS toLower($text) RETURN n LIMIT 25",
        params={"text": text},
        explanation="Free-text substring match against node labels.",
    )
