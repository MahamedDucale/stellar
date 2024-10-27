# tests/test_stellar.py
import pytest
from app.services.stellar import StellarService
from stellar_sdk import Keypair
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

@pytest.fixture
def stellar_service():
    """Create a StellarService instance for testing"""
    return StellarService()

@pytest.fixture
def test_account(stellar_service):
    """Create a funded test account"""
    keypair = stellar_service.create_account()
    time.sleep(5)  # Wait for account creation
    return keypair

def test_create_account(stellar_service):
    """Test creating a new Stellar account"""
    keypair = stellar_service.create_account()
    assert keypair is not None
    assert isinstance(keypair, Keypair)
    assert keypair.public_key.startswith('G')
    assert keypair.secret.startswith('S')

def test_setup_trustline(stellar_service, test_account):
    """Test setting up USDC trustline"""
    success, result = stellar_service.setup_trustline(test_account.secret)
    assert success is True
    assert isinstance(result, str)  # Should be transaction hash
    assert len(result) == 64  # Stellar transaction hash length

def test_get_balances(stellar_service, test_account):
    """Test getting account balances"""
    success, balances = stellar_service.get_balances(test_account.public_key)
    assert success is True
    assert isinstance(balances, dict)
    assert 'XLM' in balances
    assert 'USDC' in balances
    assert float(balances['XLM']) > 0  # Should have initial XLM
    assert float(balances['USDC']) >= 0  # Might be 0 initially

def test_send_usdc(stellar_service, test_account):
    """Test sending USDC"""
    # First setup trustline
    stellar_service.setup_trustline(test_account.secret)
    time.sleep(5)  # Wait for trustline setup

    # Try to send a small amount of USDC
    success, result = stellar_service.send_usdc(test_account.public_key, "0.1")
    assert success is True
    assert isinstance(result, str)
    assert len(result) == 64  # Transaction hash

def test_format_stellar_key(stellar_service):
    """Test key formatting"""
    test_key = "GBBD47IF6LWK7P7MDEVSCWR7DPUWV3NY3DTQEVFL4NAT4AQH3ZLLFLA5"
    formatted = stellar_service.format_stellar_key(test_key)
    assert len(formatted) < len(test_key)
    assert formatted.startswith('GBBD')
    assert formatted.endswith('FLA5')
    assert '...' in formatted

def test_create_usdc_asset(stellar_service):
    """Test USDC asset creation"""
    asset = stellar_service.create_usdc_asset()
    assert asset.code == "USDC"
    assert asset.issuer == os.getenv("USDC_ISSUER")

@pytest.mark.integration
def test_distribution_account(stellar_service):
    """Test distribution account setup"""
    distribution_key = os.getenv("DISTRIBUTION")
    assert distribution_key is not None
    
    success, balances = stellar_service.get_balances(
        Keypair.from_secret(distribution_key).public_key
    )
    assert success is True
    assert float(balances['XLM']) > 0
    assert float(balances['USDC']) >= 0