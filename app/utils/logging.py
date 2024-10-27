# app/utils/logging.py
from datetime import datetime
from colorama import Fore, Style

def log_transaction(logger, transaction, event_type="INFO"):
    """Log transaction details"""
    logger.info(f"""
Transaction Details [{event_type}]:
Reference: {transaction.ref}
Amount: {transaction.amount} USDC
Status: {transaction.status}
Phone: {transaction.phone_number}
Created: {format_date(transaction.created_at)}
Stellar TX: {transaction.stellar_tx_id or 'None'}
{'='*50}
""")

def log_user(logger, user, event_type="INFO"):
    """Log user details"""
    logger.info(f"""
User Details [{event_type}]:
Phone: {user.phone_number}
Public Key: {user.public_key}
Created: {format_date(user.created_at)}
{'='*50}
""")

def format_date(date_str):
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_str