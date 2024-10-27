# app/database/db.py
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect('transactions.db')
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_accounts
            (phone_text TEXT PRIMARY KEY, 
             public_key TEXT,
             secret_key TEXT,
             created_at TEXT)
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions
            (phone_text TEXT, 
             moneygram_ref TEXT PRIMARY KEY, 
             amount REAL, 
             status TEXT, 
             created_at TEXT,
             stellar_tx_id TEXT)
        ''')
        conn.commit()