# Development Guide

## 🚀 Quick Start

### Development Mode (with Hot Reload)

```bash
# 1. Set environment variables in .env
BUILD_TARGET=development
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.docker

# 2. Start with watch mode - auto-reloads on code changes
docker compose up --watch
```

### Production Mode

```bash
# 1. Set environment variables in .env
BUILD_TARGET=production
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production

# 2. Start without watch - uses Gunicorn
docker compose up -d
```

## 📋 How It Works

The project automatically detects the mode based on the `DEBUG` environment variable:

| Mode | Command | DEBUG | Server | Auto-reload | Use Case |
|------|---------|-------|--------|-------------|----------|
| **Development** | `docker compose up --watch` | `True` | Django Dev Server | ✅ Yes | Local development |
| **Production** | `docker compose up` | `False` | Gunicorn | ❌ No | Production deployment |

## 🔥 Development Mode Features

When `DEBUG=True`:

### 1. Auto-reload on Code Changes
The `--watch` flag enables automatic synchronization:

- **Python files** (`apps/`, `config/`) - Instant sync, Django auto-reloads
- **Requirements.txt** - Sync + container restart
- **Dockerfile** - Full rebuild

### 2. Django Development Server
- Runs `python manage.py runserver 0.0.0.0:8000`
- Automatic reload on Python file changes
- Better error pages with detailed tracebacks
- SQL query debugging

### 3. Development Tools Enabled
- Django Debug Toolbar (if installed)
- Browsable API in DRF
- Django Extensions
- Verbose logging

## 🚀 Production Mode Features

When `DEBUG=False`:

### 1. Gunicorn Production Server
- Multiple workers for concurrency
- Better performance and stability
- Process management and monitoring

### 2. Production Optimizations
- Static files served efficiently
- No auto-reload overhead
- Compressed responses
- Security headers enabled

### 3. Production Security
- Detailed error pages hidden
- HTTPS enforcement (when configured)
- Secure cookies
- CORS properly configured

## 📁 What Gets Watched in Development

The `develop.watch` configuration monitors:

```yaml
apps/          # Your Django apps - sync changes instantly
config/        # Settings and URLs - sync changes instantly
requirements.txt  # Dependencies - sync and restart
Dockerfile     # Build config - full rebuild
```

**Ignored:**
- `__pycache__/` directories
- `*.pyc` compiled files
- `.git/` directory
- Virtual environments

## 🛠️ Common Development Commands

```bash
# Start development with watch
docker compose up --watch

# View logs
docker compose logs -f web

# Run migrations
docker compose exec web python manage.py migrate

# Create migrations
docker compose exec web python manage.py makemigrations

# Django shell
docker compose exec web python manage.py shell

# Create superuser
docker compose exec web python manage.py createsuperuser

# Run tests
docker compose exec web python manage.py test

# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Database shell
docker compose exec db psql -U postgres -d replycompass_db

# Redis CLI
docker compose exec redis redis-cli
```

## 🔄 Switching Between Modes

### Switch to Development Mode

```bash
# 1. Update .env
echo "DEBUG=True" > .env.dev
echo "DJANGO_SETTINGS_MODULE=config.settings.docker" >> .env.dev

# 2. Stop current containers
docker compose down

# 3. Start in development mode
docker compose --env-file .env.dev up --watch
```

### Switch to Production Mode

```bash
# 1. Update .env
echo "DEBUG=False" > .env.prod
echo "DJANGO_SETTINGS_MODULE=config.settings.production" >> .env.prod

# 2. Stop current containers
docker compose down

# 3. Start in production mode
docker compose --env-file .env.prod up
```

## 🐛 Debugging Tips

### View Container Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web

# Last 100 lines
docker compose logs --tail 100 web
```

### Access Container Shell
```bash
# Web container
docker compose exec web bash

# Database
docker compose exec db psql -U postgres

# Redis
docker compose exec redis redis-cli
```

### Check Container Status
```bash
docker compose ps
```

### Restart Single Service
```bash
docker compose restart web
```

## 📊 Performance Monitoring

### Development Mode
- Django Debug Toolbar (http://localhost:8000/)
- Query count displayed in toolbar
- SQL query profiling
- Template rendering time

### Production Mode
- Gunicorn access logs
- Application performance monitoring (APM) tools
- Sentry error tracking (if configured)

## 🔐 Environment Variables

Key variables for development:

```env
# Development
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.docker
LOG_LEVEL=DEBUG

# Production
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
LOG_LEVEL=INFO
SECURE_SSL_REDIRECT=True
```

## 🧪 Testing

```bash
# Run all tests
docker compose exec web python manage.py test

# Run specific app
docker compose exec web python manage.py test apps.accounts

# Run with coverage
docker compose exec web pytest --cov=apps --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 📦 Adding New Dependencies

```bash
# 1. Add to requirements.txt
echo "package-name==version" >> requirements.txt

# 2. With --watch, it will auto-install and restart
# OR manually rebuild:
docker compose build web
docker compose up -d
```

## 🎯 Best Practices

### Development
- ✅ Use `--watch` for instant feedback
- ✅ Keep `DEBUG=True`
- ✅ Use Django dev server
- ✅ Enable debug toolbar
- ✅ Commit `.env.example`, not `.env`

### Production
- ✅ Set `DEBUG=False`
- ✅ Use Gunicorn with multiple workers
- ✅ Enable security headers
- ✅ Use environment-specific settings
- ✅ Monitor with Sentry/APM tools

## 🆘 Troubleshooting

### Changes Not Reflecting

```bash
# 1. Ensure --watch is used
docker compose up --watch

# 2. Check if files are being synced
docker compose logs web | grep "Syncing"

# 3. Hard restart
docker compose down
docker compose up --watch
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
WEB_PORT=8001 docker compose up --watch
```

### Database Connection Issues

```bash
# Check if DB is running
docker compose ps db

# View DB logs
docker compose logs db

# Restart DB
docker compose restart db
```

## 📚 Additional Resources

- [Docker Compose Watch Documentation](https://docs.docker.com/compose/file-watch/)
- [Django Development Server](https://docs.djangoproject.com/en/stable/ref/django-admin/#runserver)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

## 🎉 Happy Coding!

You're all set! Start developing with:

```bash
docker compose up --watch
```

Access your app at: http://localhost:8000
