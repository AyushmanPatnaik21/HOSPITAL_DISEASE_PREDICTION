import sqlite3
import os
from datetime import datetime

def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "database", "hospital.db")
    return sqlite3.connect(db_path)


def add_record(patient_id, doctor_id, diagnosis, treatment_plan, medications, notes):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ehr (patient_id, doctor_id, diagnosis, treatment_plan, medications, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, doctor_id, diagnosis, treatment_plan, medications, notes, datetime.now()))

    conn.commit()
    conn.close()


def get_all_records():
    """Get all EHR records"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.ehr_id, p.name, d.name, e.diagnosis, e.treatment_plan, e.medications, e.notes, e.created_at
        FROM ehr e
        JOIN patients p ON e.patient_id = p.patient_id
        JOIN doctors d ON e.doctor_id = d.doctor_id
        ORDER BY e.created_at DESC
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def get_records_by_patient(patient_id):
    """Get EHR records for a specific patient"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.ehr_id, p.name, d.name, e.diagnosis, e.treatment_plan, e.medications, e.notes, e.created_at
        FROM ehr e
        JOIN patients p ON e.patient_id = p.patient_id
        JOIN doctors d ON e.doctor_id = d.doctor_id
        WHERE e.patient_id = ?
        ORDER BY e.created_at DESC
    """, (patient_id,))

    data = cursor.fetchall()
    conn.close()
    return data


def get_record_by_id(record_id):
    """Get a specific EHR record"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.ehr_id, p.name, d.name, e.diagnosis, e.treatment_plan, e.medications, e.notes, e.created_at
        FROM ehr e
        JOIN patients p ON e.patient_id = p.patient_id
        JOIN doctors d ON e.doctor_id = d.doctor_id
        WHERE e.ehr_id = ?
    """, (record_id,))

    data = cursor.fetchone()
    conn.close()
    return data


def delete_record(record_id):
    """Delete an EHR record"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ehr WHERE ehr_id = ?", (record_id,))
    conn.commit()
    conn.close()


def get_records_by_user(user_id):
    """Get EHR records for patients associated with a specific user"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.ehr_id, p.name, d.name, e.diagnosis, e.treatment_plan, e.medications, e.notes, e.created_at
        FROM ehr e
        JOIN patients p ON e.patient_id = p.patient_id
        JOIN doctors d ON e.doctor_id = d.doctor_id
        WHERE p.user_id = ?
        ORDER BY e.created_at DESC
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data