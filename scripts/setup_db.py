# scripts/setup_db.py
import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import logging
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('setup')

def print_colored(message, color=Fore.WHITE):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.BLUE}{timestamp}{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")

def setup_database():
    """Initialize the database with required tables"""
    try:
        # Connect to SQLite database (creates it if it doesn't exist)
        conn = sqlite3.connect('transactions.db')
        c = conn.cursor()

        print_colored("Creating database tables...", Fore.YELLOW)

        # Create user_accounts table
        c.execute('''
        CREATE TABLE IF NOT EXISTS user_accounts
        (phone_text TEXT PRIMARY KEY, 
         public_key TEXT,
         secret_key TEXT,
         created_at TEXT)
        ''')
        print_colored("Created user_accounts table", Fore.GREEN)

        # Create transactions table
        c.execute('''
        CREATE TABLE IF NOT EXISTS transactions
        (phone_text TEXT,
         moneygram_ref TEXT PRIMARY KEY, 
         amount REAL,
         status TEXT,
         created_at TEXT,
         stellar_tx_id TEXT)
        ''')
        print_colored("Created transactions table", Fore.GREEN)

        # Create indexes for better performance
        c.execute('''
        CREATE INDEX IF NOT EXISTS idx_phone_text 
        ON transactions(phone_text)
        ''')
        
        c.execute('''
        CREATE INDEX IF NOT EXISTS idx_status 
        ON transactions(status)
        ''')
        print_colored("Created database indexes", Fore.GREEN)

        # Commit changes and close connection
        conn.commit()
        conn.close()

        print_colored("\nDatabase initialization complete!", Fore.GREEN + Style.BRIGHT)
        print_colored("Tables created:", Fore.CYAN)
        print_colored("1. user_accounts - Stores user Stellar accounts", Fore.CYAN)
        print_colored("2. transactions - Stores transaction history", Fore.CYAN)
        
        return True

    except Exception as e:
        print_colored(f"Error setting up database: {str(e)}", Fore.RED)
        return False

if __name__ == "__main__":
    print_colored("\nStarting database setup...", Fore.YELLOW + Style.BRIGHT)
    print_colored("=" * 50, Fore.YELLOW)
    
    if setup_database():
        print_colored("=" * 50, Fore.GREEN)
        print_colored("Database setup completed successfully!", Fore.GREEN + Style.BRIGHT)
        sys.exit(0)
    else:
        print_colored("=" * 50, Fore.RED)
        print_colored("Database setup failed!", Fore.RED + Style.BRIGHT)
        sys.exit(1)