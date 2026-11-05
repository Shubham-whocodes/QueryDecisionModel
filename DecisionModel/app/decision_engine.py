from __future__ import annotations

from typing import Any, Dict, List

from app.agents.data_scientist import DataScientistAgent
from app.agents.executor import ExecutionAgent
from app.agents.governance import GovernanceAgent
from app.agents.planner import PlannerAgent
from app.agents.query_decomposer import QueryDecomposerAgent
from app.agents.query_enhancer import QueryEnhancerAgent
from app.agents.visualizer import VisualizerAgent
from app.db import get_warehouse
from app.models import BusinessAnswer
from app.semantic_layer import SemanticLayer
from app.services.llm_provider import LLMProvider


class DecisionEngine:
    def __init__(self, warehouse=None) -> None:
        self.warehouse = warehouse or get_warehouse()
        self.semantic_layer = SemanticLayer()
        self.governance = GovernanceAgent()
        self.enhancer = QueryEnhancerAgent()
        self.decomposer = QueryDecomposerAgent()
        self.planner = PlannerAgent(self.semantic_layer)
        self.executor = ExecutionAgent(self.warehouse)
        self.data_scientist = DataScientistAgent()
        self.visualizer = VisualizerAgent()
        self.llm = LLMProvider()
        self.conversation_history: List[Dict[str, str]] = []

    def _is_general_chat(self, question: str) -> bool:
        lowered = (question or "").strip().lower()
        if not lowered:
            return False

        general_markers = [
            "who built you",
            "who created you",
            "who are you",
            "what are you",
            "what can you do",
            "how do you work",
            "how are you",
            "hello",
            "hi",
            "hey",
            "thanks",
            "thank you",
            "can you help",
            "what is your name",
            "what do you do",
            "tell me about yourself",
            "what are your capabilities",
            "how should i use you",
            "what kind of questions can you answer",
        ]
        if any(marker in lowered for marker in general_markers):
            return True

        business_terms = [
            "revenue",
            "customer",
            "supplier",
            "region",
            "nation",
            "late delivery",
            "order count",
            "sales",
            "discount",
            "ship",
            "returns",
            "metric",
            "by month",
            "by year",
            "by quarter",
        ]
        if any(term in lowered for term in business_terms):
            return False

        return False

    def _default_general_response(self, question: str) -> str:
        lowered = (question or "").strip().lower()
        if "who built you" in lowered or "who created you" in lowered:
            return (
                "I’m DecisionModel, a SQL analytics assistant built to answer trusted business questions over a TPC-H warehouse. "
                "I combine a governed warehouse, a semantic layer, and a conversational interface so the answers are grounded in evidence instead of guessing."
            )
        if "who are you" in lowered or "what are you" in lowered:
            return (
                "I’m DecisionModel, an analytics copilot designed for governed decision support. I can explain how the system works, talk through business questions, and answer warehouse-backed questions with SQL and evidence."
            )
        if "how do you work" in lowered or "how are you" in lowered:
            return (
                "I route the question through a clear decision pipeline: understand the intent, check whether it belongs to the warehouse, plan the SQL, execute it, and then summarize the result with evidence and charts. If the question is out of scope, I refuse or ask for clarification instead of guessing."
            )
        return (
            "I’m DecisionModel, a governed analytics assistant. I can hold a normal conversation, explain the decision engine, and answer supported warehouse questions with SQL-backed evidence. If a question falls outside the available data, I’ll clarify or refuse rather than invent an answer."
        )

    def _record_conversation(self, question: str, answer: str) -> None:
        self.conversation_history.append({"question": question, "answer": answer})
        self.conversation_history = self.conversation_history[-8:]

    def _general_chat_answer(self, question: str) -> BusinessAnswer:
        history = self.conversation_history[-6:]
        history_text = "\n".join(
            f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history
        )

        prompt = (
            "You are DecisionModel, a hybrid analytics assistant. "
            "Answer general conversation naturally and stay consistent with the previous context. "
            "Be concise but helpful. If the user asks about your identity or design, explain that you are a governed analytics system built for SQL-backed business questions. "
            "Do not pretend to be human.\n\n"
            f"Recent conversation:\n{history_text if history_text else 'No prior conversation.'}\n\n"
            f"Current user message: {question}\n\n"
            "Answer in plain language."
        )
        llm_answer = (self.llm.generate(prompt) or "").strip()
        response = llm_answer or self._default_general_response(question)

        result = BusinessAnswer(
            question=question,
            status="general",
            answer=response,
            sql="",
            confidence=0.82,
            chart={"type": "table", "data": [], "layout": {}},
            table=[],
            narrative=response,
            evidence=["General conversational response outside the governed warehouse path."],
            metadata={"conversation_history": history, "interaction_mode": "general"},
            mode="general",
        )
        self._record_conversation(question, result.answer)
        return result

    def answer(self, question: str) -> BusinessAnswer:
        q = (question or "").strip()
        if not q:
            return BusinessAnswer(
                question="",
                status="clarify",
                answer="Please ask a specific question about revenue, customer ranking, supplier performance, or late delivery.",
                sql="",
                confidence=0.0,
                chart={"type": "table", "data": [], "layout": {}},
                table=[],
                narrative="No question was provided.",
                evidence=["Question is empty."],
                clarifications=["Please specify a time window or business dimension."],
            )

        if self._is_general_chat(q):
            return self._general_chat_answer(q)

        governance = self.governance.run(q)
        if governance["status"] == "refuse":
            result = BusinessAnswer(
                question=q,
                status="refusal",
                answer="I cannot answer this reliably from the TPC-H data available in this warehouse.",
                sql="",
                confidence=0.0,
                chart={"type": "table", "data": [], "layout": {}},
                table=[],
                narrative=governance["reason"],
                evidence=[governance["reason"]],
                clarifications=["Please ask about revenue, customer ranking, supplier performance, region performance, or late-delivery behavior."],
            )
            self._record_conversation(q, result.answer)
            return result
        if governance["status"] == "clarify":
            result = BusinessAnswer(
                question=q,
                status="clarify",
                answer="Please clarify the exact time window or dimension before I compute this answer.",
                sql="",
                confidence=0.0,
                chart={"type": "table", "data": [], "layout": {}},
                table=[],
                narrative=governance["reason"],
                evidence=[governance["reason"]],
                clarifications=[governance["reason"]],
            )
            self._record_conversation(q, result.answer)
            return result

        enhanced = self.enhancer.run(q)
        decomposition = self.decomposer.run(q, enhanced)
        plan = self.planner.run(q, enhanced)

        if plan["status"] == "refuse":
            result = BusinessAnswer(
                question=q,
                status="refusal",
                answer="I cannot answer this reliably from the TPC-H data available in this warehouse.",
                sql="",
                confidence=0.0,
                chart={"type": "table", "data": [], "layout": {}},
                table=[],
                narrative=plan["reason"],
                evidence=[plan["reason"]],
            )
            self._record_conversation(q, result.answer)
            return result

        if plan["status"] == "clarify":
            result = BusinessAnswer(
                question=q,
                status="clarify",
                answer="Please clarify the time window or region for this metric before I compute it.",
                sql="",
                confidence=0.0,
                chart={"type": "table", "data": [], "layout": {}},
                table=[],
                narrative=plan["reason"],
                evidence=[plan["reason"]],
                clarifications=[plan["reason"]],
            )
            self._record_conversation(q, result.answer)
            return result

        sql = plan["sql"]
        df = self.executor.run(sql)
        chart = self.visualizer.run(df, q, plan.get("chart_type", "bar"))
        narrative = self.data_scientist.run(df, q)

        result_rows = df.to_dict(orient="records")
        result = BusinessAnswer(
            question=q,
            status="answered",
            answer=narrative,
            sql=sql,
            confidence=float(plan.get("confidence", 0.8)),
            chart=chart,
            table=result_rows,
            narrative=narrative,
            evidence=[
                "Question was translated into approved SQL against the TPC-H warehouse.",
                "The chart and summary are derived from the executed result set.",
            ],
            metadata={
                "decomposition": decomposition,
                "business_terms": enhanced["business_terms"],
                "row_count": len(result_rows),
            },
        )
        self._record_conversation(q, result.answer)
        return result

    def health(self) -> Dict[str, str]:
        return {"status": "ok", "warehouse": "duckdb"}
