import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "hospital.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)
               """)
# ------------------ PATIENT TABLE ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    contact TEXT,
    address TEXT,
    medical_history TEXT
)
""")

# ------------------ DOCTOR TABLE ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialization TEXT,
    contact TEXT,
    availability TEXT
)
""")

# ------------------ APPOINTMENT TABLE ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    date TEXT,
    time TEXT,
    status TEXT,
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ehr (
    ehr_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    diagnosis TEXT,
    treatment_plan TEXT,
    medications TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS billing (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    amount REAL,
    payment_status TEXT,
    date TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pharmacy (
    medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    stock INTEGER,
    price REAL,
    expiry_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS lab_tests (
    test_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    test_type TEXT,
    result TEXT,
    status TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
)
""")

# ------------------ LAB TEST TYPES TABLE ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS lab_test_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL,
    description TEXT,
    parameters TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ------------------ TEST BOOKINGS TABLE ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS test_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    test_id INTEGER NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME,
    status TEXT DEFAULT 'Pending',
    prescription_file TEXT,
    report_file TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (test_id) REFERENCES lab_test_types(id)
)
""")

# ------------------ MEDICINES TABLE ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    generic_name VARCHAR(120),
    description TEXT,
    price FLOAT NOT NULL,
    quantity_in_stock INTEGER DEFAULT 0,
    expiry_date DATE,
    manufacturer VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ------------------ PRESCRIPTIONS TABLE ------------------
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

# ------------------ PRESCRIPTION ITEMS TABLE ------------------
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

# ------------------ SALES TABLE ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
)
""")

# ------------------ SALE ITEMS TABLE ------------------
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

# ------------------ BILLS TABLE (UPDATED) ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    appointment_id INTEGER,
    amount FLOAT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    payment_date DATETIME,
    bill_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
)
""")

# ------------------ EHR TABLE (UPDATED) ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS ehr (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_id INTEGER,
    diagnosis TEXT NOT NULL,
    treatment_plan TEXT,
    medications TEXT,
    vital_signs TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
)
""")

# ------------------ USERS TABLE (UPDATED) ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ------------------ PATIENTS TABLE (UPDATED) ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    age INTEGER,
    gender TEXT,
    contact TEXT,
    address TEXT,
    medical_history TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

# ------------------ DOCTORS TABLE (UPDATED) ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    specialization TEXT,
    contact TEXT,
    availability TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

# ------------------ APPOINTMENTS TABLE (UPDATED) ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    date TEXT,
    time TEXT,
    status TEXT,
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ All tables created successfully!")