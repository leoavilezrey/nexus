import sqlite3
import pprint

conn = sqlite3.connect('../personal_file_mcp/files.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

tables = ['files', 'metadata', 'descriptions']

for t in tables:
    print(f"\n--- {t} ---")
    cur.execute(f"PRAGMA table_info({t});")
    for row in cur.fetchall():
        print(f"{row['name']} ({row['type']})")

conn.close()
