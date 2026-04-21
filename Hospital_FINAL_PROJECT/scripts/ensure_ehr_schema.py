import sqlite3

DB_PATH = r"c:\Users\asuto\Desktop\H_M_S\database\hospital.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cols = [r[1] for r in cur.execute('PRAGMA table_info(ehr)').fetchall()]
print('ehr columns:', cols)

to_add = {
    'treatment_plan': 'TEXT',
    'medications': 'TEXT',
    'notes': 'TEXT',
    'created_at': 'TIMESTAMP'
}

for col, col_type in to_add.items():
    if col not in cols:
        print(f'Adding column: {col}')
        cur.execute(f'ALTER TABLE ehr ADD COLUMN {col} {col_type}')

conn.commit()
conn.close()
