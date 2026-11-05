from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, List

import duckdb

from app.config import settings


class Warehouse:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.database_path
        path = Path(self.db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = duckdb.connect(self.db_path)
        self._ensure_tpch()

    def _ensure_tpch(self) -> None:
        path = Path(self.db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tables = [
            "customer",
            "lineitem",
            "nation",
            "orders",
            "part",
            "partsupp",
            "region",
            "supplier",
        ]
        existing = self.connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
        existing_names = {row[0].lower() for row in existing}
        if all(table in existing_names for table in tables):
            return

        try:
            self.connection.execute("INSTALL tpch")
            self.connection.execute("LOAD tpch")
            self.connection.execute("CALL dbgen(sf = 0.1)")
        except Exception:
            raise RuntimeError(
                "TPC-H data could not be generated. Ensure network access for DuckDB tpch extension or set up a local parquet fallback."
            )

    def execute(self, sql: str) -> List[Any]:
        sql = sql.strip().rstrip(";")
        return self.connection.execute(sql).fetchall()

    def query_df(self, sql: str):
        sql = sql.strip().rstrip(";")
        return self.connection.execute(sql).fetchdf()

    def table_exists(self, table: str) -> bool:
        result = self.connection.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'main' AND lower(table_name) = lower(?)",
            [table],
        ).fetchone()
        return bool(result and result[0] > 0)

    def close(self) -> None:
        self.connection.close()


def get_warehouse() -> Warehouse:
    return Warehouse()
