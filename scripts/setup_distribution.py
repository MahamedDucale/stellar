# scripts/setup_distribution.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset
import requests
from datetime import datetime
import logging
from dotenv import load_dotenv
from colorama import init, Fore, Style
import time

# Initialize colorama
init()

# Load environment variables
load_dotenv()

# Use testnet configuration
STELLAR_SERVER_URL = "https://horizon-testnet.stellar.org"
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
GOLD_CODE = "GOLD"
GOLD_ISSUER = None  # Will be set after issuer creation
GOLD_DESCRIPTION = "Test Gold Token - Each token represents 1 gram of physical gold"

def print_colored(message, color=Fore.WHITE, style=Style.NORMAL):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.BLUE}{timestamp}{Style.RESET_ALL} {color}{style}{message}{Style.RESET_ALL}")

def create_gold_issuer():
    """Create and fund the gold token issuer account"""
    try:
        issuer_keypair = Keypair.random()
        print_colored("\nCreating Gold Token Issuer Account:", Fore.CYAN)
        print_colored(f"Issuer Public Key: {issuer_keypair.public_key}", Fore.YELLOW)
        print_colored(f"Issuer Secret Key: {issuer_keypair.secret}", Fore.RED)

        # Fund issuer account with friendbot
        print_colored("\nFunding issuer account with friendbot...", Fore.YELLOW)
        response = requests.get(
            f'https://friendbot.stellar.org?addr={issuer_keypair.public_key}'
        )
        response.raise_for_status()
        print_colored("Issuer account funded successfully!", Fore.GREEN)

        return issuer_keypair
    except Exception as e:
        print_colored(f"Error creating issuer account: {str(e)}", Fore.RED)
        return None

def setup_distribution_account(issuer_keypair):
    """Setup distribution account with Gold token trustline"""
    try:
        print_colored(f"\nSetting up distribution account for {GOLD_CODE} tokens", Fore.CYAN)
        
        # Create distribution account
        distribution_keypair = Keypair.random()
        print_colored("\nCreated distribution account:", Fore.GREEN)
        print_colored(f"Public Key: {distribution_keypair.public_key}", Fore.YELLOW)
        print_colored(f"Secret Key: {distribution_keypair.secret}", Fore.RED)
        
        # Fund with friendbot
        print_colored("\nFunding distribution account with friendbot...", Fore.YELLOW)
        response = requests.get(
            f'https://friendbot.stellar.org?addr={distribution_keypair.public_key}'
        )
        response.raise_for_status()
        print_colored("Distribution account funded with 10,000 test XLM!", Fore.GREEN)

        # Wait for account creation
        time.sleep(5)
        server = Server(STELLAR_SERVER_URL)

        # Setup trustline
        print_colored(f"\nSetting up {GOLD_CODE} trustline...", Fore.YELLOW)
        account = server.load_account(distribution_keypair.public_key)
        gold_asset = Asset(GOLD_CODE, issuer_keypair.public_key)
        
        transaction = (
            TransactionBuilder(
                source_account=account,
                network_passphrase=NETWORK_PASSPHRASE,
                base_fee=100)
            .append_change_trust_op(
                asset=gold_asset,
                limit="1000000")
            .set_timeout(30)
            .build()
        )
        
        transaction.sign(distribution_keypair)
        response = server.submit_transaction(transaction)
        print_colored("Trustline established!", Fore.GREEN)

        # Send initial test gold tokens from issuer to distribution account
        print_colored("\nSending initial test gold tokens...", Fore.YELLOW)
        issuer_account = server.load_account(issuer_keypair.public_key)
        transaction = (
            TransactionBuilder(
                source_account=issuer_account,
                network_passphrase=NETWORK_PASSPHRASE,
                base_fee=100)
            .append_payment_op(
                destination=distribution_keypair.public_key,
                asset=gold_asset,
                amount="1000")  # Start with 1000 test gold tokens
            .set_timeout(30)
            .build()
        )
        
        transaction.sign(issuer_keypair)
        response = server.submit_transaction(transaction)
        print_colored("Initial gold tokens sent successfully!", Fore.GREEN)
        
        print_colored("\nNext steps:", Fore.CYAN, Style.BRIGHT)
        print_colored("1. Add these lines to your .env file:", Fore.CYAN)
        print_colored("DISTRIBUTION=" + distribution_keypair.secret, Fore.RED)
        print_colored("GOLD_ISSUER=" + issuer_keypair.public_key, Fore.RED)
        
        # Print summary
        print_colored("\nAccount Summary:", Fore.GREEN, Style.BRIGHT)
        print_colored(f"Network: Testnet", Fore.GREEN)
        print_colored(f"Gold Token Code: {GOLD_CODE}", Fore.GREEN)
        print_colored(f"Distribution Account: {distribution_keypair.public_key}", Fore.GREEN)
        print_colored(f"Initial Balance: 1000 {GOLD_CODE} tokens", Fore.GREEN)
        print_colored(f"XLM Balance: 10,000 XLM", Fore.GREEN)
        
        return True
    except Exception as e:
        print_colored(f"\nError setting up distribution account: {str(e)}", Fore.RED)
        return False

if __name__ == "__main__":
    print_colored("\nStellar Test Gold Token Setup", Fore.CYAN + Style.BRIGHT)
    print_colored("=" * 50, Fore.CYAN)
    
    # Create issuer first
    issuer_keypair = create_gold_issuer()
    if not issuer_keypair:
        print_colored("Failed to create issuer account!", Fore.RED + Style.BRIGHT)
        sys.exit(1)

    # Then setup distribution account
    if setup_distribution_account(issuer_keypair):
        print_colored("=" * 50, Fore.GREEN)
        print_colored("Setup completed successfully!", Fore.GREEN + Style.BRIGHT)
        sys.exit(0)
    else:
        print_colored("=" * 50, Fore.RED)
        print_colored("Setup failed!", Fore.RED + Style.BRIGHT)
        sys.exit(1)