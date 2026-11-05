# DecisionModel

DecisionModel is a board-grade decision engine built over the TPC-H SF 0.1 warehouse. It accepts plain-English business questions, converts them into governed SQL, executes them safely against DuckDB, and returns a trustworthy answer with a chart, table, narrative, and provenance.

## Why this direction

The brief is not asking for a generic AI chatbot. It is asking for a trusted decision engine that can say "I cannot answer reliably" instead of guessing. We therefore chose a constrained, explainable architecture with a semantic layer and explicit governance rules.

This project is intentionally hybrid: it keeps a strict warehouse-governed analytics path for business questions, while also supporting normal general conversation and short-term memory outside the data layer. The general chat path is intentionally conversational, but the SQL analytics path remains the source of truth for numbers and evidence.

## Core design choices

- Semantic layer: business concepts such as revenue, late-delivery rate, region revenue, and top customer are defined explicitly, not inferred ad hoc.
- Multi-role internal architecture: QueryEnhancer, Planner, QueryDecomposer, Executor, DataScientist, Visualizer, and Governance each own a narrow responsibility.
- Governance-first logic: unsupported or ambiguous queries are refused or clarified before SQL generation.
- Evidence and trust: every answer includes SQL, chart metadata, a narrative summary, and confidence scoring.
- Evaluation harness: 24 benchmark questions validate both answerability and refusal quality.

## Architecture

```text
User question
   ↓
GovernanceAgent
   ↓
QueryEnhancerAgent
   ↓
QueryDecomposerAgent
   ↓
PlannerAgent
   ↓
ExecutorAgent (DuckDB SQL)
   ↓
DataScientistAgent + VisualizerAgent
   ↓
BusinessAnswer
```

## Run locally

```bash
cd DecisionModel
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Open the browser at http://localhost:8000/ to use the interactive decision engine.

Then call:

```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"question":"What was total revenue in 1995?"}'
```

## Product UI

The application includes an interactive front end with:

- plain-English question input
- real-time answer rendering
- Plotly chart output
- result table display
- refusal and clarification status handling

## Reproduce the evaluation

```bash
cd DecisionModel
source .venv/bin/activate
python -m app.evaluator
```

## Docker

```bash
cd DecisionModel
docker compose up --build
```

## What was deliberately cut

To stay within the time constraints, we focused on a strong, disciplined system over a sprawling multi-agent orchestration. We did not build a full enterprise feature matrix or external authentication layer; the goal was correctness, trust, and explainability over breadth.

## Known limitations

- The warehouse is constrained to TPC-H data and a small set of business metrics.
- The system is intentionally conservative: unsupported metrics trigger refusal.
- The semantic layer is config-driven but intentionally compact rather than fully generic.

## Why this is board-grade

A board-grade decision engine should not feel clever. It should be precise, explainable, and honest. This system is designed to produce answers only when the evidence is defensible and to surface uncertainty early.
