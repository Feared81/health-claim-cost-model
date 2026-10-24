import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "kaggle" / "insurance.csv"
DB_PATH = PROJECT_ROOT / "data" / "processed" / "insurance.db"


def load_csv_to_sqlite(csv_path: Path = RAW_CSV, db_path: Path = DB_PATH) -> int:
    """Read the raw CSV and replace the `members` table. Returns the row count."""
    df = pd.read_csv(csv_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        df.to_sql("members", conn, if_exists="replace", index=False)

    return len(df)


def main():
    rows = load_csv_to_sqlite()
    print(f"loaded {rows} rows into {DB_PATH}")


if __name__ == "__main__":
    main()
