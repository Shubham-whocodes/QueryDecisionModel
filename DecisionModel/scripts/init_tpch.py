from __future__ import annotations

from app.db import Warehouse


if __name__ == "__main__":
    warehouse = Warehouse()
    print("TPC-H dataset ready at", warehouse.db_path)
    warehouse.close()
