from __future__ import annotations

from typing import Any, List

import pandas as pd

from app.agents.base import BaseAgent
from app.db import Warehouse


class ExecutionAgent(BaseAgent):
    name = "executor"

    def __init__(self, warehouse: Warehouse):
        self.warehouse = warehouse

    def run(self, sql: str) -> pd.DataFrame:
        return self.warehouse.query_df(sql)
