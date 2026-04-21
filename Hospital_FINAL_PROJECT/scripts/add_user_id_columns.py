import sqlite3

DB_PATH = r"c:\Users\asuto\Desktop\H_M_S\database\hospital.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

for table in ["patients", "doctors"]:
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()]
    if "user_id" not in cols:
        print(f"Adding user_id to {table}")
        cur.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER")
    else:
        print(f"user_id already exists in {table}")

conn.commit()
conn.close()
