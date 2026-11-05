# Interview preparation guide

## What the company is really testing

The Unloq case study rewards engineers who can combine:

- business judgment
- SQL discipline
- evaluation rigor
- observation of uncertainty
- product thinking around trust and explainability

The goal is not to make an AI assistant that sounds smart. The goal is to make a system that accurately distinguishes between:

- answerable and defensible
- outside scope
- ambiguous
- evidence insufficient

## The design story to tell

"I built a board-grade decision engine over TPC-H. The architecture is intentionally constrained by a semantic layer and governance rules, because a confident wrong number is worse than a refusal. My system turns plain-English questions into SQL, validates them against explicit business definitions, and returns a chart, table, and narrative with provenance."

## Core design choices to explain

### 1. Why a semantic layer

Without a semantic layer, the system guesses what terms like revenue, late delivery, or top customer mean. The semantic layer makes the business contract explicit and reduces silent drift.

### 2. Why governance is first

A decision engine is not just generation; it is permissioning. The system should say no or ask for clarification whenever the data does not support the question.

### 3. Why evaluation matters

You are not just building a feature. You are building a system whose output must be trustworthy enough for a boardroom. That means evaluation is central, not optional.

### 4. Why the answer is not always one number

The best answer can include:

- chart
- narrative summary
- SQL provenance
- confidence metadata
- refusal or clarification path

## Questions interviewers may ask

### Why not just use a raw LLM?
Because raw generation will hallucinate metrics and produce confident but wrong SQL. The system needs constraints, governance, and measurement.

### Why is refusal important?
Because the business value of a decision engine is not in making something up. It is in identifying when the evidence is insufficient.

### Why Docker and a modular structure?
Because this is a product-grade engineering challenge. You want repeatability, clean boundaries, and easier validation.

### How do you know your answer is good?
By using a benchmark, verification against SQL, and explicit checks around unsupported and ambiguous questions.

## One-sentence product pitch

"I built a governed SQL-backed decision intelligence engine that answers what the data supports, refuses what it cannot justify, and explains the output so a finance leader can trust it."
