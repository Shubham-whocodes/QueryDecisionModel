from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BusinessAnswer:
    question: str
    status: str
    answer: str
    sql: str
    confidence: float
    chart: Dict[str, Any]
    table: List[Dict[str, Any]]
    narrative: str
    evidence: List[str] = field(default_factory=list)
    clarifications: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    mode: str = "business"
