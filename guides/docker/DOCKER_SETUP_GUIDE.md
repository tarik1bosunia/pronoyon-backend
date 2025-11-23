# Docker Setup Guide for ReplyCompass

## 📦 Overview

This Docker setup provides a complete development and production environment for ReplyCompass with:

- **Django Web Application** (Gunicorn in production, runserver in dev)
- **PostgreSQL Database** with extensions
- **Redis** for caching and message broker
- **Celery Worker** for background tasks
- **Celery Beat** for scheduled tasks
- **Nginx** reverse proxy (production only)
- **MailHog** email testing (development only)

---

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Make (optional, for convenience commands)

### Installation

1. **Clone and navigate to project:**
   ```bash
   cd /home/tata/tarik/replycompass
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file with your settings:**
   ```bash
   nano .env
   ```

4. **Build and start services:**
   ```bash
   # Using Make (recommended)
   make install

   # Or using docker compose directly
   docker compose build
   docker compose up -d
   ```

5. **Run migrations and seed data:**
   ```bash
   make migrate
   make seed-rbac
   ```

6. **Create superuser:**
   ```bash
   make createsuperuser
   ```

7. **Access the application:**
   - Web: http://localhost:8000
   - Admin: http://localhost:8000/admin/
   - API: http://localhost:8000/api/

---

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Django
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,yourdomain.com

# Database
DB_NAME=replycompass
DB_USER=replycompass_user
DB_PASSWORD=changeme
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_PASSWORD=changeme
REDIS_HOST=redis
REDIS_PORT=6379

# Ports
WEB_PORT=8000
NGINX_PORT=80
NGINX_SSL_PORT=443
```

---

## 🛠️ Development Setup

### Start Development Environment

```bash
# Using Make
make dev-build

# Or using docker compose
docker compose -f docker compose.dev.yml up --build
```

### Development Features

- **Hot Reload**: Code changes are automatically reflected
- **Debug Mode**: Django runs with DEBUG=True
- **MailHog**: Email testing UI at http://localhost:8025
- **Django Debug Toolbar**: Available when installed
- **Direct Database Access**: PostgreSQL on port 5432

### Development Commands

```bash
# View logs
make dev-logs

# Access Django shell
docker compose -f docker compose.dev.yml exec web python manage.py shell

# Run tests
docker compose -f docker compose.dev.yml exec web python manage.py test

# Access container bash
docker compose -f docker compose.dev.yml exec web bash
```

### Development Services

- **Web**: http://localhost:8000
- **MailHog UI**: http://localhost:8025
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## 🚀 Production Setup

### Start Production Environment

```bash
# Build and start
make prod-build

# Or using docker compose
docker compose up --build -d
```

### Production Features

- **Gunicorn**: Production WSGI server with 3 workers
- **Nginx**: Reverse proxy with SSL support, caching, and rate limiting
- **Static Files**: Served by Nginx for better performance
- **Health Checks**: Automatic service monitoring
- **Auto-restart**: Services restart on failure
- **Security**: Non-root user, security headers, SSL-ready

### Production Commands

```bash
# View logs
make prod-logs

# Restart services
docker compose restart

# Check health
make health

# View specific service logs
make logs-web
make logs-celery
make logs-db
```

### SSL Configuration (Production)

1. **Place SSL certificates:**
   ```bash
   mkdir -p nginx/ssl
   cp /path/to/fullchain.pem nginx/ssl/
   cp /path/to/privkey.pem nginx/ssl/
   ```

2. **Uncomment HTTPS block in `nginx/conf.d/replycompass.conf`**

3. **Update `.env`:**
   ```bash
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   SECURE_HSTS_SECONDS=31536000
   ```

4. **Restart Nginx:**
   ```bash
   docker compose restart nginx
   ```

---

## 📋 Common Commands

### Using Make (Recommended)

```bash
# Development
make dev              # Start dev environment
make dev-build        # Build and start dev
make dev-down         # Stop dev environment
make dev-logs         # View dev logs

# Production
make prod             # Start production
make prod-build       # Build and start production
make prod-down        # Stop production
make prod-logs        # View production logs

# Database
make migrate          # Run migrations
make makemigrations   # Create migrations
make dbshell          # Open DB shell
make seed-rbac        # Seed RBAC data
make backup-db        # Backup database

# Management
make shell            # Django shell
make createsuperuser  # Create superuser
make test             # Run tests
make collectstatic    # Collect static files

# Utilities
make restart          # Restart all services
make ps               # List containers
make health           # Check service health
make clean            # Remove everything
```

### Using Docker Compose Directly

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild and start
docker compose up --build -d

# Execute command in container
docker compose exec web python manage.py migrate

# View running containers
docker compose ps

# Restart specific service
docker compose restart web
```

---

## 🗄️ Database Management

### Run Migrations

```bash
make migrate

# Or
docker compose exec web python manage.py migrate
```

### Create Migrations

```bash
make makemigrations

# Or
docker compose exec web python manage.py makemigrations
```

### Access Database Shell

```bash
make dbshell

# Or
docker compose exec db psql -U replycompass_user -d replycompass
```

### Backup Database

```bash
make backup-db

# Or manually
docker compose exec db pg_dump -U replycompass_user replycompass > backup.sql
```

### Restore Database

```bash
# Using Make (interactive)
make restore-db

# Or manually
docker compose exec -T db psql -U replycompass_user replycompass < backup.sql
```

---

## 🔄 Celery Tasks

### View Celery Worker Logs

```bash
make logs-celery

