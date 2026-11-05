from __future__ import annotations

from app.agents.base import BaseAgent


class GovernanceAgent(BaseAgent):
    name = "governance"

    def run(self, question: str) -> dict:
        lowered = question.lower().replace("-", " ")
        unsupported_terms = [
            "customer satisfaction",
            "satisfaction score",
            "employee turnover",
            "inventory turns",
            "salesperson",
            "late payment",
            "returns by product color",
            "product color",
            "returns",
            "sentiment",
            "likely to leave",
            "leave the network",
            "next quarter",
            "forecast",
            "predict",
        ]

        if "last quarter" in lowered:
            return {"status": "clarify", "reason": "Please specify the exact quarter boundary or date window for this comparison."}

        matched = [term for term in unsupported_terms if term in lowered]
        if matched:
            return {
                "status": "refuse",
                "reason": "The dataset does not include the requested dimension; the engine should refuse instead of guessing.",
            }

        if not lowered.strip():
            return {"status": "clarify", "reason": "Please ask a specific business question."}

        return {"status": "ok", "reason": "Question is in-scope for the TPC-H warehouse."}
