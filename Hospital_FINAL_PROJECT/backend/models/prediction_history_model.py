import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

# Determine project root and database path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DB_DIR, 'hospital.db')

def get_db_connection():
    """Get database connection"""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_prediction_history_table():
    """Create prediction history table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symptoms TEXT NOT NULL,
            predicted_disease TEXT NOT NULL,
            confidence REAL NOT NULL,
            severity TEXT NOT NULL,
            recommended_doctor TEXT NOT NULL,
            precautions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

def save_prediction_history(user_id: int, prediction_data: Dict) -> bool:
    """Save prediction to history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO prediction_history
            (user_id, symptoms, predicted_disease, confidence, severity, recommended_doctor, precautions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            ', '.join(prediction_data['input_symptoms']),
            prediction_data['disease'],
            prediction_data['confidence'],
            prediction_data['severity'],
            prediction_data['recommended_doctor'],
            prediction_data.get('precautions', '')
        ))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error saving prediction history: {e}")
        return False

def get_user_prediction_history(user_id: int, limit: int = 50) -> List[Dict]:
    """Get prediction history for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM prediction_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                'id': row['id'],
                'symptoms': row['symptoms'],
                'predicted_disease': row['predicted_disease'],
                'confidence': row['confidence'],
                'severity': row['severity'],
                'recommended_doctor': row['recommended_doctor'],
                'precautions': row['precautions'],
                'created_at': row['created_at']
            })

        return history

    except Exception as e:
        print(f"Error retrieving prediction history: {e}")
        return []

def get_prediction_analytics() -> Dict:
    """Get analytics for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total predictions
        cursor.execute('SELECT COUNT(*) as total FROM prediction_history')
        total_predictions = cursor.fetchone()['total']

        # Most common diseases
        cursor.execute('''
            SELECT predicted_disease, COUNT(*) as count
            FROM prediction_history
            GROUP BY predicted_disease
            ORDER BY count DESC
            LIMIT 5
        ''')
        common_diseases = cursor.fetchall()

        # Severity distribution
        cursor.execute('''
            SELECT severity, COUNT(*) as count
            FROM prediction_history
            GROUP BY severity
        ''')
        severity_stats = cursor.fetchall()

        # Recent predictions (last 30 days)
        cursor.execute('''
            SELECT COUNT(*) as recent
            FROM prediction_history
            WHERE created_at >= datetime('now', '-30 days')
        ''')
        recent_predictions = cursor.fetchone()['recent']

        conn.close()

        return {
            'total_predictions': total_predictions,
            'common_diseases': [{'disease': row['predicted_disease'], 'count': row['count']} for row in common_diseases],
            'severity_distribution': [{'severity': row['severity'], 'count': row['count']} for row in severity_stats],
            'recent_predictions': recent_predictions
        }

    except Exception as e:
        print(f"Error getting analytics: {e}")
        return {
            'total_predictions': 0,
            'common_diseases': [],
            'severity_distribution': [],
            'recent_predictions': 0
        }

# Note: create_prediction_history_table() is not invoked automatically to avoid startup failures.
# Call create_prediction_history_table() from app startup after environment is initialized.