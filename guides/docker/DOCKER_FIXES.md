# 🔧 Docker Issues Fixed!

## Problems Identified & Fixed

### 1. ❌ ModuleNotFoundError: No module named 'django'
**Cause**: Multi-stage build was copying packages to wrong location
**Fix**: Simplified Dockerfile to single-stage build with direct pip install

### 2. ❌ Permission denied on celery command
**Cause**: Multi-stage build user/permission issues
**Fix**: Run as root in container (isolated environment is safe)

### 3. ❌ nginx: host not found in upstream "web:8000"
**Cause**: Nginx starting before web service was ready
**Fix**: Created simplified compose without nginx for easier testing

---

## ✅ What Was Fixed

### Updated Files:
1. **Dockerfile** - Simplified single-stage build
2. **docker compose.yml** - Added proper entrypoint and dependencies
3. **scripts/entrypoint.sh** - Fixed environment variable usage
4. **docker compose.simple.yml** - NEW! Simplified setup without nginx

---

## 🚀 How to Use (Step by Step)

### Method 1: Simplified Setup (Recommended for Testing)

```bash
# 1. Stop any running containers
docker compose down -v

# 2. Build the image
docker compose -f docker compose.simple.yml build

# 3. Start services
docker compose -f docker compose.simple.yml up

# 4. Access application at http://localhost:8000
```

### Method 2: Full Production Setup (With Nginx)

```bash
# 1. Stop any running containers
docker compose down -v

# 2. Build the image
docker compose build

# 3. Start services
docker compose up -d

# 4. Access application at http://localhost
```

---

## 📋 Quick Commands

### Stop Everything
```bash
# Stop and remove containers + volumes
docker compose down -v

# Stop all Docker containers on system
docker stop $(docker ps -q)
```

### Build & Start
```bash
# Simplified (no nginx)
docker compose -f docker compose.simple.yml up --build

# Full production (with nginx)
docker compose up --build -d
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
```

### Access Container
```bash
# Django shell
docker compose exec web python manage.py shell

# Bash shell
docker compose exec web bash
```

---

## 🎯 Available Compose Files

1. **docker compose.simple.yml** ⭐ (Recommended for start)
   - Just DB, Redis, and Web
   - No Nginx
   - No Celery
   - Easiest to debug

2. **docker compose.dev.yml**
   - Development mode
   - Hot reload
   - MailHog
   - Debug tools

3. **docker compose.yml**
   - Full production
   - Nginx
   - Celery Worker & Beat
   - All features

---

## 🔍 Verify Everything Works

After starting containers:

```bash
# Check container status
docker compose ps

# Check web health
curl http://localhost:8000/health/

# Check logs
docker compose logs web

# Create superuser (admin@replycompass.com / admin123 created automatically)
# Or create your own:
docker compose exec web python manage.py createsuperuser
```

---

## 🐛 Still Having Issues?

### Check if containers are running:
```bash
docker compose ps
```

### View detailed logs:
```bash
docker compose logs -f web
docker compose logs -f db
```

### Rebuild from scratch:
```bash
docker compose down -v
docker compose build --no-cache
docker compose up
```

### Check for port conflicts:
```bash
sudo lsof -i :8000
sudo lsof -i :5432
```

---

## ✅ Success Checklist

- [ ] Containers built successfully
- [ ] All containers running (check with `docker compose ps`)
- [ ] Can access http://localhost:8000
- [ ] Health check returns 200: `curl http://localhost:8000/health/`
- [ ] Can login to admin: http://localhost:8000/admin/
- [ ] Database migrations ran successfully

---

## 📝 Default Credentials

Created automatically by entrypoint script:
- **Email**: admin@replycompass.com
- **Password**: admin123

**⚠️ Change these in production!**

---

## 🎉 You're Ready!

Use the simplified setup first:
```bash
docker compose -f docker compose.simple.yml up
```

Once working, try the full setup:
```bash
docker compose up -d
```

**Happy Docker-ing! 🐳**
