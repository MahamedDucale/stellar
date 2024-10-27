# GOLD-SMS

A prototype SMS-based application for purchasing Gold token cryptocurrency using MoneyGram cash point payments for the unbanked.

## Features

- Purchase Gold via SMS
- MoneyGram payment integration (simulated)
- Real-time balance checking
- Transaction history
- Stellar blockchain integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file using `.env.example`

3. Initialize the application:
```bash
python main.py
```

## SMS Commands

- `buy <amount>` - Start USDC purchase
- `confirm <reference>` - Confirm payment
- `balance` - Check Gold balance
- `history` - View transaction history
- `account` - View Account

## Technical Architecture

### System Overview
The system architecture diagram below shows how different components interact:

```mermaid
flowchart TD
    User((User)) -->|SMS| Twilio[Twilio SMS Gateway]
    Twilio -->|Webhook| Backend[SMS Crypto Buyer Backend]
    Backend -->|Query/Update| DB[(SQLite Database)]
    Backend -->|API Calls| Stellar[Stellar Network]
    Backend -->|Verify Payment| MoneyGram[MoneyGram API]
    
    subgraph Backend Services
        Backend
        CommandParser[Command Parser]
        TransactionManager[Transaction Manager]
        BlockchainService[Blockchain Service]
        PaymentService[Payment Service]
    end
    
    Backend --> CommandParser
    CommandParser --> TransactionManager
    TransactionManager --> BlockchainService
    TransactionManager --> PaymentService
```

### Purchase Flow
The sequence diagram below illustrates the purchase flow from SMS initiation to completion:

```mermaid
sequenceDiagram
    participant U as User
    participant T as Twilio
    participant B as Backend
    participant M as MoneyGram
    participant S as Stellar

    U->>+T: SMS: "buy 100"
    T->>+B: Webhook Request
    B->>B: Generate Payment Reference
    B->>-U: SMS: MoneyGram Instructions
    
    U->>M: Cash Payment
    U->>+T: SMS: "confirm REF123"
    T->>+B: Webhook Request
    B->>+M: Verify Payment
    M-->>-B: Payment Confirmed
    
    B->>+S: Initialize Gold Token Transfer
    S-->>-B: Transaction Complete
    B->>-U: SMS: Purchase Confirmation
```

### Database Schema
The entity relationship diagram shows the database structure:

```mermaid
erDiagram
    USERS ||--o{ TRANSACTIONS : has
    USERS {
        string phone_number PK
        string stellar_address
        timestamp created_at
    }
    TRANSACTIONS {
        int id PK
        string reference
        string phone_number FK
        decimal amount
        string status
        timestamp created_at
        timestamp updated_at
    }
```

## Testing

For local testing:
1. Install ngrok: https://ngrok.com/download
2. Run ngrok: `ngrok http 5000`
3. Update Twilio webhook URL with ngrok URL/sms

## Development Notes

- Currently using Stellar testnet
- MoneyGram integration is simulated
- All transactions are logged in SQLite database
