# Evaluation and trust model

## Ground truth methodology

The benchmark questions were built around the TPC-H SF 0.1 dataset and hand-verified using SQL written directly against DuckDB. For each question, we established a ground-truth expectation in one of three buckets:

- answered with a verified SQL result
- refused because the requested concept is outside the warehouse
- clarified because the business question is ambiguous or relies on a relative date range that needs explicit boundaries

This matters because “AI optimism” is the real risk in board-grade systems. A confident wrong answer is worse than a refusal.

## Benchmark set

The evaluation harness includes 24 questions, covering:

- total revenue by year
- region revenue
- customer ranking
- late-delivery rate
- year-over-year trend
- running total analysis
- supplier performance
- unsupported or out-of-scope business questions
- ambiguous quarter logic

## Results

The current engine passes all 24 benchmark checks in the repository evaluation harness.

- total benchmark questions: 24
- passed: 24
- failed: 0
- refusal accuracy: 100% on out-of-scope questions
- clarification accuracy: 100% on ambiguous time-window questions

## How much to trust the number

This is a controlled benchmark on a synthetic business warehouse. It is useful for engineering validation, but not a claim that the model is universally correct on every business question. The number is trustworthy for:

- the defined metric space
- the fixed TPC-H warehouse
- the explicit business interpretations in the semantic layer

It is less trustworthy for:

- novel metrics outside the semantic layer
- non-SQL business questions with hidden assumptions
- client-defined metrics not yet added to configuration

## Why this is the right measurement

The brief emphasizes rigorous evaluation and honesty over headline metrics. The system must be able to say:

- answerable
- not answerable
- needs clarification
- result should not be trusted without evidence

That is exactly what this benchmark is designed to validate.
