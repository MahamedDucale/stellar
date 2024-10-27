# SMS Crypto Buyer

A prototype SMS-based application for purchasing USDC cryptocurrency using MoneyGram payments.

## Features

- Purchase USDC via SMS
- MoneyGram payment integration (simulated)
- Real-time balance checking
- Transaction history
- Stellar blockchain integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```
DISTRIBUTION=your_distribution_secret_key
TWILIO_PHONE_NUMBER=your_twilio_number
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
DEBUG=True
PORT=5000
```

3. Initialize the application:
```bash
python main.py
```

## SMS Commands

- `buy <amount>` - Start USDC purchase
- `confirm <reference>` - Confirm payment
- `balance` - Check USDC balance
- `history` - View transaction history

## Testing

For local testing:
1. Install ngrok: https://ngrok.com/download
2. Run ngrok: `ngrok http 5000`
3. Update Twilio webhook URL with ngrok URL/sms

## Development Notes

- Currently using Stellar testnet
- MoneyGram integration is simulated
- All transactions are logged in SQLite database