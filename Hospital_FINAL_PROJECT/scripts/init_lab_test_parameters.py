#!/usr/bin/env python3
"""
Migration script to add parameters field to lab tests
and initialize default parameters for common tests.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "database", "hospital.db")

def add_parameters_column():
    """Add parameters column to lab_test_types table if it doesn't exist"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(lab_test_types)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'parameters' in columns:
            print("✓ Parameters column already exists")
            conn.close()
            return True
        
        # Add the column
        cursor.execute("""
            ALTER TABLE lab_test_types
            ADD COLUMN parameters TEXT
        """)
        conn.commit()
        print("✓ Added parameters column to lab_test_types")
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error adding parameters column: {e}")
        conn.close()
        return False

def initialize_test_parameters():
    """Initialize parameters for common lab tests"""
    
    test_parameters = {
        "CBC": "Hemoglobin,RBC Count,WBC Count,Platelets,MCV,MCH,MCHC",
        "Blood Sugar": "Fasting Sugar,Postprandial Sugar,HbA1c",
        "Thyroid": "T3,T4,TSH",
        "Liver Function": "SGOT,SGPT,Albumin,Total Bilirubin,Direct Bilirubin,ALP",
        "Kidney Function": "Creatinine,BUN,eGFR,Sodium,Potassium",
        "Lipid Profile": "Total Cholesterol,LDL,HDL,Triglycerides",
        "Vitamin D": "25-OH Vitamin D",
        "COVID-19": "RT-PCR Result,CT Value",
        "Vitamin B12": "Vitamin B12 Level",
        "Calcium": "Total Calcium,Ionized Calcium,Phosphorus",
    }
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        for test_name, parameters in test_parameters.items():
            cursor.execute("""
                UPDATE lab_test_types
                SET parameters = ?
                WHERE test_name = ? AND parameters IS NULL
            """, (parameters, test_name))
        
        conn.commit()
        rows_updated = cursor.rowcount
        print(f"✓ Initialized parameters for {rows_updated} tests")
        
    except Exception as e:
        print(f"✗ Error initializing test parameters: {e}")
        conn.rollback()
        
    finally:
        conn.close()

def get_test_overview():
    """Display current tests and their parameters"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, test_name, parameters
            FROM lab_test_types
            ORDER BY test_name
        """)
        
        tests = cursor.fetchall()
        print("\n" + "="*80)
        print("Lab Tests Overview:")
        print("="*80)
        
        for test_id, test_name, parameters in tests:
            param_display = parameters if parameters else "(no parameters configured)"
            print(f"\n[{test_id}] {test_name}")
            print(f"    Parameters: {param_display}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"✗ Error retrieving tests: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("Initializing Lab Test Parameters...")
    print("="*80)
    
    # Step 1: Add column
    if not add_parameters_column():
        sys.exit(1)
    
    # Step 2: Initialize parameters
    initialize_test_parameters()
    
    # Step 3: Display overview
    get_test_overview()
    
    print("\n✓ Migration completed successfully!")
