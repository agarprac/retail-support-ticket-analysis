# load tickets csv into a local sqlite db so I can actually write SQL against it
# using sqlite just because it doesn't need a server, queries are normal SQL either way

import pandas as pd
import sqlite3

df = pd.read_csv("/home/claude/portfolio_project/data/support_tickets.csv")

conn = sqlite3.connect("/home/claude/portfolio_project/data/tickets.db")
df.to_sql("support_tickets", conn, if_exists="replace", index=False)

cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM support_tickets")
print("rows loaded:", cur.fetchone()[0])

conn.close()
