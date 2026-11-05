from __future__ import annotations

import argparse

from app.decision_engine import DecisionEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="DecisionModel CLI")
    parser.add_argument("question", nargs="+", help="Question to answer using the TPC-H warehouse")
    args = parser.parse_args()
    question = " ".join(args.question)

    engine = DecisionEngine()
    result = engine.answer(question)
    print(f"Status: {result.status}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Narrative: {result.narrative}")
    print(f"SQL: {result.sql}")
    print("Table:")
    for row in result.table:
        print(row)
    print("Chart:")
    print(result.chart)


if __name__ == "__main__":
    main()
