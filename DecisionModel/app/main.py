from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.decision_engine import DecisionEngine

app = FastAPI(title="DecisionModel", version="0.1.0")
engine = DecisionEngine()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health() -> dict:
    return engine.health()


@app.post("/answer")
def answer(payload: QuestionRequest) -> dict:
    result = engine.answer(payload.question)
    return {
        "status": result.status,
        "answer": result.answer,
        "sql": result.sql,
        "confidence": result.confidence,
        "narrative": result.narrative,
        "chart": result.chart,
        "table": result.table,
        "evidence": result.evidence,
        "metadata": result.metadata,
        "clarifications": result.clarifications,
        "mode": result.mode,
    }


app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