# Or
docker compose logs -f celery_worker
```

### Restart Celery

```bash
docker compose restart celery_worker celery_beat
```

### Monitor Celery Tasks

```bash
# Access worker container
docker compose exec celery_worker bash

# Inside container, use celery commands
celery -A config inspect active
celery -A config inspect scheduled
celery -A config inspect stats
```

---

## 🧪 Testing

### Run All Tests

```bash
make test

# Or
docker compose exec web python manage.py test
```

### Run Specific Tests

```bash
docker compose exec web python manage.py test apps.rbac
docker compose exec web python manage.py test apps.accounts.tests.test_models
```

### Run Tests with Coverage

```bash
make test-coverage

# Or
docker compose exec web pytest --cov=apps --cov-report=html
```

---

## 📊 Monitoring & Logs

### View All Logs

```bash
make prod-logs
# Or
docker compose logs -f
```

### View Specific Service Logs

```bash
make logs-web         # Django web
make logs-celery      # Celery worker
make logs-db          # PostgreSQL
make logs-redis       # Redis
```

### Check Service Health

```bash
make health
```

### Container Status

```bash
make ps
# Or
docker compose ps
```

---

## 🔍 Debugging

### Access Django Shell

```bash
make shell

# Or
docker compose exec web python manage.py shell
```

### Access Container Bash

```bash
# Development
docker compose -f docker compose.dev.yml exec web bash

# Production
docker compose exec web bash
```

### View Container Logs

```bash
# Last 100 lines
docker compose logs --tail=100 web

# Follow logs
docker compose logs -f web

# Specific time range
docker compose logs --since 30m web
```

### Inspect Container

```bash
docker inspect replycompass_web
docker stats replycompass_web
```

---

## 🛡️ Security Best Practices

### Production Checklist

- [ ] Change default passwords in `.env`
- [ ] Set strong `SECRET_KEY`
- [ ] Enable SSL/HTTPS
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Enable CSRF and secure cookies
- [ ] Set up firewall rules
- [ ] Use secrets management (e.g., Docker secrets, AWS Secrets Manager)
- [ ] Regularly update Docker images
- [ ] Monitor logs for suspicious activity

### Secure Secrets Management

Instead of plain text in `.env`, use Docker secrets:

```bash
# Create secrets
echo "my_secret_key" | docker secret create django_secret_key -
echo "my_db_password" | docker secret create db_password -

# Reference in docker compose.yml
services:
  web:
    secrets:
      - django_secret_key
      - db_password
    environment:
      SECRET_KEY_FILE: /run/secrets/django_secret_key
```

---

## 🔧 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose logs

# Check if ports are already in use
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :5432

# Clean and rebuild
make clean
make prod-build
```

### Database Connection Issues

```bash
# Check if DB is running
docker compose ps db

# Check DB logs
docker compose logs db

# Test connection
docker compose exec web python manage.py dbshell
```

### Permission Issues

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix volume permissions
docker compose exec web chown -R appuser:appuser /app
```

### Redis Connection Issues

```bash
# Check Redis
docker compose exec redis redis-cli ping

# Test Redis from web container
docker compose exec web python -c "import redis; r=redis.Redis(host='redis', port=6379); print(r.ping())"
```

### Static Files Not Loading

```bash
# Collect static files
make collectstatic

# Check nginx config
docker compose exec nginx nginx -t

# Restart nginx
docker compose restart nginx
```

### Celery Tasks Not Running

```bash
# Check worker logs
docker compose logs celery_worker

# Inspect Celery
docker compose exec celery_worker celery -A config inspect active

# Restart worker
docker compose restart celery_worker celery_beat
```

---

## 📦 Docker Images

### Build Custom Image

```bash
# Production
docker build -t replycompass:latest .

# Development
docker build -f Dockerfile.dev -t replycompass:dev .
```

### Push to Registry

```bash
# Tag image
docker tag replycompass:latest your-registry.com/replycompass:latest

# Push to registry
docker push your-registry.com/replycompass:latest
```

---

## 🔄 Updates & Maintenance

### Update Dependencies

```bash
# Update requirements.txt
docker compose exec web pip install -r requirements.txt --upgrade

# Rebuild image
docker compose up --build -d
```

### Clean Up

```bash
# Remove stopped containers
docker compose down

# Remove volumes (CAUTION: deletes data)
docker compose down -v

# Remove everything
make clean
```

### Prune Docker System

```bash
# Remove unused containers, networks, images
docker system prune -a

# Remove volumes too (CAUTION)
docker system prune -a --volumes
```

---

## 📈 Performance Optimization

### Gunicorn Workers

Adjust in `docker compose.yml`:

```yaml
command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2
```

**Formula**: workers = (2 × CPU cores) + 1

### Nginx Caching

Add to `nginx/conf.d/replycompass.conf`:

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 60m;
}
```

### Database Connection Pooling

In Django settings:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

---

## 🌐 Multi-Container Deployment

For production deployment across multiple servers, consider:

- **Docker Swarm**: Built-in orchestration
- **Kubernetes**: Advanced orchestration
- **AWS ECS/EKS**: Managed container services
- **Google Kubernetes Engine**: Managed Kubernetes
- **Azure Container Instances**: Serverless containers

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

## 🎉 You're Ready!

Your Docker setup is complete! Choose your environment:

```bash
# Development (with hot reload)
make dev-build

# Production (optimized)
make prod-build
```

**Happy containerizing! 🐳**
