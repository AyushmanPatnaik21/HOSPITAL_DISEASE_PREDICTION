"""Helper utility functions"""
from datetime import datetime
import os

def get_timestamp():
    """Get current timestamp"""
    return datetime.now()

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    import re
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_upload_directory():
    """Create upload directory if it doesn't exist"""
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
