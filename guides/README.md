# ReplyCompass Documentation

> Comprehensive guides for development, deployment, and system architecture

## 📖 Quick Navigation

### 🚀 Getting Started

**New to the project?** Start here:

1. **[Development Guide](development/DEVELOPMENT.md)** - Complete development workflow with Docker
2. **[Docker Setup](docker/DOCKER_SETUP_GUIDE.md)** - Detailed Docker configuration and usage
3. **[Quick Reference](docker/QUICK_REFERENCE.md)** - Common Docker commands and workflows

### 📚 Documentation by Category

## 🔧 Development

**Local development workflows and setup**

| Guide | Description |
|-------|-------------|
| **[Development Guide](development/DEVELOPMENT.md)** | Complete development workflow with hot-reload |
| **[Manual Setup Guide](development/SETUP_GUIDE_MANUAL.md)** | Local development without Docker |

**What you'll learn:**
- Setting up development environment
- Running with hot-reload
- Database migrations and management
- Testing workflows

## 🐳 Docker

**Containerization and Docker workflows**

| Guide | Description |
|-------|-------------|
| **[Docker Setup Guide](docker/DOCKER_SETUP_GUIDE.md)** | Comprehensive Docker configuration |
| **[Docker Watch Setup](docker/DOCKER_WATCH_SETUP.md)** | Hot-reload development with `--watch` |
| **[Quick Reference](docker/QUICK_REFERENCE.md)** | Common Docker commands |
| **[Docker Fixes](docker/DOCKER_FIXES.md)** | Troubleshooting guide |

**What you'll learn:**
- Multi-stage Dockerfile setup
- Development vs Production modes
- Docker Compose configuration
- Common issues and solutions

## 🎭 RBAC System

**Role-Based Access Control implementation**

| Guide | Description |
|-------|-------------|
| **[RBAC Guide](rbac/RBAC_GUIDE.md)** | Complete RBAC documentation |
| **[Quick Reference](rbac/RBAC_QUICK_REFERENCE.md)** | Roles and permissions cheat sheet |
| **[Implementation](rbac/RBAC_IMPLEMENTATION_SUMMARY.md)** | Technical implementation details |
| **[Selectors & Services](rbac/RBAC_SELECTORS_SERVICES_GUIDE.md)** | Architecture patterns |

**What you'll learn:**
- 9 hierarchical roles explained
- 33 granular permissions
- Permission checking
- Role assignment and management
- Custom permissions

## ⚙️ Configuration

**Settings, environment variables, and integrations**

| Guide | Description |
|-------|-------------|
| **[Settings Configuration](configuration/SETTINGS_CONFIGURATION_GUIDE.md)** | Django settings explained |
| **[CORS Configuration](configuration/DJANGO_CORS_HEADERS_GUIDE.md)** | Frontend integration setup |
| **[Multiple Frontends](configuration/MULTIPLE_FRONTEND_SUPPORT.md)** | Supporting multiple frontend apps |

**What you'll learn:**
- Environment variables
- Django settings structure
- CORS setup for frontends
- Multi-frontend support

## 🧪 Testing

**Test coverage and testing workflows**

| Guide | Description |
|-------|-------------|
| **[Testing Guide](testing/TESTING_GUIDE.md)** | Comprehensive testing documentation |

**What you'll learn:**
- Running tests
- Writing unit tests
- API testing
- Test coverage
- Integration tests

## 🚀 Deployment

**Production deployment and checklist**

| Guide | Description |
|-------|-------------|
| **[GitHub Checklist](deployment/GITHUB_CHECKLIST.md)** | Pre-deployment checklist |

**What you'll learn:**
- Production configuration
- Security checklist
- Deployment steps
- Post-deployment verification

## 🔍 Find What You Need

### By Task

**I want to...**

- **Start development** → [Development Guide](development/DEVELOPMENT.md)
- **Use Docker** → [Docker Setup Guide](docker/DOCKER_SETUP_GUIDE.md)
- **Configure permissions** → [RBAC Guide](rbac/RBAC_GUIDE.md)
- **Setup frontend** → [CORS Configuration](configuration/DJANGO_CORS_HEADERS_GUIDE.md)
- **Deploy to production** → [GitHub Checklist](deployment/GITHUB_CHECKLIST.md)
- **Fix Docker issues** → [Docker Fixes](docker/DOCKER_FIXES.md)

### By Experience Level

**Beginner:**
1. [Development Guide](development/DEVELOPMENT.md)
2. [Quick Reference](docker/QUICK_REFERENCE.md)
3. [RBAC Quick Reference](rbac/RBAC_QUICK_REFERENCE.md)

**Intermediate:**
1. [Docker Setup Guide](docker/DOCKER_SETUP_GUIDE.md)
2. [RBAC Guide](rbac/RBAC_GUIDE.md)
3. [Settings Configuration](configuration/SETTINGS_CONFIGURATION_GUIDE.md)

**Advanced:**
1. [RBAC Implementation](rbac/RBAC_IMPLEMENTATION_SUMMARY.md)
2. [Selectors & Services](rbac/RBAC_SELECTORS_SERVICES_GUIDE.md)
3. [Multiple Frontends](configuration/MULTIPLE_FRONTEND_SUPPORT.md)

## 📋 Quick Commands

### Development
```bash
make dev           # Start development with hot-reload
make dev-build     # Rebuild and start development
make shell         # Django shell (iPython)
make test          # Run tests
```

### Database
```bash
make migrate       # Run migrations
make seed          # Seed RBAC data
make superuser     # Create superuser
make dbshell       # Database shell
```

### Docker
```bash
make health        # Check service health
make logs-web      # View web logs
make bash          # Container bash shell
make ps            # List containers
```

### Production
```bash
make prod          # Start production
make prod-build    # Rebuild production
make backup-db     # Backup database
```

> See [`../Makefile`](../Makefile) or run `make help` for all commands

## 🏗️ Project Structure

```
replycompass/
├── apps/
│   ├── accounts/       # User authentication
│   ├── core/          # Core utilities
│   └── rbac/          # RBAC system
├── config/            # Settings & URLs
├── guides/            # ← You are here
│   ├── development/   # Development guides
│   ├── docker/        # Docker guides
│   ├── rbac/          # RBAC documentation
│   ├── configuration/ # Config guides
│   └── deployment/    # Deployment guides
├── static/           # Static files
├── media/            # Uploaded files
└── requirements.txt
```

## 🆘 Need Help?

### Common Issues

1. **Services won't start**
   - Check: [Docker Fixes](docker/DOCKER_FIXES.md)
   - Run: `make health`

2. **Permission errors**
   - Check: [RBAC Guide](rbac/RBAC_GUIDE.md)
   - Run: `make seed`

3. **Configuration issues**
   - Check: [Settings Configuration](configuration/SETTINGS_CONFIGURATION_GUIDE.md)
   - Verify: `.env` file

### Still stuck?

- Check [Docker Fixes](docker/DOCKER_FIXES.md) for troubleshooting
- Review [Quick Reference](docker/QUICK_REFERENCE.md) for commands
- See [Development Guide](development/DEVELOPMENT.md) for workflows

## 📞 Support

- **GitHub Issues**: For bugs and feature requests
- **Documentation**: You're in it!
- **Email**: support@yourapp.com

---

**Pro tip:** Use `Ctrl+F` to search for specific topics within this page! 🔍
