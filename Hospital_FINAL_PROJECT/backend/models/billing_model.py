import sqlite3
import os
from datetime import datetime

def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "database", "hospital.db")
    return sqlite3.connect(db_path)

# ==================== INITIALIZE BILLING TABLES ====================

def init_billing_tables():
    """Initialize billing tables if they don't exist"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create bills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billing_bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'Unpaid',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)
    
    # Create bill_items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billing_bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bill_id) REFERENCES billing_bills(id)
        )
    """)
    
    conn.commit()
    conn.close()

# ==================== BILL MANAGEMENT ====================

def create_bill(patient_id):
    """Create a new bill for a patient"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO billing_bills (patient_id, total_amount, status)
        VALUES (?, ?, ?)
    """, (patient_id, 0, 'Unpaid'))
    
    conn.commit()
    bill_id = cursor.lastrowid
    conn.close()
    return bill_id

def get_all_bills():
    """Get all bills with patient details"""
    init_billing_tables()  # Ensure tables exist
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            b.id, 
            b.patient_id,
            p.name AS patient_name,
            b.total_amount,
            b.status,
            b.created_at,
            COUNT(bi.id) AS item_count
        FROM billing_bills b
        LEFT JOIN patients p ON b.patient_id = p.patient_id
        LEFT JOIN billing_bill_items bi ON b.id = bi.bill_id
        GROUP BY b.id
        ORDER BY b.created_at DESC
    """)
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_bill_by_id(bill_id):
    """Get bill details by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            b.id,
            b.patient_id,
            p.name AS patient_name,
            p.contact,
            b.total_amount,
            b.status,
            b.created_at
        FROM billing_bills b
        LEFT JOIN patients p ON b.patient_id = p.patient_id
        WHERE b.id = ?
    """, (bill_id,))
    
    bill = cursor.fetchone()
    conn.close()
    return bill

def get_bills_by_patient(patient_id):
    """Get all bills for a specific patient"""
    init_billing_tables()  # Ensure tables exist
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            b.id,
            b.patient_id,
            p.name AS patient_name,
            b.total_amount,
            b.status,
            b.created_at,
            COUNT(bi.id) AS item_count
        FROM billing_bills b
        LEFT JOIN patients p ON b.patient_id = p.patient_id
        LEFT JOIN billing_bill_items bi ON b.id = bi.bill_id
        WHERE b.patient_id = ?
        GROUP BY b.id
        ORDER BY b.created_at DESC
    """, (patient_id,))
    
    data = cursor.fetchall()
    conn.close()
    return data

def update_bill_status(bill_id, status):
    """Update bill status (Paid/Unpaid)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE billing_bills
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, bill_id))
    
    conn.commit()
    conn.close()

def delete_bill(bill_id):
    """Delete a bill and its items"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Delete bill items first
    cursor.execute("DELETE FROM billing_bill_items WHERE bill_id = ?", (bill_id,))
    # Delete bill
    cursor.execute("DELETE FROM billing_bills WHERE id = ?", (bill_id,))
    
    conn.commit()
    conn.close()

# ==================== BILL ITEMS MANAGEMENT ====================

def add_bill_item(bill_id, description, amount):
    """Add an item to a bill"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO billing_bill_items (bill_id, description, amount)
        VALUES (?, ?, ?)
    """, (bill_id, description, amount))
    
    conn.commit()
    conn.close()
    
    # Update bill total
    update_bill_total(bill_id)

def get_bill_items(bill_id):
    """Get all items for a specific bill"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, bill_id, description, amount, created_at
        FROM billing_bill_items
        WHERE bill_id = ?
        ORDER BY created_at ASC
    """, (bill_id,))
    
    data = cursor.fetchall()
    conn.close()
    return data

def delete_bill_item(item_id):
    """Delete a bill item"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get bill_id before deleting
    cursor.execute("SELECT bill_id FROM billing_bill_items WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    bill_id = result[0] if result else None
    
    # Delete item
    cursor.execute("DELETE FROM billing_bill_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    
    # Update bill total
    if bill_id:
        update_bill_total(bill_id)

def update_bill_item(item_id, description, amount):
    """Update a bill item"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get bill_id
    cursor.execute("SELECT bill_id FROM billing_bill_items WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    bill_id = result[0] if result else None
    
    # Update item
    cursor.execute("""
        UPDATE billing_bill_items
        SET description = ?, amount = ?
        WHERE id = ?
    """, (description, amount, item_id))
    
    conn.commit()
    conn.close()
    
    # Update bill total
    if bill_id:
        update_bill_total(bill_id)

# ==================== CALCULATIONS ====================

def update_bill_total(bill_id):
    """Calculate and update total amount for a bill"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Sum all items
    cursor.execute("""
        SELECT SUM(amount) FROM billing_bill_items WHERE bill_id = ?
    """, (bill_id,))
    
    result = cursor.fetchone()
    total = result[0] if result[0] else 0
    
    # Update bill total
    cursor.execute("""
        UPDATE billing_bills SET total_amount = ? WHERE id = ?
    """, (total, bill_id))
    
    conn.commit()
    conn.close()

def get_billing_dashboard_stats():
    """Get billing statistics for admin dashboard"""
    init_billing_tables()  # Ensure tables exist
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Total bills
    cursor.execute("SELECT COUNT(*) FROM billing_bills")
    total_bills = cursor.fetchone()[0]
    
    # Paid bills
    cursor.execute("SELECT COUNT(*) FROM billing_bills WHERE status = 'Paid'")
    paid_bills = cursor.fetchone()[0]
    
    # Unpaid bills
    cursor.execute("SELECT COUNT(*) FROM billing_bills WHERE status = 'Unpaid'")
    unpaid_bills = cursor.fetchone()[0]
    
    # Total revenue
    cursor.execute("SELECT SUM(total_amount) FROM billing_bills WHERE status = 'Paid'")
    result = cursor.fetchone()
    total_revenue = result[0] if result[0] else 0
    
    # Pending amount
    cursor.execute("SELECT SUM(total_amount) FROM billing_bills WHERE status = 'Unpaid'")
    result = cursor.fetchone()
    pending_amount = result[0] if result[0] else 0
    
    conn.close()
    
    return {
        'total_bills': total_bills,
        'paid_bills': paid_bills,
        'unpaid_bills': unpaid_bills,
        'total_revenue': round(total_revenue, 2),
        'pending_amount': round(pending_amount, 2)
    }


def get_bills_by_patient(patient_id):
    """Get bills for a specific patient"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.bill_id, p.name, b.amount, b.payment_status, b.date
        FROM billing b
        JOIN patients p ON b.patient_id = p.patient_id
        WHERE b.patient_id = ?
    """, (patient_id,))

    data = cursor.fetchall()
    conn.close()
    return data


def get_bills_by_user(user_id):
    """Get bills for patients associated with a specific user"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.bill_id, p.name, b.amount, b.payment_status, b.date
        FROM billing b
        JOIN patients p ON b.patient_id = p.patient_id
        WHERE p.user_id = ?
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data


def get_bill_patient_user_id(bill_id):
    """Get the user_id for the patient associated with a specific bill."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.user_id
        FROM billing b
        JOIN patients p ON b.patient_id = p.patient_id
        WHERE b.bill_id = ?
    """, (bill_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None