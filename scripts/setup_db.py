# scripts/setup_db.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import logging
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
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

        # Drop existing tables if they exist
        print_colored("Dropping existing tables...", Fore.YELLOW)
        c.execute('DROP TABLE IF EXISTS transactions')
        c.execute('DROP TABLE IF EXISTS user_accounts')

        # Create user_accounts table
        print_colored("Creating user_accounts table...", Fore.YELLOW)
        c.execute('''
        CREATE TABLE IF NOT EXISTS user_accounts
        (phone_text TEXT PRIMARY KEY, 
         public_key TEXT NOT NULL,
         secret_key TEXT NOT NULL,
         created_at TEXT NOT NULL)
        ''')
        print_colored("Created user_accounts table", Fore.GREEN)

        # Create transactions table with usd_amount column
        print_colored("Creating transactions table...", Fore.YELLOW)
        c.execute('''
        CREATE TABLE IF NOT EXISTS transactions
        (phone_text TEXT NOT NULL,
         moneygram_ref TEXT PRIMARY KEY, 
         amount REAL NOT NULL,
         usd_amount REAL NOT NULL,
         status TEXT NOT NULL,
         created_at TEXT NOT NULL,
         stellar_tx_id TEXT,
         FOREIGN KEY (phone_text) REFERENCES user_accounts(phone_text))
        ''')
        print_colored("Created transactions table", Fore.GREEN)

        # Create indexes for better performance
        print_colored("Creating indexes...", Fore.YELLOW)
        
        c.execute('''
        CREATE INDEX IF NOT EXISTS idx_transactions_phone 
        ON transactions(phone_text)
        ''')
        
        c.execute('''
        CREATE INDEX IF NOT EXISTS idx_transactions_status 
        ON transactions(status)
        ''')
        
        c.execute('''
        CREATE INDEX IF NOT EXISTS idx_transactions_created 
        ON transactions(created_at)
        ''')

        print_colored("Created database indexes", Fore.GREEN)

        # Commit changes and close connection
        conn.commit()

        print_colored("\nDatabase schema:", Fore.CYAN)
        # Show the schema of each table
        for table in ['user_accounts', 'transactions']:
            c.execute(f"PRAGMA table_info({table})")
            columns = c.fetchall()
            print_colored(f"\nTable: {table}", Fore.CYAN)
            for col in columns:
                print_colored(f"  {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}", Fore.WHITE)

        conn.close()
        
        print_colored("\nDatabase initialization complete!", Fore.GREEN + Style.BRIGHT)
        
        return True

    except Exception as e:
        print_colored(f"Error setting up database: {str(e)}", Fore.RED)
        return False

if __name__ == "__main__":
    print_colored("\nStarting database setup...", Fore.YELLOW + Style.BRIGHT)
    print_colored("=" * 50, Fore.YELLOW)
    
    # Delete existing database file
    if os.path.exists('transactions.db'):
        print_colored("Removing existing database...", Fore.YELLOW)
        os.remove('transactions.db')
        print_colored("Existing database removed", Fore.GREEN)
    
    if setup_database():
        print_colored("=" * 50, Fore.GREEN)
        print_colored("Database setup completed successfully!", Fore.GREEN + Style.BRIGHT)
        sys.exit(0)
    else:
        print_colored("=" * 50, Fore.RED)
        print_colored("Database setup failed!", Fore.RED + Style.BRIGHT)
        sys.exit(1)