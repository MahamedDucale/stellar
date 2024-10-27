# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Stellar Configuration
STELLAR_SERVER_URL = "https://horizon-testnet.stellar.org"
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
USDC_ISSUER = "GBBD47IF6LWK7P7MDEVSCWR7DPUWV3NY3DTQEVFL4NAT4AQH3ZLLFLA5"
DISTRIBUTION_SECRET_KEY = os.getenv("DISTRIBUTION")

# Twilio Configuration
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Database Configuration
DATABASE_URL = "sqlite:///transactions.db"

# Application Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", "5000"))