# Pronoyon Backend

[![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A robust Django-based backend API with advanced Role-Based Access Control (RBAC), comprehensive authentication, payment processing, and question bank management.

## ✨ Features

- 🔐 **Authentication & Authorization**
  - Email-based authentication with Django Allauth
  - Social OAuth (Google)
  - JWT token-based authentication
  - Advanced RBAC system with 9 hierarchical roles and 33 granular permissions

- 🎯 **Core Functionality**
  - User account management
  - Question bank system with groups and subjects
  - Payment processing and wallet management
  - RESTful API with Django REST Framework

- 🚀 **Performance & Scalability**
  - PostgreSQL database for production-ready data storage
  - Redis for caching and session management
  - Celery for asynchronous task processing
  - Django Channels for WebSocket support

- 🛠️ **Developer Experience**
  - Fully containerized with Docker
  - Hot-reload development environment
  - Comprehensive API documentation (Swagger/ReDoc)
  - Extensive test coverage
  - Code quality tools (Black, Flake8, Pylint)

- 📊 **Production Ready**
  - Gunicorn production server
  - Nginx reverse proxy
  - Environment-based configuration
  - Health check endpoints
  - Error tracking with Sentry

## 🏗️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Django 5.2.8 |
| **API Framework** | Django REST Framework |
| **Database** | PostgreSQL 15 |
| **Cache/Broker** | Redis 7 |
| **Task Queue** | Celery + Celery Beat |
| **Web Server** | Gunicorn + Nginx |
| **WebSocket** | Django Channels |
| **Containerization** | Docker & Docker Compose |
| **API Documentation** | drf-spectacular |

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/tarik1bosunia/pronoyon-backend.git
   cd pronoyon-backend
   ```

2. **Create environment file**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**

   ```bash
   make install
   ```

   Or manually:

   ```bash
   # Build and start services
   BUILD_TARGET=development docker compose build
   BUILD_TARGET=development docker compose up -d
   
   # Run migrations
   docker compose exec web python manage.py migrate
   
   # Seed RBAC roles and permissions
   docker compose exec web python manage.py seed_rbac
   ```

4. **Access the application**
   - **Admin Panel**: <http://localhost:8000/admin/>
   - **API Root**: <http://localhost:8000/api/>
   - **API Docs (Swagger)**: <http://localhost:8000/api/schema/swagger-ui/>
   - **API Docs (ReDoc)**: <http://localhost:8000/api/schema/redoc/>

5. **Create superuser**

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

## 📋 Common Commands

### Development

```bash
make dev              # Start development with hot-reload
make dev-build        # Rebuild & start development
make dev-down         # Stop development
make dev-logs         # View development logs
```

### Production

```bash
make prod             # Start production environment
make prod-build       # Rebuild & start production
make prod-down        # Stop production
make prod-logs        # View production logs
```

### Database

```bash
make migrate          # Run database migrations
make makemigrations   # Create new migrations
make seed             # Seed RBAC roles and permissions
make superuser        # Create Django superuser
```

### Testing

```bash
make test             # Run all tests
make coverage         # Run tests with coverage report
```

### Utilities

```bash
make shell            # Open Django shell (iPython)
make bash             # Open container bash shell
make ps               # List running containers
make clean            # Remove containers and volumes
make help             # Show all available commands
```

## 🏛️ Project Structure

```
pronoyon-backend/
├── apps/
│   ├── accounts/          # User authentication and profiles
│   ├── core/              # Core utilities and base classes
│   ├── rbac/              # Role-Based Access Control system
│   ├── questions/         # Question bank management
│   └── payments/          # Payment and wallet management
├── config/                # Project settings and configuration
│   ├── settings/
│   │   ├── base.py       # Shared settings
│   │   ├── local.py      # Local development settings
│   │   ├── production.py # Production settings
│   │   └── docker.py     # Docker-specific settings
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── guides/                # Comprehensive documentation
├── scripts/               # Deployment and utility scripts
├── static/                # Static files
├── mediafiles/            # User uploaded files
├── logs/                  # Application logs
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── Makefile               # Common commands
└── requirements.txt       # Python dependencies
```

## 🔐 RBAC System

The application includes a comprehensive Role-Based Access Control system with hierarchical roles:

### Predefined Roles (Hierarchical)

1. **Guest** (Level 0) - Basic read access
2. **User** (Level 10) - Standard user permissions
3. **Premium User** (Level 20) - Enhanced features
4. **Moderator** (Level 30) - Content moderation
5. **Content Manager** (Level 40) - Content management
6. **Support Agent** (Level 50) - Customer support
7. **Manager** (Level 60) - Team management
8. **Admin** (Level 70) - Administrative access
9. **Super Admin** (Level 80) - Full system access

### Permission Categories

- **User Management** - View, create, update, delete users
- **Content Management** - CRUD operations on content
- **Analytics** - View and export analytics
- **Settings** - System configuration
- **Billing** - Billing and invoices
- **Support** - Ticket management
- **API Access** - API read/write/admin permissions
- **Admin Panel** - System administration

> 📖 See [`guides/rbac/RBAC_GUIDE.md`](guides/rbac/RBAC_GUIDE.md) for detailed RBAC documentation

## 🌐 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: <http://localhost:8000/api/schema/swagger-ui/>
- **ReDoc**: <http://localhost:8000/api/schema/redoc/>
- **OpenAPI Schema**: <http://localhost:8000/api/schema/>

## ⚙️ Environment Configuration

Key environment variables (see `.env.example` for full list):

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=pronoyon
DB_USER=pronoyon_user
DB_PASSWORD=change-this-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=change-this-password

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Build Configuration
BUILD_TARGET=development  # or 'production'
DJANGO_SETTINGS_MODULE=config.settings.docker
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific app tests
docker compose exec web python manage.py test apps.rbac

# Run with coverage
make coverage
```

## 📚 Documentation

All detailed guides are in the [`guides/`](guides/) directory:

### Getting Started

- [Development Guide](guides/development/DEVELOPMENT.md) - Complete development workflow
- [Docker Setup Guide](guides/docker/DOCKER_SETUP_GUIDE.md) - Comprehensive Docker configuration
- [Manual Setup Guide](guides/development/SETUP_GUIDE_MANUAL.md) - Local development without Docker

### RBAC System

- [RBAC Guide](guides/rbac/RBAC_GUIDE.md) - Complete RBAC documentation
- [RBAC Quick Reference](guides/rbac/RBAC_QUICK_REFERENCE.md) - Quick reference for roles and permissions
- [RBAC Implementation](guides/rbac/RBAC_IMPLEMENTATION_SUMMARY.md) - Technical implementation details

### Configuration

- [Settings Configuration](guides/configuration/SETTINGS_CONFIGURATION_GUIDE.md) - Django settings explained
- [CORS Configuration](guides/configuration/DJANGO_CORS_HEADERS_GUIDE.md) - Frontend integration setup
- [Multiple Frontends](guides/configuration/MULTIPLE_FRONTEND_SUPPORT.md) - Supporting multiple frontend apps

### Deployment

- [GitHub Checklist](guides/deployment/GITHUB_CHECKLIST.md) - Pre-deployment checklist
- [Docker Fixes](guides/docker/DOCKER_FIXES.md) - Common Docker issues and solutions

## 🚢 Production Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Set up external PostgreSQL (AWS RDS, DigitalOcean, etc.)
- [ ] Set up external Redis
- [ ] Configure cloud storage for media files (S3, Cloudinary, etc.)
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Enable backups

### Production Configuration

```env
BUILD_TARGET=production
DEBUG=False
SECRET_KEY=<strong-random-secret>
ALLOWED_HOSTS=yourdomain.com
# Use external managed services
DB_HOST=your-postgres-host
REDIS_HOST=your-redis-host
```

Then start:

```bash
make prod-build
```

## 🛠️ Development Setup (Without Docker)

1. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Configure your local database and Redis settings
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   python manage.py seed_rbac
   ```

5. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**

   ```bash
   python manage.py runserver
   ```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

[Your License Here]

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tarik1bosunia/pronoyon-backend/issues)
- **Documentation**: [`guides/`](guides/)
- **Email**: <support@pronoyon.com>

---

Made with ❤️ by the Pronoyon Team
