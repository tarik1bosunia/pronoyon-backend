# 🚀 Quick Reference - Docker Development & Production

## Environment Setup

### Development Mode
```bash
# In .env file:
BUILD_TARGET=development
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.docker
```

### Production Mode
```bash
# In .env file:
BUILD_TARGET=production
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
```

## Docker Commands

### Development (Hot Reload)
```bash
docker compose up --watch              # Start with file watching
docker compose up --watch --build      # Rebuild and start with watching
docker compose logs -f web             # View logs
```

### Production
```bash
docker compose up -d                   # Start in background
docker compose up -d --build          # Rebuild and start
docker compose ps                      # Check status
docker compose logs -f                # View all logs
docker compose down                    # Stop all containers
```

### Rebuild After Changes
```bash
# If you changed Dockerfile or requirements.txt
docker compose build --no-cache       # Full rebuild
docker compose up --build             # Rebuild and start
```

## What Gets Auto-Reloaded (Development Mode)

✅ **Instant Sync** (no restart):
- `apps/**/*.py` - Python files in apps
- `config/**/*.py` - Settings and URLs

🔄 **Sync + Restart**:
- `requirements.txt` - Dependencies

🔨 **Full Rebuild**:
- `Dockerfile` - Docker configuration

## Architecture

### Dockerfile Stages

```
base (common dependencies)
├── development (+ dev tools, Django runserver)
└── production (Gunicorn, optimized)
```

**Development Stage**:
- Django dev server
- Hot-reload enabled
- ipython, ipdb, django-debug-toolbar
- Detailed error pages

**Production Stage**:
- Gunicorn with 3 workers
- No dev dependencies
- Optimized and secured
- Health checks enabled

## Common Commands

### Django Management
```bash
# Run migrations
docker compose exec web python manage.py migrate

# Create migrations
docker compose exec web python manage.py makemigrations

# Django shell
docker compose exec web python manage.py shell

# Create superuser
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic --noinput
```

### Database
```bash
# Connect to PostgreSQL
docker compose exec db psql -U replycompass_user -d replycompass

# Backup database
docker compose exec db pg_dump -U replycompass_user replycompass > backup.sql

# Restore database
docker compose exec -T db psql -U replycompass_user replycompass < backup.sql
```

### Redis
```bash
# Connect to Redis
docker compose exec redis redis-cli -a changeme

# Flush cache
docker compose exec redis redis-cli -a changeme FLUSHALL
```

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f celery_worker

# Last 100 lines
docker compose logs --tail=100 web
```

## Troubleshooting

### Ports Already in Use
```bash
# Find what's using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Clean Start
```bash
# Stop everything and remove volumes
docker compose down -v

# Remove all containers and images
docker compose down --rmi all --volumes

# Rebuild from scratch
docker compose build --no-cache
docker compose up --watch
```

### Permission Issues
```bash
# Fix permissions on logs/media directories
sudo chown -R $USER:$USER logs/ mediafiles/ staticfiles/
```

### Container Not Starting
```bash
# Check container status
docker compose ps

# View container logs
docker compose logs web

# Check container health
docker inspect replycompass_web --format='{{.State.Health.Status}}'
```

## File Structure

```
replycompass/
├── Dockerfile                  # Multi-stage: base → dev/prod
├── docker compose.yml          # Orchestration (all services)
├── .env                       # Environment config (not in git)
├── .env.example               # Template with defaults
├── requirements.txt           # Python dependencies
├── apps/                      # Django apps (watched)
├── config/                    # Settings (watched)
├── scripts/                   # Entrypoint scripts
└── guides/                    # Documentation
```

## Environment Variables

### Required
- `BUILD_TARGET` - development | production
- `DEBUG` - True | False
- `DJANGO_SETTINGS_MODULE` - config.settings.docker | production
- `SECRET_KEY` - Django secret key
- `DB_PASSWORD` - Database password
- `REDIS_PASSWORD` - Redis password

### Optional
- `DB_NAME` - Database name (default: replycompass)
- `DB_USER` - Database user (default: replycompass_user)
- `DB_HOST` - Database host (default: db)
- `REDIS_HOST` - Redis host (default: redis)
- `WEB_PORT` - Web port (default: 8000)

## Quick Switching

### Switch to Development
```bash
sed -i 's/BUILD_TARGET=.*/BUILD_TARGET=development/' .env
sed -i 's/DEBUG=.*/DEBUG=True/' .env
docker compose down
docker compose up --watch
```

### Switch to Production
```bash
sed -i 's/BUILD_TARGET=.*/BUILD_TARGET=production/' .env
sed -i 's/DEBUG=.*/DEBUG=False/' .env
docker compose down
docker compose up -d
```

## Best Practices

### Development
- ✅ Use `--watch` for hot-reload
- ✅ Keep `DEBUG=True`
- ✅ Use `config.settings.docker`
- ✅ Monitor logs with `-f` flag
- ✅ Commit `.env.example`, not `.env`

### Production
- ✅ Set `DEBUG=False`
- ✅ Use strong `SECRET_KEY`
- ✅ Change default passwords
- ✅ Use `config.settings.production`
- ✅ Enable HTTPS/SSL
- ✅ Set up monitoring and backups

## Need Help?

- 📖 [Full Development Guide](DEVELOPMENT.md)
- 🐳 [Docker Setup Guide](DOCKER_SETUP_GUIDE.md)
- 🔧 [Docker Fixes](DOCKER_FIXES.md)
- 📚 [All Guides](README.md)
