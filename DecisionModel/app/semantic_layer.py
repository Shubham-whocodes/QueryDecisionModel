from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    description: str
    sql_expression: str
    unit: str
    time_grain: str = "order_date"


class SemanticLayer:
    """Defines approved business metrics for the warehouse and their meaning."""

    def __init__(self) -> None:
        self.metrics: Dict[str, MetricDefinition] = {
            "revenue": MetricDefinition(
                name="revenue",
                description="Monetary value of shipped or ordered goods after discount.",
                sql_expression="SUM(li.l_extendedprice * (1 - li.l_discount))",
                unit="USD",
                time_grain="date",
            ),
            "order_count": MetricDefinition(
                name="order_count",
                description="Number of unique customer orders.",
                sql_expression="COUNT(DISTINCT o.o_orderkey)",
                unit="count",
                time_grain="date",
            ),
            "avg_order_value": MetricDefinition(
                name="avg_order_value",
                description="Average order value across all orders.",
                sql_expression="SUM(li.l_extendedprice * (1 - li.l_discount)) / COUNT(DISTINCT o.o_orderkey)",
                unit="USD",
                time_grain="date",
            ),
            "late_delivery_rate": MetricDefinition(
                name="late_delivery_rate",
                description="Share of line items shipped after the committed date.",
                sql_expression="100.0 * SUM(CASE WHEN li.l_shipdate > li.l_commitdate THEN 1 ELSE 0 END) / COUNT(*)",
                unit="percent",
                time_grain="date",
            ),
            "top_customer": MetricDefinition(
                name="top_customer",
                description="Customer with the largest cumulative revenue.",
                sql_expression="c.c_name",
                unit="customer",
                time_grain="date",
            ),
            "region_revenue": MetricDefinition(
                name="region_revenue",
                description="Revenue aggregated to the region level.",
                sql_expression="SUM(li.l_extendedprice * (1 - li.l_discount))",
                unit="USD",
                time_grain="region",
            ),
        }

    def defines(self, term: str) -> bool:
        return term.lower() in self.metrics or term.lower().replace(" ", "_") in self.metrics

    def resolve_term(self, term: str) -> MetricDefinition | None:
        normalized = term.lower().replace(" ", "_")
        return self.metrics.get(normalized)

    def detect_business_terms(self, question: str) -> List[str]:
        tokens = question.lower()
        hits = []
        for name in self.metrics:
            if name in tokens or name.replace("_", " ") in tokens:
                hits.append(name)
        if "revenue" in tokens and "revenue" not in hits:
            hits.append("revenue")
        if "late delivery" in tokens or "late-delivery" in tokens:
            hits.append("late_delivery_rate")
        if "top customer" in tokens or "largest customer" in tokens:
            hits.append("top_customer")
        return hits

    def get_definition(self, name: str) -> MetricDefinition:
        term = name.lower().replace(" ", "_")
        return self.metrics[term]
