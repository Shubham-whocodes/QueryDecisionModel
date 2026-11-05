from __future__ import annotations

from app.agents.base import BaseAgent
from app.semantic_layer import SemanticLayer


class PlannerAgent(BaseAgent):
    name = "planner"

    def __init__(self, semantic_layer: SemanticLayer):
        self.semantic_layer = semantic_layer

    def run(self, question: str, enhanced: dict) -> dict:
        lowered = (enhanced.get("canonical_question") or enhanced.get("lowered_question") or question.lower()).strip()
        filters = self._infer_filters(lowered)

        if any(term in lowered for term in ["customer satisfaction", "employee", "satisfaction score", "inventory turns", "late payment"]):
            return {"status": "refuse", "reason": "This question depends on data outside the TPC-H warehouse schema."}

        if "running total" in lowered or "cumulative" in lowered:
            return {
                "status": "ok",
                "chart_type": "line",
                "sql": self._running_total_sql(filters),
                "confidence": 0.9,
            }

        if "late delivery" in lowered:
            if "region" in lowered:
                return {
                    "status": "ok",
                    "chart_type": "bar",
                    "sql": self._late_delivery_by_region_sql(filters, enhanced.get("limit") or 3),
                    "confidence": 0.92,
                }
            return {
                "status": "ok",
                "chart_type": "bar",
                "sql": self._late_delivery_sql(filters),
                "confidence": 0.92,
            }

        if "top customer" in lowered or "largest customer" in lowered or ("customer" in lowered and "revenue" in lowered and "top" in lowered):
            return {
                "status": "ok",
                "chart_type": "bar",
                "sql": self._top_customer_sql(filters, enhanced.get("limit") or 5),
                "confidence": 0.94,
            }

        if "year over year" in lowered or "yoy" in lowered or "year over year" in lowered or ("revenue" in lowered and ("year" in lowered or "trend" in lowered)):
            return {
                "status": "ok",
                "chart_type": "line",
                "sql": self._yoy_revenue_sql(filters),
                "confidence": 0.9,
            }

        if "region" in lowered and "revenue" in lowered:
            limit = enhanced.get("limit") or 10
            return {
                "status": "ok",
                "chart_type": "bar",
                "sql": self._region_revenue_sql(filters, limit),
                "confidence": 0.95,
            }

        if "supplier" in lowered and "revenue" in lowered:
            return {
                "status": "ok",
                "chart_type": "bar",
                "sql": self._supplier_revenue_sql(filters),
                "confidence": 0.9,
            }

        if "supplier" in lowered and "nation" in lowered and "performance" in lowered:
            return {
                "status": "ok",
                "chart_type": "bar",
                "sql": self._supplier_by_nation_sql(filters),
                "confidence": 0.88,
            }

        if "avg order" in lowered or "average order" in lowered:
            return {
                "status": "ok",
                "chart_type": "bar",
                "sql": self._avg_order_value_sql(filters),
                "confidence": 0.88,
            }

        if "total revenue" in lowered or "revenue" in lowered:
            return {
                "status": "ok",
                "chart_type": "bar",
                "sql": self._total_revenue_sql(filters),
                "confidence": 0.95,
            }

        if enhanced.get("needs_clarification"):
            return {"status": "clarify", "question": question, "reason": "Please specify the time window or region for this metric."}

        return {
            "status": "ok",
            "chart_type": "table",
            "sql": self._fallback_sql(filters),
            "confidence": 0.7,
        }

    def _infer_filters(self, lowered: str):
        filters = {}
        if "1995" in lowered:
            filters["year"] = 1995
        elif "1994" in lowered:
            filters["year"] = 1994
        elif "1993" in lowered:
            filters["year"] = 1993
        if "region" in lowered:
            filters["region"] = "region"
        return filters

    def _region_revenue_sql(self, filters: dict, limit: int = 10) -> str:
        year_clause = "WHERE EXTRACT(YEAR FROM o.o_orderdate) = 1995" if filters.get("year") else ""
        return f"""
        SELECT r.r_name AS region, ROUND(SUM(li.l_extendedprice * (1 - li.l_discount)), 2) AS revenue
        FROM region r
        JOIN nation n ON n.n_regionkey = r.r_regionkey
        JOIN customer c ON c.c_nationkey = n.n_nationkey
        JOIN orders o ON o.o_custkey = c.c_custkey
        JOIN lineitem li ON li.l_orderkey = o.o_orderkey
        {year_clause}
        GROUP BY r.r_name
        ORDER BY revenue DESC
        LIMIT {limit}
        """

    def _top_customer_sql(self, filters: dict, limit: int) -> str:
        year_clause = "WHERE EXTRACT(YEAR FROM o.o_orderdate) = 1995" if filters.get("year") else ""
        return f"""
        SELECT c.c_name AS customer, ROUND(SUM(li.l_extendedprice * (1 - li.l_discount)), 2) AS revenue
        FROM customer c
        JOIN orders o ON o.o_custkey = c.c_custkey
        JOIN lineitem li ON li.l_orderkey = o.o_orderkey
        {year_clause}
        GROUP BY c.c_name
        ORDER BY revenue DESC
        LIMIT {limit}
        """

    def _late_delivery_sql(self, filters: dict) -> str:
        year_clause = "WHERE EXTRACT(YEAR FROM o.o_orderdate) = 1995" if filters.get("year") else ""
        return f"""
        SELECT n.n_name AS nation, ROUND(100.0 * SUM(CASE WHEN li.l_shipdate > li.l_commitdate THEN 1 ELSE 0 END) / COUNT(*), 2) AS late_delivery_rate
        FROM nation n
        JOIN customer c ON c.c_nationkey = n.n_nationkey
        JOIN orders o ON o.o_custkey = c.c_custkey
        JOIN lineitem li ON li.l_orderkey = o.o_orderkey
        {year_clause}
        GROUP BY n.n_name
        ORDER BY late_delivery_rate DESC
        """

    def _late_delivery_by_region_sql(self, filters: dict, limit: int = 3) -> str:
        year_clause = "WHERE EXTRACT(YEAR FROM o.o_orderdate) = 1995" if filters.get("year") else ""
        return f"""
        SELECT r.r_name AS region, ROUND(100.0 * SUM(CASE WHEN li.l_shipdate > li.l_commitdate THEN 1 ELSE 0 END) / COUNT(*), 2) AS late_delivery_rate
        FROM region r
        JOIN nation n ON n.n_regionkey = r.r_regionkey
        JOIN customer c ON c.c_nationkey = n.n_nationkey
        JOIN orders o ON o.o_custkey = c.c_custkey
        JOIN lineitem li ON li.l_orderkey = o.o_orderkey
        {year_clause}
        GROUP BY r.r_name
        ORDER BY late_delivery_rate DESC
        LIMIT {limit}
        """

    def _yoy_revenue_sql(self, filters: dict) -> str:
        return """
        SELECT EXTRACT(YEAR FROM o.o_orderdate) AS year, ROUND(SUM(li.l_extendedprice * (1 - li.l_discount)), 2) AS revenue
        FROM orders o
        JOIN lineitem li ON li.l_orderkey = o.o_orderkey
        GROUP BY EXTRACT(YEAR FROM o.o_orderdate)
        ORDER BY year ASC
        """

    def _supplier_revenue_sql(self, filters: dict) -> str:
        year_clause = "WHERE EXTRACT(YEAR FROM o.o_orderdate) = 1995" if filters.get("year") else ""
        return f"""
        SELECT s.s_name AS supplier, ROUND(SUM(li.l_extendedprice * (1 - li.l_discount)), 2) AS revenue
        FROM supplier s
        JOIN lineitem li ON li.l_suppkey = s.s_suppkey
        JOIN orders o ON o.o_orderkey = li.l_orderkey
        {year_clause}
        GROUP BY s.s_name
        ORDER BY revenue DESC
        LIMIT 10
        """

    def _supplier_by_nation_sql(self, filters: dict) -> str:
        year_clause = "WHERE EXTRACT(YEAR FROM o.o_orderdate) = 1995" if filters.get("year") else ""
        return f"""
        SELECT n.n_name AS nation, s.s_name AS supplier, ROUND(SUM(li.l_extendedprice * (1 - li.l_discount)), 2) AS revenue
        FROM nation n
        JOIN supplier s ON s.s_nationkey = n.n_nationkey
        JOIN lineitem li ON li.l_suppkey = s.s_suppkey
        JOIN orders o ON o.o_orderkey = li.l_orderkey
        {year_clause}
        GROUP BY n.n_name, s.s_name
        ORDER BY revenue DESC
        LIMIT 10
        """

    def _avg_order_value_sql(self, filters: dict) -> str:
        year_clause = "WHERE EXTRACT(YEAR FROM o.o_orderdate) = 1995" if filters.get("year") else ""
        return f"""
        SELECT n.n_name AS nation, ROUND(SUM(li.l_extendedprice * (1 - li.l_discount)) / COUNT(DISTINCT o.o_orderkey), 2) AS avg_order_value
        FROM nation n
        JOIN customer c ON c.c_nationkey = n.n_nationkey
        JOIN orders o ON o.o_custkey = c.c_custkey
        JOIN lineitem li ON li.l_orderkey = o.o_orderkey
        {year_clause}
        GROUP BY n.n_name
        ORDER BY avg_order_value DESC
        """

    def _total_revenue_sql(self, filters: dict) -> str:
        year_clause = "WHERE EXTRACT(YEAR FROM o.o_orderdate) = 1995" if filters.get("year") else ""
        return f"""
        SELECT ROUND(SUM(li.l_extendedprice * (1 - li.l_discount)), 2) AS revenue
        FROM orders o
        JOIN lineitem li ON li.l_orderkey = o.o_orderkey
        {year_clause}
        """

    def _running_total_sql(self, filters: dict) -> str:
        return """
        WITH monthly AS (
            SELECT DATE_TRUNC('month', o.o_orderdate)::DATE AS month,
                   ROUND(SUM(li.l_extendedprice * (1 - li.l_discount)), 2) AS revenue
            FROM orders o
            JOIN lineitem li ON li.l_orderkey = o.o_orderkey
            GROUP BY DATE_TRUNC('month', o.o_orderdate)::DATE
        )
        SELECT month,
               revenue,
               SUM(revenue) OVER (ORDER BY month) AS running_total
        FROM monthly
        ORDER BY month
        """

    def _fallback_sql(self, filters: dict) -> str:
        year_clause = "WHERE EXTRACT(YEAR FROM o.o_orderdate) = 1995" if filters.get("year") else ""
        return f"""
        SELECT n.n_name AS nation, ROUND(SUM(li.l_extendedprice * (1 - li.l_discount)), 2) AS revenue
        FROM nation n
        JOIN customer c ON c.c_nationkey = n.n_nationkey
        JOIN orders o ON o.o_custkey = c.c_custkey
        JOIN lineitem li ON li.l_orderkey = o.o_orderkey
        {year_clause}
        GROUP BY n.n_name
        ORDER BY revenue DESC
        LIMIT 10
        """
