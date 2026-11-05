from __future__ import annotations

import json
from typing import Any, Dict, List

from app.decision_engine import DecisionEngine


EVAL_QUESTIONS: List[Dict[str, Any]] = [
    {"id": "Q1", "question": "What was the total revenue in 1995?", "expected_status": "answered"},
    {"id": "Q2", "question": "What was revenue by region in 1995?", "expected_status": "answered"},
    {"id": "Q3", "question": "Who were the top 5 customers by revenue in 1995?", "expected_status": "answered"},
    {"id": "Q4", "question": "What was year-over-year revenue trend across the TPC-H dataset?", "expected_status": "answered"},
    {"id": "Q5", "question": "Which suppliers generated the most revenue?", "expected_status": "answered"},
    {"id": "Q6", "question": "What was the average order value by nation in 1995?", "expected_status": "answered"},
    {"id": "Q7", "question": "What was the late-delivery rate by nation in 1995?", "expected_status": "answered"},
    {"id": "Q8", "question": "Show total revenue by year.", "expected_status": "answered"},
    {"id": "Q9", "question": "Which 3 regions had the highest revenue in 1995?", "expected_status": "answered"},
    {"id": "Q10", "question": "List the top 10 suppliers by revenue in 1995.", "expected_status": "answered"},
    {"id": "Q11", "question": "What was the total revenue in 1996?", "expected_status": "answered"},
    {"id": "Q12", "question": "What was the average order value by region in 1995?", "expected_status": "answered"},
    {"id": "Q13", "question": "Which customer generated the highest revenue in 1994?", "expected_status": "answered"},
    {"id": "Q14", "question": "Compare revenue growth from 1994 to 1995.", "expected_status": "answered"},
    {"id": "Q15", "question": "Which nation had the highest late-delivery rate in 1995?", "expected_status": "answered"},
    {"id": "Q16", "question": "What was the average customer order value by nation?", "expected_status": "answered"},
    {"id": "Q17", "question": "What is the customer satisfaction score by nation?", "expected_status": "refusal"},
    {"id": "Q18", "question": "Which employee had the highest turnover in 1995?", "expected_status": "refusal"},
    {"id": "Q19", "question": "Which product color had the highest returns?", "expected_status": "refusal"},
    {"id": "Q20", "question": "Which supplier was most likely to leave the network next quarter?", "expected_status": "refusal"},
    {"id": "Q21", "question": "Tell me the revenue by customer for the last quarter of 1995.", "expected_status": "clarify"},
    {"id": "Q22", "question": "Can you summarize supplier performance by nation?", "expected_status": "answered"},
    {"id": "Q23", "question": "What are the top 3 late-delivery regions?", "expected_status": "answered"},
    {"id": "Q24", "question": "What is the running total revenue by month?", "expected_status": "answered"},
]


def run_eval(cli: bool = False) -> List[Dict[str, Any]]:
    engine = DecisionEngine()
    results: List[Dict[str, Any]] = []
    for item in EVAL_QUESTIONS:
        result = engine.answer(item["question"])
        observed = result.status
        passed = observed == item["expected_status"]
        row = {
            "id": item["id"],
            "question": item["question"],
            "expected_status": item["expected_status"],
            "observed_status": observed,
            "passed": passed,
            "confidence": result.confidence,
            "answer": result.answer,
            "sql": result.sql,
        }
        results.append(row)
        if cli:
            print(json.dumps({"id": item["id"], "question": item["question"], "status": observed, "passed": passed}, indent=2))
    return results


if __name__ == "__main__":
    run_eval(cli=True)
