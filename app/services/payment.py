# app/services/payment.py
import logging

logger = logging.getLogger('sms_crypto')

class PaymentService:
    def verify_payment(self, reference):
        """
        Verify MoneyGram payment (simulated)
        In production, this would integrate with MoneyGram's API
        """
        logger.info(f"Verifying payment reference: {reference}")
        return True  # Simulated verification

    def process_refund(self, reference):
        """
        Process refund if needed (simulated)
        In production, this would integrate with MoneyGram's refund API
        """
        logger.info(f"Processing refund for reference: {reference}")
        return True  # Simulated refund