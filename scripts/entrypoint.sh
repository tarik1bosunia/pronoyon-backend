#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 0.1
done
echo "PostgreSQL started"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
  sleep 0.1
done
echo "Redis started"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if doesn't exist
echo "Checking for superuser..."
python manage.py shell <<EOF
from apps.accounts.models import CustomUser
if not CustomUser.objects.filter(is_superuser=True).exists():
    CustomUser.objects.create_superuser(
        email='admin@replycompass.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created: admin@replycompass.com / admin123')
else:
    print('Superuser already exists')
EOF

# Seed RBAC data if needed
echo "Seeding RBAC data..."
python manage.py seed_rbac 2>&1 || echo "RBAC seeding skipped or error occurred (tables may not exist yet)"

# Seed Question Bank permissions
echo "Seeding Question Bank permissions..."
python manage.py seed_question_bank 2>&1 || echo "Question Bank seeding skipped or error occurred"

# Create default superuser
echo "Creating default superuser..."
python manage.py create_superuser || echo "Superuser already exists"

# Seed payment data (sample users and transactions)
echo "Seeding payment data..."
python manage.py seed_payment_data || echo "Payment data already seeded or error occurred"

echo "Starting application..."
exec "$@"
