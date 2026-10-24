import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "insurance.db"

SMOKER_SUMMARY = """
SELECT smoker,
       COUNT(*)              AS members,
       ROUND(AVG(charges), 2) AS avg_charges
FROM members
GROUP BY smoker;
"""


def smoker_summary(db_path: Path = DB_PATH) -> pd.DataFrame:
    with closing(sqlite3.connect(db_path)) as conn:
        return pd.read_sql(SMOKER_SUMMARY, conn)


def main():
    print(smoker_summary())


if __name__ == "__main__":
    main()
