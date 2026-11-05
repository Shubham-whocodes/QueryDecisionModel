from app.decision_engine import DecisionEngine


def test_supported_question_returns_answer():
    engine = DecisionEngine()
    result = engine.answer("What was the total revenue in 1995?")
    assert result.status == "answered"
    assert result.sql
    assert result.confidence > 0.0


def test_refusal_question_is_rejected():
    engine = DecisionEngine()
    result = engine.answer("What is the customer satisfaction score by nation?")
    assert result.status in {"refusal", "clarify"}


def test_year_over_year_question_is_supported():
    engine = DecisionEngine()
    result = engine.answer("What was year-over-year revenue trend across the TPC-H dataset?")
    assert result.status == "answered"
    assert "revenue" in result.narrative.lower() or "trend" in result.narrative.lower()


def test_general_chat_question_is_handled_naturally():
    engine = DecisionEngine()
    result = engine.answer("Who built you?")
    assert result.status == "general"
    assert "DecisionModel" in result.answer


def test_conversation_memory_is_kept_for_follow_up_questions():
    engine = DecisionEngine()
    engine.answer("Who built you?")
    follow_up = engine.answer("How do you work?")
    assert follow_up.status == "general"
    assert len(engine.conversation_history) >= 2
