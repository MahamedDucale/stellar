# app/services/sms.py
import logging
from datetime import datetime
import uuid
from app.models.user import User
from app.models.transaction import Transaction
from app.services.stellar import StellarService
from app.services.payment import PaymentService
from config.settings import (
    GOLD_CODE,
    GOLD_UNIT,
    GOLD_ISSUER
)

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.stellar = StellarService()
        self.payment = PaymentService()
        self.gold_price = 60  # Fixed price for testing

    def handle_message(self, phone_number, message):
        """Main message handler"""
        try:
            message = message.lower().strip()
            parts = message.split()

            if not parts:
                return None

            command = parts[0]
            logger.info(f"Processing command: {command} from {phone_number}")

            commands = {
                'buy': lambda: self.handle_buy(phone_number, parts[1] if len(parts) > 1 else None),
                'confirm': lambda: self.handle_confirm(phone_number, parts[1] if len(parts) > 1 else None),
                'balance': lambda: self.handle_balance(phone_number),
                'history': lambda: self.handle_history(phone_number),
                'account': lambda: self.handle_account(phone_number)
            }

            handler = commands.get(command)
            return handler() if handler else None

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return "An error occurred. Please try again."

    def generate_reference(self):
        return f"MG-{uuid.uuid4().hex[:8].upper()}"

    def handle_buy(self, phone_number, amount_str):
        if not amount_str:
            return "Invalid format. Use: buy <amount in USD>"

        try:
            usd_amount = float(amount_str)
            if usd_amount <= 0:
                return "Amount must be greater than 0"

            gold_amount = round(usd_amount / self.gold_price, 6)
            reference = self.generate_reference()

            transaction = Transaction(
                phone_number=phone_number,
                ref=reference,
                amount=gold_amount,
                usd_amount=usd_amount
            )
            transaction.save()

            return (
                f"Please deposit ${usd_amount:.2f} at MoneyGram using reference: {reference}\n"
                f"This will buy you {gold_amount} {GOLD_UNIT}s of Gold tokens\n"
                f"After depositing, send: confirm {reference}"
            )

        except ValueError:
            return "Invalid amount. Please enter a number."

    def handle_confirm(self, phone_number, reference):
        if not reference:
            return "Invalid format. Use: confirm <reference>"

        try:
            reference = reference.upper()
            
            transaction = Transaction.get_by_ref(reference)
            if not transaction:
                return "Reference number not found."

            if transaction.status != 'pending':
                return f"Transaction already {transaction.status}."

            # Get or create user's Stellar account
            user = User.get_by_phone(phone_number)
            if not user:
                keypair = self.stellar.create_account()
                user = User(
                    phone_number=phone_number,
                    public_key=keypair.public_key,
                    secret_key=keypair.secret
                )
                user.save()

            # Setup trustline and send tokens
            trustline_ok, trustline_msg = self.stellar.setup_trustline(user.secret_key)
            if not trustline_ok:
                return f"Error setting up Gold tokens: {trustline_msg}"

            send_ok, tx_hash = self.stellar.send_gold(user.public_key, transaction.amount)
            if not send_ok:
                return f"Error sending Gold tokens: {tx_hash}"

            transaction.status = 'completed'
            transaction.stellar_tx_id = tx_hash
            transaction.save()

            return (
                f"Successfully purchased {transaction.amount} {GOLD_UNIT}s of Gold tokens!\n"
                f"Value: ${transaction.usd_amount:.2f}"
            )

        except Exception as e:
            logger.error(f"Error confirming transaction: {str(e)}")
            return "Error processing confirmation. Please try again."

    def handle_balance(self, phone_number):
        try:
            user = User.get_by_phone(phone_number)
            if not user:
                return "No account found. Buy Gold tokens first."

            success, balances = self.stellar.get_balances(user.public_key)
            if not success:
                return f"Error checking balance: {balances}"

            gold_balance = float(balances.get('GOLD', 0))
            usd_value = gold_balance * self.gold_price

            return (
                f"Your Gold Token Balance:\n"
                f"{gold_balance} {GOLD_UNIT}s\n"
                f"Value: ${usd_value:.2f}"
            )

        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            return "Error checking balance. Please try again."

    def handle_history(self, phone_number):
        try:
            transactions = Transaction.get_history(phone_number)
            if not transactions:
                return "No transaction history found"

            history = "Recent transactions:"
            for tx in transactions:
                history += (
                    f"\n\nAmount: {tx.amount} {GOLD_UNIT}s"
                    f"\nValue: ${tx.usd_amount:.2f}"
                    f"\nStatus: {tx.status}"
                    f"\nReference: {tx.ref}"
                )

            return history

        except Exception as e:
            logger.error(f"Error fetching history: {str(e)}")
            return "Error fetching history. Please try again."

    def handle_account(self, phone_number):
        try:
            user = User.get_by_phone(phone_number)
            if not user:
                return "No account found. Buy Gold tokens first."

            success, balances = self.stellar.get_balances(user.public_key)
            
            return (
                f"Stellar Account Details:\n\n"
                f"Public Key: {user.public_key}\n"
                f"Created: {user.created_at}\n\n"
                f"View on Stellar Explorer:\n"
                f"https://stellar.expert/explorer/testnet/account/{user.public_key}"
            )

        except Exception as e:
            logger.error(f"Error getting account details: {str(e)}")
            return "Error fetching account details. Please try again."