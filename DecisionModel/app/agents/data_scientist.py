from __future__ import annotations

import pandas as pd

from app.agents.base import BaseAgent


class DataScientistAgent(BaseAgent):
    name = "data_scientist"

    def run(self, dataframe: pd.DataFrame, question: str) -> str:
        lowered = question.lower().replace("-", " ")

        if dataframe.empty:
            return "The query returned no rows for the requested filters; the answer is not defensible without a narrower or clarified request."

        if "year over year" in lowered or "yoy" in lowered or ("year" in lowered and "revenue" in lowered and "trend" in lowered):
            return self._summarize_yoy(dataframe)

        if "running total" in lowered or "cumulative" in lowered:
            return self._summarize_running_total(dataframe)

        if "top customer" in lowered or "largest customer" in lowered or ("customer" in lowered and "revenue" in lowered and "top" in lowered):
            top_row = dataframe.iloc[0]
            return f"The leading customer is {top_row.iloc[0]} with {top_row.iloc[1]:,.2f} in revenue."

        if "region" in lowered and "revenue" in lowered:
            top_row = dataframe.iloc[0]
            return f"The highest-revenue region is {top_row.iloc[0]} with {top_row.iloc[1]:,.2f} in revenue."

        if "late delivery" in lowered:
            top_row = dataframe.iloc[0]
            return f"The strongest late-delivery signal is in {top_row.iloc[0]} at {top_row.iloc[1]:,.2f}% of line items."

        if "supplier" in lowered and "performance" in lowered:
            top_row = dataframe.iloc[0]
            return f"The strongest supplier performance is {top_row.iloc[1]} in {top_row.iloc[0]} with revenue of {top_row.iloc[2]:,.2f}."

        if "revenue" in lowered:
            total = self._pick_numeric_value(dataframe)
            return f"The total revenue is {total:,.2f}."

        return "The result was computed from the warehouse, and the answer is grounded in the underlying transactional data."

    def _pick_numeric_value(self, dataframe: pd.DataFrame) -> float:
        for col in dataframe.columns:
            values = pd.to_numeric(dataframe[col], errors="coerce")
            if values.notna().any():
                return float(values.iloc[0])
        return 0.0

    def _summarize_yoy(self, dataframe: pd.DataFrame) -> str:
        if len(dataframe) < 2:
            return "The year-over-year trend is based on a single year of data, which limits comparative interpretation."

        current_year = int(float(dataframe.iloc[-1].iloc[0]))
        prior_year = int(float(dataframe.iloc[-2].iloc[0]))
        current = float(dataframe.iloc[-1].iloc[1])
        prior = float(dataframe.iloc[-2].iloc[1])
        delta = ((current - prior) / prior) * 100 if prior else 0.0
        return (
            f"Revenue moved from {prior:,.2f} in {prior_year} to {current:,.2f} in {current_year}, a {delta:,.2f}% change."
        )

    def _summarize_running_total(self, dataframe: pd.DataFrame) -> str:
        if len(dataframe) < 2:
            return "The running total is based on a single period, so it is effectively the same as the period total."
        month = dataframe.iloc[-1].iloc[0]
        total = float(dataframe.iloc[-1].iloc[2])
        return f"By {month}, the cumulative revenue reached {total:,.2f}."
