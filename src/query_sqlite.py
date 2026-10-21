import sqlite3
import pandas as pd

conn = sqlite3.connect("data/processed/insurance.db")

query = """
SELECT smoker,
       COUNT(*)              AS members,
       ROUND(AVG(charges), 2) AS avg_charges
FROM members
GROUP BY smoker;
"""
print(pd.read_sql(query, conn))
conn.close()