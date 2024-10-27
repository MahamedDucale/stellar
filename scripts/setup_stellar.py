# scripts/setup_stellar.py
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

# Configuration
STELLAR_SERVER_URL = "https://horizon-testnet.stellar.org"
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
USDC_ISSUER = "GBBD47IF6LWK7P7MDEVSCWR7DPUWV3NY3DTQEVFL4NAT4AQH3ZLLFLA5"
DISTRIBUTION_SECRET_KEY = os.getenv("DISTRIBUTION")

def print_colored(message, color=Fore.WHITE, style=Style.NORMAL):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.BLUE}{timestamp}{Style.RESET_ALL} {color}{style}{message}{Style.RESET_ALL}")

def create_distribution_account():
    """Create and fund a new distribution account"""
    try:
        # Create new keypair
        keypair = Keypair.random()
        print_colored(f"\nCreated new distribution account:", Fore.GREEN)
        print_colored(f"Public Key: {keypair.public_key}", Fore.CYAN)
        print_colored(f"Secret Key: {keypair.secret}", Fore.YELLOW)

        # Fund account with friendbot
        print_colored("\nFunding account with test XLM...", Fore.YELLOW)
        response = requests.get(
            f'https://friendbot.stellar.org?addr={keypair.public_key}'
        )
        response.raise_for_status()
        print_colored("Account funded with test XLM!", Fore.GREEN)

        # Wait for account creation to be confirmed
        time.sleep(5)
        
        # Setup USDC trustline
        server = Server(STELLAR_SERVER_URL)
        account = server.load_account(keypair.public_key)
        usdc_asset = Asset("USDC", USDC_ISSUER)

        print_colored("\nSetting up USDC trustline...", Fore.YELLOW)
        transaction = (
            TransactionBuilder(
                source_account=account,
                network_passphrase=NETWORK_PASSPHRASE,
                base_fee=100)
            .append_change_trust_op(
                asset=usdc_asset,
                limit="1000000")
            .set_timeout(30)
            .build()
        )

        transaction.sign(keypair)
        response = server.submit_transaction(transaction)
        print_colored("USDC trustline established!", Fore.GREEN)

        print_colored("\nSAVE THESE DETAILS:", Fore.RED + Style.BRIGHT)
        print_colored("Add this line to your .env file:", Fore.RED)
        print_colored(f"DISTRIBUTION={keypair.secret}", Fore.RED)
        
        print_colored("\nTo get test USDC:", Fore.CYAN)
        print_colored("1. Go to: https://laboratory.stellar.org", Fore.CYAN)
        print_colored("2. Switch to 'Test Network'", Fore.CYAN)
        print_colored("3. Go to 'Transaction Builder'", Fore.CYAN)
        print_colored("4. Set Source Account to the USDC issuer", Fore.CYAN)
        print_colored("5. Add a Payment operation:", Fore.CYAN)
        print_colored(f"   - Destination: {keypair.public_key}", Fore.CYAN)
        print_colored("   - Asset: USDC", Fore.CYAN)
        print_colored(f"   - Issuer: {USDC_ISSUER}", Fore.CYAN)
        print_colored("   - Amount: 10000", Fore.CYAN)

        return keypair

    except Exception as e:
        print_colored(f"Error creating distribution account: {str(e)}", Fore.RED)
        return None

def check_existing_account():
    """Check existing distribution account status"""
    try:
        if not DISTRIBUTION_SECRET_KEY:
            print_colored("No distribution account found in .env", Fore.YELLOW)
            return False

        server = Server(STELLAR_SERVER_URL)
        distribution_keypair = Keypair.from_secret(DISTRIBUTION_SECRET_KEY)
        
        print_colored("\nChecking existing distribution account...", Fore.YELLOW)
        print_colored(f"Public Key: {distribution_keypair.public_key}", Fore.CYAN)

        # Get account details
        account = server.accounts().account_id(distribution_keypair.public_key).call()
        
        xlm_balance = "0"
        usdc_balance = "0"
        has_trustline = False

        for balance in account['balances']:
            if balance['asset_type'] == 'native':
                xlm_balance = balance['balance']
            elif (balance['asset_type'] == 'credit_alphanum4' and 
                  balance['asset_code'] == 'USDC' and 
                  balance['asset_issuer'] == USDC_ISSUER):
                usdc_balance = balance['balance']
                has_trustline = True

        print_colored("\nAccount Status:", Fore.GREEN)
        print_colored(f"XLM Balance: {xlm_balance}", Fore.GREEN)
        print_colored(f"USDC Balance: {usdc_balance}", Fore.GREEN)
        print_colored(f"Has USDC Trustline: {has_trustline}", Fore.GREEN)

        if float(xlm_balance) < 5:
            print_colored("\nWarning: Low XLM balance", Fore.RED)
        if float(usdc_balance) < 100:
            print_colored("Warning: Low USDC balance", Fore.RED)
        if not has_trustline:
            print_colored("Warning: No USDC trustline", Fore.RED)

        return True

    except Exception as e:
        print_colored(f"Error checking distribution account: {str(e)}", Fore.RED)
        return False

def setup_stellar():
    """Main setup function"""
    print_colored("\nStellar Setup", Fore.CYAN + Style.BRIGHT)
    print_colored("=" * 50, Fore.CYAN)

    # Check existing account first
    if not check_existing_account():
        print_colored("\nCreating new distribution account...", Fore.YELLOW)
        keypair = create_distribution_account()
        if not keypair:
            return False

    print_colored("\nSetup complete!", Fore.GREEN + Style.BRIGHT)
    return True

if __name__ == "__main__":
    if setup_stellar():
        print_colored("=" * 50, Fore.GREEN)
        print_colored("Stellar setup completed successfully!", Fore.GREEN + Style.BRIGHT)
        sys.exit(0)
    else:
        print_colored("=" * 50, Fore.RED)
        print_colored("Stellar setup failed!", Fore.RED + Style.BRIGHT)
        sys.exit(1)