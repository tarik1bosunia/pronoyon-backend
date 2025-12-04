# Payment Data Seeding

## Overview
The `seed_payment_data` management command creates sample users, wallets, and transactions for testing the admin dashboard.

## What it creates:

### Users (6 total):
1. **Admin User**
   - Email: `admin@pronoyon.com`
   - Password: `admin123`
   - Role: Admin (superuser)

2. **Manager Users** (2):
   - `manager1@pronoyon.com` / `manager123` (Farhana Ahmed)
   - `manager2@pronoyon.com` / `manager123` (Tanvir Rahman)
   - Role: Manager

3. **Regular Users** (3):
   - `user1@example.com` / `user123` (Anis Khan)
   - `user2@example.com` / `user123` (Mou Akter)
   - `user3@example.com` / `user123` (Rafi Islam)
   - Role: User

### For each user:
- Creates a wallet with initial balance
- Generates 3-10 random transactions
- Transactions include:
  - Random amounts (100-2000 for credits, 50-500 for debits)
  - Random payment methods (bKash, Nagad, Rocket, Bank)
  - Random statuses (80% completed, 10% pending, 5% failed, 5% refunded)
  - Dates spread across last 30 days

## Usage:

### Manual execution:
```bash
python manage.py seed_payment_data
```

### Clear existing sample data and reseed:
```bash
python manage.py seed_payment_data --clear
```

### Automatic execution:
The command runs automatically when Docker starts (configured in entrypoint scripts).

## Testing the Admin Dashboard:

1. Login with admin credentials: `admin@pronoyon.com` / `admin123`
2. Navigate to `/admin` in the frontend
3. View the dashboard with real statistics:
   - User counts and role distribution
   - Payment statistics and revenue
   - Transaction breakdowns
   - Active/inactive users

## Notes:
- The command is idempotent - it won't create duplicate users
- Sample transactions are marked with "Sample" in description
- Use `--clear` flag to remove only sample data, keeping real transactions
- All users have simple passwords for development purposes only
