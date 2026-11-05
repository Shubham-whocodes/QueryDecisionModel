from __future__ import annotations

from app.agents.base import BaseAgent


class QueryDecomposerAgent(BaseAgent):
    name = "query_decomposer"

    def run(self, question: str, enhanced: dict) -> dict:
        lowered = enhanced["lowered_question"]

        metrics = []
        if "revenue" in lowered:
            metrics.append("revenue")
        if "late delivery" in lowered or "late-delivery" in lowered:
            metrics.append("late_delivery_rate")
        if "top customer" in lowered or "largest customer" in lowered:
            metrics.append("top_customer")

        filters = {}
        for token in ["1995", "1994", "1993"]:
            if token in lowered:
                filters["year"] = int(token)

        if "region" in lowered:
            filters["region"] = True

        return {
            "metrics": metrics,
            "filters": filters,
            "group_by": "region" if "region" in lowered else "nation" if "nation" in lowered else None,
            "sort_order": "DESC" if any(word in lowered for word in ["top", "largest", "highest"]) else "ASC",
        }
