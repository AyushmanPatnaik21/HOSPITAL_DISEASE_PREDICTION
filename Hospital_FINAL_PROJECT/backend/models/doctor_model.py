import sqlite3
import os

def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "database", "hospital.db")
    return sqlite3.connect(db_path)


def add_doctor(name, specialization, contact, availability, user_id=None):
    conn = get_db()
    cursor = conn.cursor()

    if user_id:
        cursor.execute("""
            INSERT INTO doctors (name, specialization, contact, availability, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name, specialization, contact, availability, user_id))
    else:
        cursor.execute("""
            INSERT INTO doctors (name, specialization, contact, availability)
            VALUES (?, ?, ?, ?)
        """, (name, specialization, contact, availability))

    conn.commit()
    conn.close()


def get_all_doctors():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM doctors")
    data = cursor.fetchall()

    conn.close()
    return data


def get_doctor(doctor_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,))
    data = cursor.fetchone()

    conn.close()
    return data


def delete_doctor(doctor_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM doctors WHERE doctor_id=?", (doctor_id,))
    conn.commit()
    conn.close()


def get_doctor_by_user_id(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM doctors WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()

    conn.close()
    return data