"""
Management command to seed sample payment and wallet data for testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import ProgrammingError, OperationalError
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

from apps.payments.models import WalletBalance, WalletTransaction
from apps.rbac.models import Role, UserRole

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed sample users and payment data for admin dashboard testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before seeding',
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting payment data seeding...'))

            if options['clear']:
                self.stdout.write('Clearing existing sample data...')
                # Clear sample transactions (keep real ones)
                WalletTransaction.objects.filter(
                    description__contains='Sample'
                ).delete()
                self.stdout.write(self.style.SUCCESS('Sample data cleared'))

            # Get or create roles
            admin_role, _ = Role.objects.get_or_create(
                slug='admin',
                defaults={
                    'name': 'Admin',
                    'role_type': 'admin',
                    'level': 100
                }
            )
            
            manager_role, _ = Role.objects.get_or_create(
                slug='manager',
                defaults={
                    'name': 'Manager',
                    'role_type': 'manager',
                    'level': 60
                }
            )
            
            user_role, _ = Role.objects.get_or_create(
                slug='user',
                defaults={
                    'name': 'User',
                    'role_type': 'user',
                    'level': 10
                }
            )

            # Create sample users with different roles
            sample_users_data = [
                {
                    'email': 'admin@pronoyon.com',
                    'password': 'admin123',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'role': admin_role,
                    'is_staff': True,
                    'is_superuser': True,
                },
                {
                    'email': 'manager1@pronoyon.com',
                    'password': 'manager123',
                    'first_name': 'Farhana',
                    'last_name': 'Ahmed',
                    'role': manager_role,
                },
                {
                    'email': 'manager2@pronoyon.com',
                    'password': 'manager123',
                    'first_name': 'Tanvir',
                    'last_name': 'Rahman',
                    'role': manager_role,
                },
                {
                    'email': 'user1@example.com',
                    'password': 'user123',
                    'first_name': 'Anis',
                    'last_name': 'Khan',
                    'role': user_role,
                },
                {
                    'email': 'user2@example.com',
                    'password': 'user123',
                    'first_name': 'Mou',
                    'last_name': 'Akter',
                    'role': user_role,
                },
                {
                    'email': 'user3@example.com',
                    'password': 'user123',
                    'first_name': 'Rafi',
                    'last_name': 'Islam',
                    'role': user_role,
                },
            ]

            created_users = []
            for user_data in sample_users_data:
                role = user_data.pop('role')
                email = user_data.pop('email')
                password = user_data.pop('password')
                
                if User.objects.filter(email=email).exists():
                    user = User.objects.get(email=email)
                    self.stdout.write(self.style.WARNING(f'User {email} already exists'))
                else:
                    if user_data.get('is_superuser'):
                        # Remove is_staff and is_superuser from user_data as create_superuser sets them
                        user_data.pop('is_staff', None)
                        user_data.pop('is_superuser', None)
                        user = User.objects.create_superuser(
                            email=email,
                            password=password,
                            **user_data
                        )
                    else:
                        user = User.objects.create_user(
                            email=email,
                            password=password,
                            **user_data
                        )
                    self.stdout.write(self.style.SUCCESS(f'Created user: {email}'))
                
                # Assign role if not exists
                if not UserRole.objects.filter(user=user, role=role, is_active=True).exists():
                    # Check if user already has a primary role
                    has_primary = UserRole.objects.filter(user=user, is_primary=True, is_active=True).exists()
                    UserRole.objects.create(
                        user=user,
                        role=role,
                        is_primary=not has_primary,  # Only set as primary if user doesn't have one
                        is_active=True,
                        assigned_by=user if user.is_superuser else None
                    )
                    self.stdout.write(f'  Assigned role: {role.name}')
                
                created_users.append(user)

            # Create wallets and transactions for users
            now = timezone.now()
            payment_methods = ['bkash', 'nagad', 'rocket', 'bank']
            
            for user in created_users:
            # Get or create wallet
                wallet, created = WalletBalance.objects.get_or_create(
                    user=user,
                    defaults={'balance': Decimal('0.00')}
                )
            
                if created:
                    self.stdout.write(f'Created wallet for {user.email}')
            
            # Generate random transactions
            num_transactions = random.randint(3, 10)
            
            for i in range(num_transactions):
                # Random date within last 30 days
                days_ago = random.randint(0, 30)
                transaction_date = now - timedelta(days=days_ago)
                
                # Random transaction type (more credits than debits)
                transaction_type = random.choices(
                    [WalletTransaction.CREDIT, WalletTransaction.DEBIT],
                    weights=[70, 30]
                )[0]
                
                # Random amount
                if transaction_type == WalletTransaction.CREDIT:
                    amount = Decimal(str(random.choice([100, 200, 500, 1000, 1500, 2000])))
                else:
                    amount = Decimal(str(random.choice([50, 100, 150, 250, 500])))
                
                # Random status (mostly completed)
                status = random.choices(
                    [
                        WalletTransaction.COMPLETED,
                        WalletTransaction.PENDING,
                        WalletTransaction.FAILED,
                        WalletTransaction.REFUNDED
                    ],
                    weights=[80, 10, 5, 5]
                )[0]
                
                # Calculate balance after
                if status == WalletTransaction.COMPLETED:
                    if transaction_type == WalletTransaction.CREDIT:
                        wallet.balance += amount
                    else:
                        if wallet.balance >= amount:
                            wallet.balance -= amount
                
                balance_after = wallet.balance
                
                # Create transaction
                transaction = WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type=transaction_type,
                    amount=amount,
                    payment_method=random.choice(payment_methods),
                    status=status,
                    description=f"Sample {transaction_type} transaction",
                    balance_after=balance_after,
                    gateway_transaction_id=f"TXN{random.randint(100000, 999999)}",
                    created_at=transaction_date,
                    completed_at=transaction_date if status == WalletTransaction.COMPLETED else None
                )
                
                # Update wallet totals
                if status == WalletTransaction.COMPLETED:
                    if transaction_type == WalletTransaction.CREDIT:
                        wallet.total_credited += amount
                    else:
                        wallet.total_debited += amount
            
            wallet.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'  Generated {num_transactions} transactions for {user.email} '
                    f'(Balance: ৳{wallet.balance})'
                )
            )

            # Print summary
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('SEEDING COMPLETE'))
            self.stdout.write('='*60)
            self.stdout.write(f'Total Users: {User.objects.count()}')
            self.stdout.write(f'Total Wallets: {WalletBalance.objects.count()}')
            self.stdout.write(f'Total Transactions: {WalletTransaction.objects.count()}')
            self.stdout.write(f'Completed Transactions: {WalletTransaction.objects.filter(status=WalletTransaction.COMPLETED).count()}')
            self.stdout.write(f'Pending Transactions: {WalletTransaction.objects.filter(status=WalletTransaction.PENDING).count()}')
            
            from django.db.models import Sum
            total_revenue = WalletTransaction.objects.filter(
                transaction_type=WalletTransaction.CREDIT,
                status=WalletTransaction.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            self.stdout.write(f'Total Revenue: ৳{total_revenue}')
            self.stdout.write('\n' + self.style.SUCCESS('Sample Login Credentials:'))
            self.stdout.write('  Admin: admin@pronoyon.com / admin123')
            self.stdout.write('  Manager: manager1@pronoyon.com / manager123')
            self.stdout.write('  User: user1@example.com / user123')
            self.stdout.write('='*60 + '\n')
        
        except (ProgrammingError, OperationalError) as e:
            self.stdout.write(
                self.style.WARNING(
                    f'Payment data seeding skipped - database tables may not exist yet: {str(e)}'
                )
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during payment data seeding: {str(e)}')
            )
            raise
