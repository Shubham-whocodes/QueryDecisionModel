from __future__ import annotations

import re

from app.agents.base import BaseAgent


class QueryEnhancerAgent(BaseAgent):
    name = "query_enhancer"

    def run(self, question: str) -> dict:
        q = (question or "").strip()
        lowered = q.lower()
        canonical = lowered.replace("-", " ")

        top_match = re.search(r"(top|largest|highest|most)\s+(\d+)", canonical)
        limit = int(top_match.group(2)) if top_match else None

        business_terms = {
            "revenue": "revenue" in canonical,
            "region": "region" in canonical,
            "customer": "customer" in canonical,
            "nation": "nation" in canonical,
            "supplier": "supplier" in canonical,
            "year": any(token in canonical for token in ["year", "yoy", "year over year", "annual"]),
            "late_delivery": "late delivery" in canonical,
            "ranking": any(token in canonical for token in ["top", "largest", "highest", "most"]),
            "trend": any(token in canonical for token in ["growth", "trend", "increase", "decrease", "year over year", "yoy"]),
            "running_total": "running total" in canonical or "cumulative" in canonical,
        }

        return {
            "normalized_question": q,
            "lowered_question": lowered,
            "canonical_question": canonical,
            "limit": limit,
            "business_terms": business_terms,
            "needs_clarification": self._looks_ambiguous(canonical),
        }

    def _looks_ambiguous(self, lowered: str) -> bool:
        ambiguous_markers = [
            "top customer",
            "best customer",
            "popular",
            "performance",
            "late",
            "sales",
            "success",
        ]
        return any(marker in lowered for marker in ambiguous_markers) and "by region" not in lowered and "by nation" not in lowered
