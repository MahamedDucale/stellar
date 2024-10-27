# app/models/transaction.py
from datetime import datetime
from app.database.db import get_db

class Transaction:
    def __init__(self, phone_number, ref, amount, usd_amount=None, status='pending', created_at=None, stellar_tx_id=None):
        self.phone_number = phone_number
        self.ref = ref
        self.amount = amount
        self.usd_amount = usd_amount
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.stellar_tx_id = stellar_tx_id

    def save(self):
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO transactions 
                (phone_text, moneygram_ref, amount, usd_amount, status, created_at, stellar_tx_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.phone_number, self.ref, self.amount, self.usd_amount,
                  self.status, self.created_at, self.stellar_tx_id))
            conn.commit()

    @classmethod
    def get_by_ref(cls, ref):
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT phone_text, moneygram_ref, amount, usd_amount, status, created_at, stellar_tx_id 
                FROM transactions 
                WHERE moneygram_ref = ?
            ''', (ref,))
            row = c.fetchone()
            if row:
                return cls(
                    phone_number=row[0],
                    ref=row[1],
                    amount=row[2],
                    usd_amount=row[3],
                    status=row[4],
                    created_at=row[5],
                    stellar_tx_id=row[6]
                )
            return None

    @classmethod
    def get_history(cls, phone_number, limit=5):
        with get_db() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT phone_text, moneygram_ref, amount, usd_amount, status, created_at, stellar_tx_id 
                FROM transactions 
                WHERE phone_text = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (phone_number, limit))
            return [cls(
                phone_number=row[0],
                ref=row[1],
                amount=row[2],
                usd_amount=row[3],
                status=row[4],
                created_at=row[5],
                stellar_tx_id=row[6]
            ) for row in c.fetchall()]