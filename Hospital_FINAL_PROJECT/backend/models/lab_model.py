import sqlite3
import os
from datetime import datetime

def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "database", "hospital.db")
    return sqlite3.connect(db_path)

def ensure_parameters_column():
    """Ensure parameters column exists in lab_test_types table"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if parameters column exists
        cursor.execute("PRAGMA table_info(lab_test_types)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'parameters' not in columns:
            # Add the column
            cursor.execute("""
                ALTER TABLE lab_test_types
                ADD COLUMN parameters TEXT
            """)
            conn.commit()
            print("✓ Added parameters column to lab_test_types")
        
        conn.close()
    except Exception as e:
        print(f"Note: Could not ensure parameters column: {e}")

# Initialize on import
ensure_parameters_column()

# ==================== LAB TEST TYPES MANAGEMENT ====================

def create_lab_test_type(test_name, price, description, parameters=None):
    """Create a new lab test type"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO lab_test_types (test_name, price, description, parameters)
            VALUES (?, ?, ?, ?)
        """, (test_name, price, description, parameters))
    except sqlite3.OperationalError:
        # Fallback if parameters column doesn't exist
        cursor.execute("""
            INSERT INTO lab_test_types (test_name, price, description)
            VALUES (?, ?, ?)
        """, (test_name, price, description))

    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_all_lab_test_types():
    """Get all available lab test types"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, test_name, price, description, parameters
            FROM lab_test_types
            ORDER BY test_name
        """)
    except sqlite3.OperationalError:
        # Fallback if parameters column doesn't exist
        cursor.execute("""
            SELECT id, test_name, price, description, NULL as parameters
            FROM lab_test_types
            ORDER BY test_name
        """)

    data = cursor.fetchall()
    conn.close()
    return data

def get_lab_test_type_by_id(test_id):
    """Get a specific lab test type by ID"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, test_name, price, description, parameters
            FROM lab_test_types
            WHERE id = ?
        """, (test_id,))
    except sqlite3.OperationalError:
        # Fallback if parameters column doesn't exist
        cursor.execute("""
            SELECT id, test_name, price, description, NULL as parameters
            FROM lab_test_types
            WHERE id = ?
        """, (test_id,))

    data = cursor.fetchone()
    conn.close()
    return data

def update_lab_test_type(test_id, test_name, price, description, parameters=None):
    """Update a lab test type"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE lab_test_types
            SET test_name = ?, price = ?, description = ?, parameters = ?
            WHERE id = ?
        """, (test_name, price, description, parameters, test_id))
    except sqlite3.OperationalError:
        # Fallback if parameters column doesn't exist
        cursor.execute("""
            UPDATE lab_test_types
            SET test_name = ?, price = ?, description = ?
            WHERE id = ?
        """, (test_name, price, description, test_id))

    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_lab_test_type(test_id):
    """Delete a lab test type"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM lab_test_types WHERE id = ?", (test_id,))

    conn.commit()
    conn.close()
    return cursor.rowcount > 0

# ==================== TEST BOOKINGS MANAGEMENT ====================

def create_test_booking(patient_id, test_id, booking_date, booking_time=None, prescription_file=None, notes=None):
    """Create a new test booking"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO test_bookings (patient_id, test_id, booking_date, booking_time, prescription_file, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (patient_id, test_id, booking_date, booking_time, prescription_file, notes))

    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_test_bookings_by_patient(patient_id):
    """Get all test bookings for a specific patient"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tb.id, tb.patient_id, tb.test_id, tb.booking_date, tb.booking_time,
               tb.status, tb.prescription_file, tb.report_file, tb.notes, tb.created_at,
               ltt.test_name, ltt.price, ltt.description
        FROM test_bookings tb
        JOIN lab_test_types ltt ON tb.test_id = ltt.id
        WHERE tb.patient_id = ?
        ORDER BY tb.booking_date DESC, tb.created_at DESC
    """, (patient_id,))

    data = cursor.fetchall()
    conn.close()
    return data

def get_all_test_bookings():
    """Get all test bookings (for admin)"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tb.id, tb.patient_id, tb.test_id, tb.booking_date, tb.booking_time,
               tb.status, tb.prescription_file, tb.report_file, tb.notes, tb.created_at,
               ltt.test_name, ltt.price, ltt.description, p.name as patient_name
        FROM test_bookings tb
        JOIN lab_test_types ltt ON tb.test_id = ltt.id
        JOIN patients p ON tb.patient_id = p.patient_id
        ORDER BY tb.booking_date DESC, tb.created_at DESC
    """)

    data = cursor.fetchall()
    conn.close()
    return data

def get_test_booking_by_id(booking_id):
    """Get a specific test booking by ID"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tb.id, tb.patient_id, tb.test_id, tb.booking_date, tb.booking_time,
               tb.status, tb.prescription_file, tb.report_file, tb.notes, tb.created_at,
               ltt.test_name, ltt.price, ltt.description, p.name as patient_name
        FROM test_bookings tb
        JOIN lab_test_types ltt ON tb.test_id = ltt.id
        JOIN patients p ON tb.patient_id = p.patient_id
        WHERE tb.id = ?
    """, (booking_id,))

    data = cursor.fetchone()
    conn.close()
    return data

def update_booking_status(booking_id, status, report_file=None):
    """Update booking status and optionally set report file"""
    conn = get_db()
    cursor = conn.cursor()

    if report_file:
        cursor.execute("""
            UPDATE test_bookings
            SET status = ?, report_file = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, report_file, booking_id))
    else:
        cursor.execute("""
            UPDATE test_bookings
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, booking_id))

    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_test_booking(booking_id):
    """Delete a test booking"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM test_bookings WHERE id = ?", (booking_id,))

    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def check_duplicate_booking(patient_id, test_id, booking_date):
    """Check if patient already has a booking for same test on same date"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM test_bookings
        WHERE patient_id = ? AND test_id = ? AND booking_date = ? AND status != 'Cancelled'
    """, (patient_id, test_id, booking_date))

    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# ==================== DASHBOARD STATISTICS ====================

