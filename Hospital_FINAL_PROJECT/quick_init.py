#!/usr/bin/env python3
"""
Quick database initialization script.
Ensures lab_test_types table has parameters column.
Run this if you get: sqlite3.OperationalError: no such column: parameters
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models.lab_model import ensure_parameters_column

if __name__ == "__main__":
    print("Initializing Lab Test Database Schema...")
    print("=" * 60)
    ensure_parameters_column()
    print("=" * 60)
    print("✓ Database ready!")
    print("\nNext steps:")
    print("1. Restart Flask: python app.py")
    print("2. Go to Admin → Manage Test Bookings")
    print("3. Click Update on any booking")
