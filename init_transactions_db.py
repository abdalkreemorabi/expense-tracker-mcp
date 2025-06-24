import sqlite3
import os
from datetime import datetime

def init_database():
    db_path = os.path.join(os.path.dirname(__file__), 'transactions.db')
    
    # Remove the database if it already exists for a clean start
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database for clean initialization.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create expenses table
    cursor.execute('''
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            notes TEXT,
            currency TEXT DEFAULT 'USD',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Create category_limits table
    cursor.execute('''
        CREATE TABLE category_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE,
            limit_amount REAL NOT NULL,
            limit_type TEXT NOT NULL CHECK (limit_type IN ('daily', 'weekly', 'monthly')),
            currency TEXT DEFAULT 'USD',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

    print("Database initialized successfully with:")
    print("- expenses table (id, category, amount, notes, currency, created_at, updated_at)")
    print("- category_limits table (id, category, limit_amount, limit_type, currency, created_at, updated_at)")

if __name__ == "__main__":
    init_database() 