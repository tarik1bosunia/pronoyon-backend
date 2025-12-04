# Payments Module

## Overview

The payments module handles wallet management and bKash payment gateway integration for the Pronoyon Question Bank application.

## Features

✅ **Wallet Management**
- User wallet balance tracking
- Transaction history
- Real-time balance updates
- Lifetime statistics (total credited, total debited)

✅ **bKash Integration**
- Tokenized checkout API
- Secure payment flow
- Automatic token management
- Payment execution and verification
- Refund support

✅ **Transaction Types**
- Credit (Top-up via bKash, Nagad, Rocket, Bank)
- Debit (PDF export payments)

✅ **Payment Methods**
- bKash (Primary)
- Nagad
- Rocket
- Bank Transfer

✅ **Security**
- JWT authentication required
- Transaction validation
- Balance verification
- Error handling and logging

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   Backend   │────────▶│   bKash     │
│  (Next.js)  │         │   (Django)  │         │     API     │
└─────────────┘         └─────────────┘         └─────────────┘
       │                       │                        │
       │                       ▼                        │
       │                ┌─────────────┐                │
       │                │  PostgreSQL │                │
       │                │   Database  │                │
       │                └─────────────┘                │
       │                                                │
       └────────────────────────────────────────────────┘
              (Payment callback & verification)
```

## Database Models

### WalletBalance
- Stores user wallet balance
- Tracks lifetime statistics
- One-to-one with User model

### WalletTransaction
- Records all wallet transactions
- Stores payment gateway responses
- Supports credit and debit operations

### PaymentTransaction
- Tracks PDF export payments
- Links to user drafts
- References wallet transactions

## API Endpoints

### Wallet Management

#### Get Wallet
```http
GET /api/payments/wallets/
Authorization: Bearer {token}

Response:
{
  "id": "uuid",
  "balance": "100.00",
  "total_credited": "500.00",
  "total_debited": "400.00",
  ...
}
```

#### Get Transactions
```http
GET /api/payments/wallets/{id}/transactions/
Authorization: Bearer {token}
Query: ?status=completed&type=credit

Response: [
  {
    "id": "uuid",
    "transaction_type": "credit",
    "amount": "100.00",
    "payment_method": "bkash",
    "status": "completed",
    ...
  }
]
```

#### Top Up Wallet
```http
POST /api/payments/wallets/{id}/topup/
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "amount": 100.00,
  "payment_method": "bkash"
}

Response:
{
  "success": true,
  "payment_id": "TR00001234567890",
  "bkash_url": "https://tokenized.sandbox.bka.sh/...",
  "transaction_id": "uuid"
}
```

### Payment Operations

#### Execute Payment
```http
POST /api/payments/transactions/execute/
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "payment_id": "TR00001234567890"
}

Response:
{
  "success": true,
  "trx_id": "BKA12345678",
  "amount": "100.00",
  "new_balance": "1100.00"
}
```

#### Query Payment
```http
POST /api/payments/transactions/query/
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "payment_id": "TR00001234567890"
}

Response:
{
  "success": true,
  "payment_id": "TR00001234567890",
  "trx_id": "BKA12345678",
  "status": "Completed",
  "amount": "100.00"
}
```

#### Refund Transaction (Admin Only)
```http
POST /api/payments/transactions/refund/
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "transaction_id": "uuid",
  "reason": "Customer request"
}

Response:
{
  "success": true,
  "refund_trx_id": "BKA87654321",
  "amount": "100.00"
}
```

## Frontend Components

### WalletManagement
Main component for wallet interface:
- Displays current balance
- Shows lifetime statistics
- Top-up dialog with payment method selection
- Transaction history table
- Real-time updates

Location: `components/payments/WalletManagement.tsx`

### Payment Callback Handler
Handles return from bKash:
- Processes payment status
- Executes payment verification
- Updates UI based on result
- Redirects to wallet

Location: `app/payment/callback/page.tsx`

## Redux Integration

### Store Setup
```typescript
import { paymentsApi } from './services/paymentsApi';

