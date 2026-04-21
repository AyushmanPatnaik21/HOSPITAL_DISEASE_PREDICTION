import sqlite3

def get_db():
    return sqlite3.connect("database/hospital.db")


def create_user(name, email, password, role):
    conn = sqlite3.connect('database/hospital.db')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, password, role))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False   # email already exists

    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    conn.close()
    return user