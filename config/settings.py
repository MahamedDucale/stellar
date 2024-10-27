# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Stellar Configuration
STELLAR_SERVER_URL = "https://horizon-testnet.stellar.org"
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"

# Gold Token Configuration
GOLD_CODE = "GOLD"
GOLD_ISSUER = os.getenv("GOLD_ISSUER")
GOLD_DECIMALS = 6
GOLD_UNIT = "gram"
GOLD_DESCRIPTION = "Test Gold Token - Each token represents 1 gram of physical gold"

# Price API Configuration
METALS_API_KEY = os.getenv("METALS_API_KEY")
PRICE_UPDATE_INTERVAL = 300  # 5 minutes

# Distribution Account
DISTRIBUTION_SECRET_KEY = os.getenv("DISTRIBUTION")

# Application Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", "5000"))