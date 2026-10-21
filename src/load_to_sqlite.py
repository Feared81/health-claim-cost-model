import sqlite3
import pandas as pd

df = pd.read_csv("data/raw/insurance.csv")

conn = sqlite3.connect("data/processed/insurance.db")
df.to_sql("members", conn, if_exists="replace", index=False)
conn.close()
