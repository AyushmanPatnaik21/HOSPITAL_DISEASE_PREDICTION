#!/usr/bin/env python3
"""
Script to initialize lab test types in the database
"""

import sqlite3
import os

def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(BASE_DIR, "database", "hospital.db")
    return sqlite3.connect(db_path)

def init_lab_test_types():
    """Initialize the database with sample lab test types"""

    # Sample lab test data
    test_types = [
        ("Complete Blood Count (CBC)", 25.00, "Comprehensive blood test that evaluates overall health and detects disorders"),
        ("Lipid Profile", 35.00, "Measures cholesterol levels and triglyceride levels in the blood"),
        ("Blood Glucose Test", 15.00, "Measures glucose levels to screen for diabetes"),
        ("Thyroid Function Test", 45.00, "Evaluates thyroid hormone levels (TSH, T3, T4)"),
        ("Liver Function Test", 40.00, "Assesses liver health through enzyme and protein levels"),
        ("Kidney Function Test", 30.00, "Evaluates kidney health through creatinine and BUN levels"),
        ("Urine Analysis", 20.00, "Comprehensive analysis of urine for infections and other conditions"),
        ("Hemoglobin A1C", 28.00, "Measures average blood sugar levels over past 2-3 months"),
        ("Vitamin D Test", 50.00, "Assesses vitamin D levels for bone health and immunity"),
        ("Iron Studies", 35.00, "Evaluates iron levels and related markers for anemia diagnosis"),
    ]

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Check if table exists and has data
        cursor.execute("SELECT COUNT(*) FROM lab_test_types")
        count = cursor.fetchone()[0]

        if count == 0:
            print("Initializing lab test types...")

            cursor.executemany("""
                INSERT INTO lab_test_types (test_name, price, description)
                VALUES (?, ?, ?)
            """, test_types)

            conn.commit()
            print(f"Successfully added {len(test_types)} lab test types!")
        else:
            print(f"Lab test types already initialized ({count} existing records)")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_lab_test_types()