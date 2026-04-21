"""Database connection and management utilities"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

def close_db(e=None):
    """Close database connection"""
    pass
