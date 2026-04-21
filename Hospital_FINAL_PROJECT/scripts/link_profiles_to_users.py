import sqlite3

DB_PATH = r"c:\Users\asuto\Desktop\H_M_S\database\hospital.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Link patients by name to users
cur.execute("SELECT user_id, name FROM users")
users = cur.fetchall()

for user_id, name in users:
    # only update patients without user_id
    cur.execute("SELECT patient_id FROM patients WHERE name=? AND (user_id IS NULL OR user_id='')", (name,))
    rows = cur.fetchall()
    for (patient_id,) in rows:
        print(f"Linking patient {patient_id} (name={name}) to user {user_id}")
        cur.execute("UPDATE patients SET user_id=? WHERE patient_id=?", (user_id, patient_id))

# Link doctors by name to users
for user_id, name in users:
    cur.execute("SELECT doctor_id FROM doctors WHERE name=? AND (user_id IS NULL OR user_id='')", (name,))
    rows = cur.fetchall()
    for (doctor_id,) in rows:
        print(f"Linking doctor {doctor_id} (name={name}) to user {user_id}")
        cur.execute("UPDATE doctors SET user_id=? WHERE doctor_id=?", (user_id, doctor_id))

conn.commit()
conn.close()
