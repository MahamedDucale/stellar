# app/models/user.py
from datetime import datetime
from app.database.db import get_db

class User:
    def __init__(self, phone_number, public_key=None, secret_key=None, created_at=None):
        self.phone_number = phone_number
        self.public_key = public_key
        self.secret_key = secret_key
        self.created_at = created_at or datetime.now().isoformat()

    @classmethod
    def from_db_row(cls, row):
        """Create User object from database row"""
        if not row:
            return None
        return cls(
            phone_number=row[0],
            public_key=row[1],
            secret_key=row[2],
            created_at=row[3]
        )

    def save(self):
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO user_accounts 
                (phone_text, public_key, secret_key, created_at)
                VALUES (?, ?, ?, ?)
            ''', (self.phone_number, self.public_key, self.secret_key, self.created_at))
            conn.commit()

    @classmethod
    def get_by_phone(cls, phone_number):
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT phone_text, public_key, secret_key, created_at 
                FROM user_accounts 
                WHERE phone_text = ?
            ''', (phone_number,))
            row = c.fetchone()
            return cls.from_db_row(row) if row else None

    def to_dict(self):
        return {
            'phone_number': self.phone_number,
            'public_key': self.public_key,
            'created_at': self.created_at
        }