def get_dashboard_stats():
    """Get statistics for admin dashboard"""
    conn = get_db()
    cursor = conn.cursor()

    # Total lab test types
    cursor.execute("SELECT COUNT(*) FROM lab_test_types")
    total_tests = cursor.fetchone()[0]

    # Total bookings
    cursor.execute("SELECT COUNT(*) FROM test_bookings")
    total_bookings = cursor.fetchone()[0]

    # Pending bookings
    cursor.execute("SELECT COUNT(*) FROM test_bookings WHERE status = 'Pending'")
    pending_bookings = cursor.fetchone()[0]

    # Completed bookings
    cursor.execute("SELECT COUNT(*) FROM test_bookings WHERE status = 'Completed'")
    completed_bookings = cursor.fetchone()[0]

    # Processing bookings
    cursor.execute("SELECT COUNT(*) FROM test_bookings WHERE status = 'Processing'")
    processing_bookings = cursor.fetchone()[0]

    # Sample collected bookings
    cursor.execute("SELECT COUNT(*) FROM test_bookings WHERE status = 'Sample Collected'")
    sample_collected = cursor.fetchone()[0]

    conn.close()

    return {
        'total_tests': total_tests,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'completed_bookings': completed_bookings,
        'processing_bookings': processing_bookings,
        'sample_collected': sample_collected,
        'reports_pending': total_bookings - completed_bookings
    }

def get_bookings_by_status(status):
    """Get all bookings for a specific status"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tb.id, tb.patient_id, tb.test_id, tb.booking_date, tb.booking_time,
               tb.status, tb.prescription_file, tb.report_file, tb.notes, tb.created_at,
               ltt.test_name, ltt.price, ltt.description, p.name as patient_name
        FROM test_bookings tb
        JOIN lab_test_types ltt ON tb.test_id = ltt.id
        JOIN patients p ON tb.patient_id = p.patient_id
        WHERE tb.status = ?
        ORDER BY tb.booking_date DESC, tb.created_at DESC
    """, (status,))

    data = cursor.fetchall()
    conn.close()
    return data

def get_recent_bookings(limit=10):
    """Get recent bookings for dashboard"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tb.id, tb.patient_id, tb.test_id, tb.booking_date, tb.booking_time,
               tb.status, tb.prescription_file, tb.report_file, tb.notes, tb.created_at,
               ltt.test_name, ltt.price, ltt.description, p.name as patient_name
        FROM test_bookings tb
        JOIN lab_test_types ltt ON tb.test_id = ltt.id
        JOIN patients p ON tb.patient_id = p.patient_id
        ORDER BY tb.created_at DESC
        LIMIT ?
    """, (limit,))

    data = cursor.fetchall()
    conn.close()
    return data

# ==================== LEGACY FUNCTIONS (for backward compatibility) ====================

def add_test(patient_id, test_type):
    # Only admins can create tests
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lab_tests (patient_id, test_type, result, status)
        VALUES (?, ?, '', 'Pending')
    """, (patient_id, test_type))

    conn.commit()
    conn.close()


def get_all_tests():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT l.test_id, p.name, l.test_type, l.result, l.status
        FROM lab_tests l
        JOIN patients p ON l.patient_id = p.patient_id
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def update_result(test_id, result):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE lab_tests
        SET result=?, status='Completed'
        WHERE test_id=?
    """, (result, test_id))

    conn.commit()
    conn.close()


def get_tests_by_patient(patient_id):
    """Get lab tests for a specific patient"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT l.test_id, p.name, l.test_type, l.result, l.status
        FROM lab_tests l
        JOIN patients p ON l.patient_id = p.patient_id
        WHERE l.patient_id = ?
    """, (patient_id,))

    data = cursor.fetchall()
    conn.close()
    return data


def get_tests_by_user(user_id):
    """Get lab tests for patients associated with a specific user"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT l.test_id, p.name, l.test_type, l.result, l.status
        FROM lab_tests l
        JOIN patients p ON l.patient_id = p.patient_id
        WHERE p.user_id = ?
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data