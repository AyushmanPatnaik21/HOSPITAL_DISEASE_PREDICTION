-- Hospital Management System Database Schema

-- Users Table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients Table
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    age INTEGER,
    gender TEXT,
    contact TEXT,
    address TEXT,
    medical_history TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Doctors Table
CREATE TABLE doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    specialization TEXT,
    contact TEXT,
    availability TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Appointments Table
CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    date TEXT,
    time TEXT,
    status TEXT,
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- EHR Table
CREATE TABLE ehr (
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
);

-- Bills Table
CREATE TABLE bills (
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
);

-- Medicines Table
CREATE TABLE medicines (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    generic_name VARCHAR(120),
    description TEXT,
    price FLOAT NOT NULL,
    quantity_in_stock INTEGER DEFAULT 0,
    expiry_date DATE,
    manufacturer VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Lab Tests Table
CREATE TABLE lab_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    test_name TEXT NOT NULL,
    test_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    result TEXT,
    notes TEXT,
    test_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    result_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- Lab Test Types Table (Available tests that can be booked)
CREATE TABLE lab_test_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test Bookings Table (Patient bookings for lab tests)
CREATE TABLE test_bookings (
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
);



-- Create indexes for better performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_doctors_user_id ON doctors(user_id);
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX idx_ehr_patient_id ON ehr(patient_id);
CREATE INDEX idx_bills_patient_id ON bills(patient_id);
CREATE INDEX idx_lab_tests_patient_id ON lab_tests(patient_id);
CREATE INDEX idx_lab_test_types_name ON lab_test_types(test_name);
CREATE INDEX idx_test_bookings_patient_id ON test_bookings(patient_id);
CREATE INDEX idx_test_bookings_test_id ON test_bookings(test_id);
CREATE INDEX idx_test_bookings_status ON test_bookings(status);


