# app/services/sms.py
import logging
from app.models.user import User
from app.models.transaction import Transaction
from app.services.stellar import StellarService
from app.services.payment import PaymentService
import uuid

logger = logging.getLogger('sms_crypto')

class SMSService:
    def __init__(self):
        self.stellar = StellarService()
        self.payment = PaymentService()

    def handle_message(self, phone_number, message):
        """Main message handler returning plain text responses"""
        message = message.lower().strip()
        parts = message.split()

        if not parts:
            return self.get_help_message()

        command = parts[0]
        logger.info(f"Processing command: {command} from {phone_number}")

        if command == 'buy':
            return self.handle_buy(phone_number, parts[1] if len(parts) > 1 else None)
        elif command == 'confirm':
            return self.handle_confirm(phone_number, parts[1] if len(parts) > 1 else None)
        elif command == 'balance':
            return self.handle_balance(phone_number)
        elif command == 'history':
            return self.handle_history(phone_number)
        else:
            return self.get_help_message()

    def handle_buy(self, phone_number, amount_str):
        """Handle buy command"""
        if not amount_str:
            return "Invalid format. Use: buy <amount>\nExample: buy 50"
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                return "Amount must be greater than 0"

            logger.info(f"Processing buy request for {amount} USDC")
            reference = self.generate_reference()

            transaction = Transaction(
                phone_number=phone_number,
                ref=reference,
                amount=amount
            )
            transaction.save()

            return (
                f"Please deposit ${amount} at MoneyGram using reference: {reference}\n"
                f"After depositing, send: confirm {reference}"
            )

        except ValueError:
            return "Invalid amount. Please enter a number.\nExample: buy 50"

    def handle_confirm(self, phone_number, reference):
        """Handle confirm command"""
        if not reference:
            return "Invalid format. Use: confirm <reference>"
            
        reference = reference.upper()
        # ... rest of confirm logic ...
        return "Successfully purchased X USDC!"

    def handle_balance(self, phone_number):
        """Handle balance command"""
        user = User.get_by_phone(phone_number)
        if not user:
            return "No account found. Buy USDC first."

        success, balances = self.stellar.get_balances(user.public_key)
        if not success:
            return f"Error checking balance: {balances}"

        return f"Your USDC balance: {balances['USDC']}"

    def handle_history(self, phone_number):
        """Handle history command"""
        transactions = Transaction.get_history(phone_number)
        if not transactions:
            return "No transaction history found"

        history = "Recent transactions:"
        for tx in transactions:
            history += (
                f"\nDate: {tx.created_at}\n"
                f"Amount: {tx.amount} USDC\n"
                f"Status: {tx.status}\n"
                f"Reference: {tx.ref}"
            )
            if tx.stellar_tx_id:
                history += f"\nTransaction: {tx.stellar_tx_id}"

        return history

    def get_help_message(self):
        """Return help message"""
        return (
            "Available commands:\n"
            "buy <amount> - Start USDC purchase\n"
            "confirm <reference> - Confirm payment\n"
            "balance - Check USDC balance\n"
            "history - View recent transactions\n\n"
            "Example: buy 50"
        )

    def generate_reference(self):
        """Generate unique MoneyGram reference"""
        return f"MG-{uuid.uuid4().hex[:8].upper()}"