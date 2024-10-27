# app/services/stellar.py
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset
import logging
import requests
from config.settings import (
    STELLAR_SERVER_URL, 
    NETWORK_PASSPHRASE, 
    GOLD_ISSUER,
    GOLD_CODE,
    DISTRIBUTION_SECRET_KEY
)

logger = logging.getLogger('sms_crypto')

class StellarService:
    def __init__(self):
        self.server = Server(STELLAR_SERVER_URL)
        self.gold_asset = self.create_gold_asset()

    def create_gold_asset(self):
        """Create Gold token asset"""
        return Asset(GOLD_CODE, GOLD_ISSUER)

    def format_stellar_key(self, key, show_full=False):
        """Format Stellar public/secret key for display"""
        if not key:
            return "None"
        if show_full:
            return key
        return f"{key[:4]}...{key[-4:]}"

    def create_account(self):
        """Create new Stellar account"""
        keypair = Keypair.random()
        logger.info(f"Created new Stellar account: {self.format_stellar_key(keypair.public_key)}")
        
        try:
            response = requests.get(
                f'https://friendbot.stellar.org?addr={keypair.public_key}'
            )
            response.raise_for_status()
            logger.info("Account funded with test XLM")
            
            return keypair
        except Exception as e:
            logger.error(f"Error funding account: {str(e)}")
            raise

    def setup_trustline(self, secret_key):
        """Setup Gold token trustline"""
        try:
            keypair = Keypair.from_secret(secret_key)
            account = self.server.load_account(keypair.public_key)
            
            transaction = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=NETWORK_PASSPHRASE,
                    base_fee=100)
                .append_change_trust_op(
                    asset=self.gold_asset,
                    limit="1000000")  # Maximum gold tokens
                .build()
            )
            
            transaction.sign(keypair)
            response = self.server.submit_transaction(transaction)
            logger.info(f"Gold token trustline established: {self.format_stellar_key(response['hash'])}")
            
            return True, response['hash']
        except Exception as e:
            logger.error(f"Trustline error: {str(e)}")
            return False, str(e)

    def send_gold(self, destination_account, amount):
        """Send Gold tokens"""
        try:
            distribution_keypair = Keypair.from_secret(DISTRIBUTION_SECRET_KEY)
            account = self.server.load_account(distribution_keypair.public_key)
            
            transaction = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=NETWORK_PASSPHRASE,
                    base_fee=100)
                .append_payment_op(
                    destination=destination_account,
                    asset=self.gold_asset,
                    amount=str(amount))
                .build()
            )
            
            transaction.sign(distribution_keypair)
            response = self.server.submit_transaction(transaction)
            logger.info(f"Gold tokens sent: {self.format_stellar_key(response['hash'])}")
            
            return True, response['hash']
        except Exception as e:
            logger.error(f"Payment error: {str(e)}")
            return False, str(e)

    def get_balances(self, public_key):
        """Get account balances"""
        try:
            account = self.server.accounts().account_id(public_key).call()
            
            balances = {
                'XLM': '0',
                'GOLD': '0'
            }
            
            for balance in account['balances']:
                if balance['asset_type'] == 'native':
                    balances['XLM'] = balance['balance']
                elif (balance['asset_type'] == 'credit_alphanum4' and 
                      balance['asset_code'] == GOLD_CODE and 
                      balance['asset_issuer'] == GOLD_ISSUER):
                    balances['GOLD'] = balance['balance']
                    
            return True, balances
        except Exception as e:
            logger.error(f"Balance check error: {str(e)}")
            return False, str(e)

    def calculate_gold_amount(self, usd_amount):
        """Calculate gold amount from USD"""
        from config.settings import GOLD_PRICE_USD
        return round(usd_amount / GOLD_PRICE_USD, 6)  # 6 decimal places