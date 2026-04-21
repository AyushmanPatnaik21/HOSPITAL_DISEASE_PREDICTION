import sqlite3
import os
from datetime import datetime


def get_db():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BASE_DIR, "database", "hospital.db")
    return sqlite3.connect(db_path)


def init_pharmacy_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity_in_stock INTEGER DEFAULT 0,
            expiry_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            notes TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescription_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            dosage TEXT NOT NULL,
            duration TEXT NOT NULL,
            FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    conn.commit()
    conn.close()


def add_medicine(name, price, quantity_in_stock, expiry_date=None):
    init_pharmacy_tables()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO medicines (name, price, quantity_in_stock, expiry_date)
        VALUES (?, ?, ?, ?)
    """, (name, price, quantity_in_stock, expiry_date))

    conn.commit()
    conn.close()


def get_all_medicines():
    init_pharmacy_tables()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price, quantity_in_stock, expiry_date FROM medicines ORDER BY name ASC"
    )
    data = cursor.fetchall()
    conn.close()
    return data


def get_medicine_by_id(medicine_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price, quantity_in_stock, expiry_date FROM medicines WHERE id = ?",
        (medicine_id,),
    )
    data = cursor.fetchone()
    conn.close()
    return data


def update_medicine(medicine_id, name, price, quantity_in_stock, expiry_date=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
            UPDATE medicines
            SET name = ?, price = ?, quantity_in_stock = ?, expiry_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
        (name, price, quantity_in_stock, expiry_date, medicine_id),
    )
    conn.commit()
    conn.close()


def delete_medicine(medicine_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
    conn.commit()
    conn.close()


def is_stock_available(medicine_id, quantity):
    medicine = get_medicine_by_id(medicine_id)
    return medicine and medicine[3] >= quantity


def decrement_stock(medicine_id, quantity):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
            UPDATE medicines
            SET quantity_in_stock = quantity_in_stock - ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
        (quantity, medicine_id),
    )
    conn.commit()
    conn.close()


def create_prescription(patient_id, doctor_id, notes=None):
    init_pharmacy_tables()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prescriptions (patient_id, doctor_id, notes) VALUES (?, ?, ?)",
        (patient_id, doctor_id, notes),
    )
    conn.commit()
    prescription_id = cursor.lastrowid
    conn.close()
    return prescription_id


def add_prescription_item(prescription_id, medicine_id, dosage, duration):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prescription_items (prescription_id, medicine_id, dosage, duration) VALUES (?, ?, ?, ?)",
        (prescription_id, medicine_id, dosage, duration),
    )
    conn.commit()
    conn.close()


def get_prescriptions_by_doctor(doctor_id):
    init_pharmacy_tables()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT pr.id, pr.patient_id, p.name, pr.notes, pr.date
        FROM prescriptions pr
        JOIN patients p ON pr.patient_id = p.patient_id
        WHERE pr.doctor_id = ?
        ORDER BY pr.date DESC
        """,
        (doctor_id,),
    )
    data = cursor.fetchall()
    conn.close()
    return data


def get_prescriptions_by_patient(patient_id):
    init_pharmacy_tables()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT pr.id, pr.doctor_id, d.name, pr.notes, pr.date
        FROM prescriptions pr
        JOIN doctors d ON pr.doctor_id = d.doctor_id
        WHERE pr.patient_id = ?
        ORDER BY pr.date DESC
        """,
        (patient_id,),
    )
    data = cursor.fetchall()
    conn.close()
    return data


def get_prescription_by_id(prescription_id):
    init_pharmacy_tables()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, patient_id, doctor_id, notes, date FROM prescriptions WHERE id = ?",
        (prescription_id,),
    )
    data = cursor.fetchone()
    conn.close()
    return data


def get_prescription_items(prescription_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT pi.id, pi.medicine_id, m.name, pi.dosage, pi.duration
        FROM prescription_items pi
        JOIN medicines m ON pi.medicine_id = m.id
        WHERE pi.prescription_id = ?
        """,
        (prescription_id,),
    )
    data = cursor.fetchall()
    conn.close()
    return data


def create_sale(patient_id, total_amount):
    init_pharmacy_tables()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sales (patient_id, total_amount) VALUES (?, ?)",
        (patient_id, total_amount),
    )
    conn.commit()
    sale_id = cursor.lastrowid
    conn.close()
    return sale_id


def add_sale_item(sale_id, medicine_id, quantity, price):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sale_items (sale_id, medicine_id, quantity, price) VALUES (?, ?, ?, ?)",
        (sale_id, medicine_id, quantity, price),
    )
    conn.commit()
    conn.close()


def get_sales():
    init_pharmacy_tables()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.id, s.patient_id, p.name, s.total_amount, s.date
        FROM sales s
        JOIN patients p ON s.patient_id = p.patient_id
        ORDER BY s.date DESC
        """
    )
    data = cursor.fetchall()
    conn.close()
    return data


def get_sales_by_patient(patient_id):
    init_pharmacy_tables()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, total_amount, date
        FROM sales
        WHERE patient_id = ?
        ORDER BY date DESC
        """,
        (patient_id,),
    )
    data = cursor.fetchall()
    conn.close()
    return data


def get_sale_by_id(sale_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, patient_id, total_amount, date FROM sales WHERE id = ?",
        (sale_id,),
    )
    data = cursor.fetchone()
    conn.close()
    return data


def get_sale_items(sale_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT si.id, si.medicine_id, m.name, si.quantity, si.price
        FROM sale_items si
        JOIN medicines m ON si.medicine_id = m.id
        WHERE si.sale_id = ?
        """,
        (sale_id,),
    )
    data = cursor.fetchall()
    conn.close()
    return data