const store = configureStore({
  reducer: {
    [paymentsApi.reducerPath]: paymentsApi.reducer,
    // ... other reducers
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .concat(paymentsApi.middleware),
});
```

### Usage in Components
```typescript
import {
  useGetWalletQuery,
  useTopUpWalletMutation,
  useExecutePaymentMutation,
} from '@/lib/redux/services/paymentsApi';

function MyComponent() {
  const { data: wallet } = useGetWalletQuery();
  const [topUpWallet] = useTopUpWalletMutation();
  const [executePayment] = useExecutePaymentMutation();
  
  // ... component logic
}
```

## Payment Flow

### 1. Initiate Top-Up
```
User → Click "Top Up" → Enter amount → Select bKash → Submit
```

### 2. Create Payment
```
Frontend → POST /api/payments/wallets/{id}/topup/ → Backend
Backend → bKash Create API → Returns payment_id & bkash_url
```

### 3. User Payment
```
Frontend → Opens bkash_url in new window
User → Completes payment in bKash
bKash → Redirects to callback_url
```

### 4. Execute Payment
```
Frontend → Detects callback → POST /api/payments/transactions/execute/
Backend → bKash Execute API → Confirms payment
Backend → Credits wallet → Returns new balance
```

### 5. Update UI
```
Frontend → Displays success message → Refreshes wallet balance
```

## Error Handling

### Frontend
- Network errors → Toast notification
- API errors → Display error message
- Payment cancellation → Return to wallet
- Payment failure → Show retry option

### Backend
- Token expiration → Auto refresh
- Invalid payment → Return error response
- Insufficient balance → Prevent transaction
- Database errors → Rollback transaction

## Testing

### Unit Tests
```bash
cd pronoyon-backend
pytest apps/payments/tests/
```

### Integration Tests
```bash
# Test wallet creation
pytest apps/payments/tests/test_wallet.py

# Test payment flow
pytest apps/payments/tests/test_payments.py
```

### Manual Testing (Sandbox)
```
1. Get sandbox credentials from bKash
2. Update .env with test credentials
3. Navigate to /user/wallet
4. Test top-up with test number: 01770618575
5. Use PIN: 1234, OTP: 123456
6. Verify balance update
```

## Configuration

### Environment Variables
```bash
# bKash Settings
BKASH_APP_KEY=your-app-key
BKASH_APP_SECRET=your-app-secret
BKASH_USERNAME=your-username
BKASH_PASSWORD=your-password
BKASH_SANDBOX=True
BKASH_CALLBACK_URL=http://localhost:3000/payment/callback
```

### Django Settings
```python
# config/settings/base.py
BKASH_APP_KEY = config('BKASH_APP_KEY', default='')
BKASH_APP_SECRET = config('BKASH_APP_SECRET', default='')
BKASH_USERNAME = config('BKASH_USERNAME', default='')
BKASH_PASSWORD = config('BKASH_PASSWORD', default='')
BKASH_SANDBOX = config('BKASH_SANDBOX', default=True, cast=bool)
BKASH_CALLBACK_URL = config('BKASH_CALLBACK_URL', default='')
```

## Monitoring

### Logs
```python
import logging
logger = logging.getLogger('apps.payments')

# View logs
tail -f logs/django.log | grep payments
```

### Metrics to Track
- Payment success rate
- Average transaction time
- Failed payment reasons
- Refund requests
- Token refresh frequency

## Security Best Practices

✅ Always use HTTPS in production
✅ Validate all payment amounts
✅ Verify payment signatures
✅ Implement rate limiting
✅ Log all transactions
✅ Monitor for suspicious activity
✅ Use environment variables for credentials
✅ Never expose bKash credentials in frontend
✅ Implement CSRF protection
✅ Use secure session management

## Troubleshooting

### Issue: Token grant failed
**Solution:** Check bKash credentials in .env file

### Issue: Payment creation failed
**Solution:** Verify callback URL is accessible and amount is within limits

### Issue: Payment execution failed
**Solution:** Check if payment was completed in bKash, query payment status

### Issue: Balance not updating
**Solution:** Check transaction status, verify execute API was called successfully

## Future Enhancements

- [ ] Add Nagad/Rocket integration
- [ ] Implement automatic refunds
- [ ] Add payment analytics dashboard
- [ ] Support multiple currencies
- [ ] Add payment reminders
- [ ] Implement loyalty points
- [ ] Add payment history export
- [ ] Create admin refund interface

## Support

- **bKash Developer Portal:** https://developer.bka.sh/
- **API Documentation:** https://developer.bka.sh/docs
- **Support Email:** developer@bka.sh

## License

Part of Pronoyon Question Bank Application
