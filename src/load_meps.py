from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "meps"

FILES = {
    2020: "h224.dta",
    2021: "h233.dta",
    2022: "h243.dta",
    2023: "h251.dta",
    2024: "h256.dta",
}

def load_meps(year: int, columns: list[str] | None = None) -> pd.DataFrame:
    """Load one year of the MEPS Full Year Consolidated file."""
    path = DATA_DIR / str(year) / FILES[year]
    return pd.read_stata(path, columns=columns, convert_categoricals=False)

