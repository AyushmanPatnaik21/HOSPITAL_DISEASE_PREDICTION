import sqlite3
import os

def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "database", "hospital.db")
    return sqlite3.connect(db_path)


def add_patient(name, age, gender, contact, address, medical_history, user_id=None):
    conn = get_db()
    cursor = conn.cursor()

    if user_id:
        cursor.execute("""
            INSERT INTO patients (name, age, gender, contact, address, medical_history, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, age, gender, contact, address, medical_history, user_id))
    else:
        cursor.execute("""
            INSERT INTO patients (name, age, gender, contact, address, medical_history)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, age, gender, contact, address, medical_history))

    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id


def get_all_patients():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    data = cursor.fetchall()

    conn.close()
    return data


def get_patient(patient_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    data = cursor.fetchone()

    conn.close()
    return data


def get_patients_by_user_id(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
    data = cursor.fetchall()

    conn.close()
    return data


def get_patient_by_user_id(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()

    conn.close()
    return data


def check_patient_exists_by_name(user_id, name):
    """Check if a patient with a specific name exists for a user"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE user_id = ? AND name = ?",
        (user_id, name)
    )
    data = cursor.fetchone()

    conn.close()
    return data is not None


def update_patient(patient_id, name, age, gender, contact, address, medical_history):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE patients
        SET name=?, age=?, gender=?, contact=?, address=?, medical_history=?
        WHERE patient_id=?
    """, (name, age, gender, contact, address, medical_history, patient_id))

    conn.commit()
    conn.close()


def delete_patient(patient_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
    conn.commit()
    conn.close()


def get_patients_for_user(user_id):
    """Get all patients associated with a specific user"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
    data = cursor.fetchall()

    conn.close()
    return data


def get_patient_by_user_id(user_id):
    """Get the patient record for a specific user (returns single record)"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()

    conn.close()
    return data


def search_patients_by_name(name):
    """Search patients by name (case-insensitive partial match)"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT patient_id, name FROM patients WHERE LOWER(name) LIKE LOWER(?)", (f'%{name}%',))
    data = cursor.fetchall()

    conn.close()
    return data