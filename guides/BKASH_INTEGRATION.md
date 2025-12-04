# bKash Payment Gateway Integration Guide

## Overview

This guide covers the complete integration of bKash Tokenized Checkout API into the Pronoyon Question Bank application for wallet top-up functionality.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Testing](#testing)
5. [Production Deployment](#production-deployment)

---

## Prerequisites

### 1. bKash Merchant Account

- **Sandbox Account**: Sign up at [bKash Developer Portal](https://developer.bka.sh/)
- **Production Account**: Contact bKash Business Team

### 2. Get Credentials

After account approval, you'll receive:
- `App Key`
- `App Secret`
- `Username`
- `Password`

---

## Backend Setup

### 1. Environment Configuration

Add bKash credentials to your `.env` file:

```bash
# bKash Payment Gateway
BKASH_APP_KEY=your-app-key-here
BKASH_APP_SECRET=your-app-secret-here
BKASH_USERNAME=your-username-here
BKASH_PASSWORD=your-password-here
BKASH_SANDBOX=True  # Set to False for production
BKASH_CALLBACK_URL=http://localhost:3000/payment/callback
```

### 2. Database Migration

Run migrations to create wallet tables:

```bash
cd pronoyon-backend
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Initial Wallet (Optional)

Wallets are created automatically when users first access payment features, but you can also create them manually:

```python
from apps.payments.models import WalletBalance
from apps.rbac.models import User

user = User.objects.get(email='user@example.com')
wallet = WalletBalance.objects.create(user=user)
```

### 4. Test Backend APIs

Start the backend server:

```bash
docker compose up
```

API endpoints available:
- `GET /api/payments/wallets/` - Get user's wallet
- `GET /api/payments/wallets/{id}/transactions/` - Get transactions
- `POST /api/payments/wallets/{id}/topup/` - Initiate top-up
- `POST /api/payments/transactions/execute/` - Execute payment
- `POST /api/payments/transactions/query/` - Query payment status
- `POST /api/payments/transactions/refund/` - Refund (admin only)

---

## Frontend Setup

### 1. Add Wallet Page Route

Create a new page at `app/user/wallet/page.tsx`:

```typescript
import WalletManagement from '@/components/payments/WalletManagement';

export default function WalletPage() {
  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-8">My Wallet</h1>
      <WalletManagement />
    </div>
  );
}
```

### 2. Add Navigation Link

Add wallet link to your user navigation:

```typescript
import { Wallet } from 'lucide-react';

// In your navigation component
<Link href="/user/wallet">
  <Wallet className="mr-2 h-4 w-4" />
  Wallet
</Link>
```

### 3. Payment Callback Page

Create `app/payment/callback/page.tsx`:

```typescript
'use client';

import { useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useExecutePaymentMutation } from '@/lib/redux/services/paymentsApi';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function PaymentCallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [executePayment] = useExecutePaymentMutation();

  useEffect(() => {
    const paymentID = searchParams.get('paymentID');
    const status = searchParams.get('status');

    if (paymentID && status === 'success') {
      executePayment({ payment_id: paymentID })
        .unwrap()
        .then((result) => {
          toast.success(`Payment successful! Balance: ${result.new_balance} BDT`);
          router.push('/user/wallet');
        })
        .catch((error) => {
          toast.error(error?.data?.error || 'Payment verification failed');
          router.push('/user/wallet');
        });
    } else if (status === 'cancel') {
      toast.error('Payment cancelled');
      router.push('/user/wallet');
    } else if (status === 'failure') {
      toast.error('Payment failed');
      router.push('/user/wallet');
    }
  }, [searchParams, router, executePayment]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4" />
        <h2 className="text-xl font-semibold">Processing payment...</h2>
        <p className="text-muted-foreground">Please wait</p>
      </div>
    </div>
  );
}
```

---

## Testing

### 1. Sandbox Testing

bKash provides test credentials for sandbox:

**Test Numbers:**
- `01770618575` - Success scenario
- `01770618576` - Insufficient Balance
- `01770618577` - Invalid PIN

**Test PIN:** `1234`
**Test OTP:** `123456`

### 2. Test Flow

1. **Top Up Wallet:**
   ```
   - Go to /user/wallet
   - Click "Top Up"
   - Enter amount (e.g., 100 BDT)
   - Select payment method (bKash)
   - Click "Proceed to Payment"
   ```

2. **Complete Payment:**
   ```
   - New window opens with bKash checkout
   - Enter test mobile number
   - Enter test PIN
   - Enter test OTP
   - Confirm payment
   ```

3. **Verify Payment:**
   ```
   - Returns to callback page
   - Payment is executed automatically
   - Balance updates in wallet
   - Transaction appears in history
   ```

### 3. Test API Endpoints

Using curl or Postman:

```bash
# Get wallet
curl -X GET http://localhost:8000/api/payments/wallets/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Top up
curl -X POST http://localhost:8000/api/payments/wallets/{wallet_id}/topup/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "payment_method": "bkash"}'

# Execute payment
curl -X POST http://localhost:8000/api/payments/transactions/execute/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"payment_id": "TR00001234567890"}'
```

---

## Payment Flow Diagram

```
User → Frontend → Backend → bKash → User Confirmation → Backend → Wallet Updated
  ↓         ↓          ↓         ↓            ↓              ↓            ↓
  1     Click Top   Create    Return      Complete      Execute     Credit
        Up Button   Payment   bKash URL   Payment       Payment     Wallet
```

### Step-by-Step:

1. **Initiate:** User clicks "Top Up" button
2. **Create:** Backend calls bKash `create` API
3. **Redirect:** User redirected to bKash checkout
4. **Complete:** User completes payment in bKash
5. **Return:** User returns to callback URL
6. **Execute:** Backend calls bKash `execute` API
7. **Update:** Wallet balance is updated
8. **Notify:** User sees success message

---

## Production Deployment

### 1. Update Environment Variables

```bash
# Production .env
BKASH_SANDBOX=False
BKASH_APP_KEY=production-app-key
BKASH_APP_SECRET=production-app-secret
BKASH_USERNAME=production-username
BKASH_PASSWORD=production-password
BKASH_CALLBACK_URL=https://yourdomain.com/payment/callback
```

### 2. Security Checklist

- ✅ Use HTTPS for all endpoints
- ✅ Validate callback signatures
- ✅ Implement rate limiting
- ✅ Log all transactions
- ✅ Monitor failed payments
- ✅ Set up alerts for anomalies

### 3. Error Handling

The integration includes comprehensive error handling:
- Network errors
- API failures
- Token expiration
- Insufficient balance
- Transaction conflicts

### 4. Monitoring

Monitor these metrics:
- Payment success rate
- Average completion time
- Failed payment reasons
- Refund requests
- Token refresh frequency

---

## API Reference

### Wallet Endpoints

#### Get Wallet
```http
GET /api/payments/wallets/
Authorization: Bearer {token}
```

#### Get Transactions
```http
GET /api/payments/wallets/{id}/transactions/?status=completed&type=credit
Authorization: Bearer {token}
```

#### Top Up Wallet
```http
POST /api/payments/wallets/{id}/topup/
Authorization: Bearer {token}
Content-Type: application/json

{
  "amount": 100.00,
  "payment_method": "bkash"
}
```

### Payment Endpoints

#### Execute Payment
```http
POST /api/payments/transactions/execute/
Authorization: Bearer {token}
Content-Type: application/json

{
  "payment_id": "TR00001234567890"
}
```

#### Query Payment
```http
POST /api/payments/transactions/query/
Authorization: Bearer {token}
Content-Type: application/json

{
  "payment_id": "TR00001234567890"
}
```

#### Refund Transaction (Admin)
```http
POST /api/payments/transactions/refund/
Authorization: Bearer {token}
Content-Type: application/json

{
  "transaction_id": "uuid-here",
  "reason": "Customer request"
}
```

---

## Troubleshooting

### Common Issues

1. **Token Grant Failed**
   - Check credentials in .env
   - Verify sandbox mode setting
   - Check network connectivity

2. **Payment Creation Failed**
   - Verify callback URL is accessible
   - Check amount limits (10-50000 BDT)
   - Ensure valid invoice number

3. **Payment Execution Failed**
   - User may have cancelled payment
   - Insufficient balance in test account
   - Payment ID may be invalid/expired

4. **Callback Not Received**
   - Check firewall settings
   - Verify callback URL is publicly accessible
   - Check bKash webhook configuration

### Debug Mode

Enable detailed logging:

```python
# In settings
LOGGING = {
    'loggers': {
        'apps.payments': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Support

- **bKash Developer Portal:** https://developer.bka.sh/
- **bKash Support:** developer@bka.sh
- **Documentation:** https://developer.bka.sh/docs

---

## License

This integration is part of the Pronoyon Question Bank project.
