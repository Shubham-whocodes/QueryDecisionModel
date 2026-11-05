# AI usage and human validation

This project was built with a disciplined AI-assisted workflow. The role of AI was to accelerate design, generate scaffolding, and test hypotheses, while the final code and logic were reviewed and adjusted by hand before submission.

## How AI was used

- Architecture and folder structure: AI helped structure the decision engine into clear responsibilities.
- Prompt design and workflow: AI helped shape the semantic-layer and refusal strategy.
- Code generation: most skeleton code for agents, service adapters, and API endpoints was drafted quickly.
- Test validation: AI assisted in thinking through edge cases and evaluation questions.

## What was accepted, rejected, or rewritten

Accepted:
- the modular agent-based decomposition
- the use of a semantic layer for business definitions
- governance-first refusal logic
- Dockerized local deployment

Rejected or rewritten:
- generic multi-agent autonomy that would hide reasoning and reduce trust
- over-broad business metrics not grounded in TPC-H schema
- uncontrolled SQL generation without checks

Updated stance for this build:
- the system has a general-conversation layer for identity, explanation, and follow-up dialogue
- the warehouse-backed analytics layer remains the trusted source for numbers and charts
- the model keeps short-lived conversational memory, but it does not let general chat override governed data evidence

The decisive principle was: AI could accelerate the build, but the final system had to be explicitly governed and explainable.

## Raw transcripts

No external AI session export was available in the local workspace for this task. The repository itself reflects the final verified result, and the system design was deliberately reviewed and constrained by the human owner before final submission.

## Guardrails used

- unsupported metrics must refuse
- ambiguous date windows must clarify
- all answers must include evidence chain and SQL output
- all core benchmark questions were manually checked against generated SQL results
