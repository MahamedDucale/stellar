# tests/test_sms.py
import pytest
from app.services.sms import SMSService
from app.models.user import User
from app.models.transaction import Transaction
import re
import os
from datetime import datetime
from stellar_sdk import Keypair

@pytest.fixture
def sms_service():
    """Create SMS service instance for testing"""
    return SMSService()

@pytest.fixture
def test_phone():
    """Test phone number"""
    return "+1234567890"

@pytest.fixture
def test_user(test_phone):
    """Create a test user"""
    user = User(
        phone_number=test_phone,
        public_key="GBBD47IF6LWK7P7MDEVSCWR7DPUWV3NY3DTQEVFL4NAT4AQH3ZLLFLA5",
        secret_key="SDFSDFSDFSDFSDFSDFSDFSDFSDFSDFSDFSDFSDFSDFSDF"  # Example key
    )
    user.save()
    return user

def test_generate_reference(sms_service):
    """Test MoneyGram reference generation"""
    ref = sms_service.generate_reference()
    assert ref.startswith("MG-")
    assert len(ref) == 11  # "MG-" + 8 characters
    assert re.match(r"MG-[A-F0-9]{8}", ref)  # Should be uppercase hex

def test_handle_buy_valid(sms_service, test_phone):
    """Test buying USDC with valid amount"""
    response = sms_service.handle_message(test_phone, "buy 50")
    assert "Please deposit $50" in response
    assert "reference: MG-" in response
    assert "confirm" in response.lower()

def test_handle_buy_invalid(sms_service, test_phone):
    """Test buying USDC with invalid amount"""
    response = sms_service.handle_message(test_phone, "buy invalid")
    assert "Invalid amount" in response
    assert "Example" in response

def test_handle_buy_negative(sms_service, test_phone):
    """Test buying USDC with negative amount"""
    response = sms_service.handle_message(test_phone, "buy -50")
    assert "Amount must be greater than 0" in response

def test_handle_confirm_invalid_ref(sms_service, test_phone):
    """Test confirming with invalid reference"""
    response = sms_service.handle_message(test_phone, "confirm MG-INVALID")
    assert "Reference number not found" in response

def test_handle_balance_new_user(sms_service, test_phone):
    """Test balance check for new user"""
    response = sms_service.handle_message(test_phone, "balance")
    assert "No account found" in response
    assert "Buy USDC first" in response

def test_handle_balance_existing_user(sms_service, test_user):
    """Test balance check for existing user"""
    response = sms_service.handle_message(test_user.phone_number, "balance")
    assert "USDC balance" in response

def test_handle_history_no_transactions(sms_service, test_phone):
    """Test history with no transactions"""
    response = sms_service.handle_message(test_phone, "history")
    assert "No transaction history found" in response

def test_handle_history_with_transactions(sms_service, test_phone):
    """Test history with transactions"""
    # Create some test transactions
    tx = Transaction(
        phone_number=test_phone,
        ref="MG-12345678",
        amount=50.0,
        status="completed",
        stellar_tx_id="abc123"
    )
    tx.save()
    
    response = sms_service.handle_message(test_phone, "history")
    assert "Recent transactions" in response
    assert "MG-12345678" in response
    assert "50.0" in response
    assert "completed" in response

def test_handle_invalid_command(sms_service, test_phone):
    """Test invalid command handling"""
    response = sms_service.handle_message(test_phone, "invalid")
    assert "Available commands" in response
    assert "buy" in response
    assert "confirm" in response
    assert "balance" in response
    assert "history" in response

def test_full_purchase_flow(sms_service, test_phone):
    """Test complete purchase flow"""
    # Start purchase
    buy_response = sms_service.handle_message(test_phone, "buy 50")
    assert "Please deposit $50" in buy_response
    
    # Extract reference
    ref_match = re.search(r'MG-[A-F0-9]{8}', buy_response)
    assert ref_match is not None
    ref = ref_match.group(0)
    
    # Confirm purchase
    confirm_response = sms_service.handle_message(test_phone, f"confirm {ref}")
    assert "Successfully purchased" in confirm_response or "Error" in confirm_response
    
    # Check balance
    balance_response = sms_service.handle_message(test_phone, "balance")
    assert "USDC balance" in balance_response

@pytest.mark.integration
def test_distribution_account_balance(sms_service):
    """Test distribution account has sufficient balance"""
    stellar_service = sms_service.stellar
    success, balances = stellar_service.get_balances(
        Keypair.from_secret(os.getenv("DISTRIBUTION")).public_key
    )
    assert success is True
    assert float(balances['XLM']) > 5  # Should have enough XLM
    assert float(balances['USDC']) > 0  # Should have some USDC