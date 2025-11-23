#!/bin/bash
set -e

# Wait for database
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database ready!"

# Run migrations
python manage.py migrate --noinput

# Create superuser for development
python manage.py shell <<EOF
from apps.accounts.models import CustomUser
if not CustomUser.objects.filter(email='dev@test.com').exists():
    CustomUser.objects.create_superuser(
        email='dev@test.com',
        password='dev123',
        first_name='Dev',
        last_name='User'
    )
    print('Dev superuser created: dev@test.com / dev123')
EOF

# Seed RBAC
python manage.py seed_rbac

exec "$@"
