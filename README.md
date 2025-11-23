# ReplyCompass# ReplyCompass



> Django-based web application with advanced Role-Based Access Control (RBAC) systemA Django-based web application with comprehensive Role-Based Access Control (RBAC) system.



[![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://www.djangoproject.com/)## Features

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)- 🔐 **Custom User Authentication** - Email-based authentication with Django Allauth

[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)- 🎭 **Advanced RBAC System** - 9 predefined roles with 33 granular permissions

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)- 🔄 **RESTful API** - Django REST Framework with JWT authentication

- 📊 **PostgreSQL Database** - Production-ready relational database

## ✨ Features- ⚡ **Redis Cache** - High-performance caching and session storage

- 🐳 **Docker Support** - Fully containerized development and production setup

- 🔐 **Email-Based Authentication** - Django Allauth with social OAuth- 🔄 **Celery Tasks** - Asynchronous task processing

- 🎭 **Advanced RBAC** - 9 hierarchical roles with 33 granular permissions- 🌐 **Django Channels** - WebSocket support for real-time features

- 🚀 **REST API** - DRF with JWT authentication + Swagger docs- 📝 **API Documentation** - Auto-generated with drf-spectacular

- 🐘 **PostgreSQL** - Production-ready database

- ⚡ **Redis** - Caching & session storage## Tech Stack

- 🐳 **Docker** - Full containerization with hot-reload

- 🔄 **Celery** - Async task processing with beat scheduler- **Backend**: Django 5.2.8

- 🌐 **WebSockets** - Django Channels for real-time features- **API**: Django REST Framework

- 📊 **API Documentation** - Auto-generated Swagger & ReDoc- **Database**: PostgreSQL 15

- **Cache/Broker**: Redis 7

## 🚀 Quick Start- **Task Queue**: Celery

- **Web Server**: Gunicorn + Nginx

### Prerequisites- **Containerization**: Docker & Docker Compose



- Docker & Docker Compose## Quick Start with Docker

- Git

### Prerequisites

### Installation

- Docker & Docker Compose installed

```bash- Git

# Clone repository

git clone <your-repo-url>### 1. Clone the repository

cd replycompass

```bash

# Setup and rungit clone <your-repo-url>

make installcd replycompass

``````



That's it! The application will be available at http://localhost:8000### 2. Create environment file



**Default credentials:**```bash

- Email: `admin@replycompass.com`cp .env.example .env

- Password: `admin123`# Edit .env with your configuration

```

### Common Commands

### 3. Start the application

```bash

make help          # Show all available commands#### Development Mode (with hot-reload)

make dev           # Start development with hot-reload```bash

make prod          # Start production environment# Set in .env:

make test          # Run testsBUILD_TARGET=development

make migrate       # Run database migrationsDEBUG=True

make shell         # Open Django shellDJANGO_SETTINGS_MODULE=config.settings.docker

```

# Start with watch mode

## 📋 Quick Referencedocker compose up --watch

```

| Command | Description |- ✅ Auto-reloads on code changes

|---------|-------------|- ✅ Django development server

| `make dev` | Start development with hot-reload |- ✅ Detailed error pages

| `make dev-build` | Rebuild and start development |- ✅ Development tools installed

| `make prod` | Start production environment |- ✅ Best for local development

| `make migrate` | Run database migrations |

| `make seed` | Seed RBAC roles & permissions |#### Production Mode

| `make test` | Run all tests |```bash

| `make shell` | Django shell (iPython) |# Set in .env:

| `make bash` | Container bash shell |BUILD_TARGET=production

| `make health` | Check service health |DEBUG=False

| `make clean` | Remove all containers & volumes |DJANGO_SETTINGS_MODULE=config.settings.production



> Run `make help` for the complete list of commands# Start in background

docker compose up -d

## 🏗️ Architecture```

- ✅ Gunicorn production server

### Tech Stack- ✅ Multiple workers

- ✅ Optimized for performance

| Component | Technology |- ✅ Production security enabled

|-----------|-----------|- ✅ Best for deployment

| **Backend** | Django 5.2.8 |

| **API** | Django REST Framework |> **Note**: The `BUILD_TARGET` environment variable controls which Dockerfile stage is used.

| **Database** | PostgreSQL 15 |

| **Cache** | Redis 7 |### 4. Access the application

| **Task Queue** | Celery + Beat |

| **Web Server** | Gunicorn + Nginx |- **Admin Panel**: http://localhost:8000/admin/

| **Container** | Docker + Docker Compose |- **API**: http://localhost:8000/api/

- **API Docs**: http://localhost:8000/api/schema/swagger-ui/

### Project Structure

**Default Superuser:**

```- **Email**: `admin@replycompass.com`

replycompass/- **Password**: `admin123`

├── apps/

│   ├── accounts/       # User authentication> 📖 **See [guides/DEVELOPMENT.md](guides/DEVELOPMENT.md) for detailed development guide**

│   ├── core/          # Core utilities

│   └── rbac/          # Role-Based Access Control## 📚 Documentation

├── config/            # Settings & configuration

│   ├── settings/All detailed guides are in the [`guides/`](guides/) directory:

│   │   ├── base.py           # Shared settings

│   │   ├── local.py          # Local development### Getting Started

│   │   ├── production.py     # Production- [Development Guide](guides/DEVELOPMENT.md) - Complete development workflow

│   │   └── docker.py         # Docker- [Docker Watch Setup](guides/DOCKER_WATCH_SETUP.md) - Hot-reload development setup

│   ├── urls.py- [Docker Setup Guide](guides/DOCKER_SETUP_GUIDE.md) - Comprehensive Docker configuration

│   ├── celery.py- [Manual Setup Guide](guides/SETUP_GUIDE_MANUAL.md) - Local development without Docker

│   └── wsgi.py/asgi.py

├── guides/            # Documentation### RBAC System

├── static/           # Static files- [RBAC Guide](guides/RBAC_GUIDE.md) - Complete RBAC documentation

├── media/            # Uploaded files- [RBAC Quick Reference](guides/RBAC_QUICK_REFERENCE.md) - Quick reference for roles and permissions

├── docker-compose.yml- [RBAC Implementation](guides/RBAC_IMPLEMENTATION_SUMMARY.md) - Technical implementation details

├── Dockerfile- [Selectors & Services Guide](guides/RBAC_SELECTORS_SERVICES_GUIDE.md) - Architecture patterns

├── Makefile

└── requirements.txt### Configuration

```- [Settings Configuration](guides/SETTINGS_CONFIGURATION_GUIDE.md) - Django settings explained

- [CORS Configuration](guides/DJANGO_CORS_HEADERS_GUIDE.md) - Frontend integration setup

## 🔐 RBAC System- [Multiple Frontends](guides/MULTIPLE_FRONTEND_SUPPORT.md) - Supporting multiple frontend apps



### Hierarchical Roles### Deployment

- [GitHub Checklist](guides/GITHUB_CHECKLIST.md) - Pre-deployment checklist

| Role | Level | Description |- [Docker Fixes](guides/DOCKER_FIXES.md) - Common Docker issues and solutions

|------|-------|-------------|

| **Super Admin** | 80 | Full system access |## Development Setup

| **Admin** | 70 | Administrative access |

| **Manager** | 60 | Team management |### Local Development (without Docker)

| **Support Agent** | 50 | Customer support |

| **Content Manager** | 40 | Content management |1. **Create virtual environment**

| **Moderator** | 30 | Content moderation |```bash

| **Premium User** | 20 | Enhanced features |python -m venv venv

| **User** | 10 | Standard access |source venv/bin/activate  # On Windows: venv\Scripts\activate

| **Guest** | 0 | Basic read access |```



### Permission Categories2. **Install dependencies**

```bash

- **User Management** - CRUD operations on userspip install -r requirements.txt

- **Content Management** - Content operations```

- **Analytics** - View and export analytics

- **Settings** - System configuration3. **Set up environment variables**

- **Billing** - Billing and invoices```bash

- **Support** - Ticket managementcp .env.example .env

- **API Access** - API permissions# Configure your local database and Redis settings

- **Admin Panel** - System administration```



> See [`guides/rbac/RBAC_GUIDE.md`](guides/rbac/RBAC_GUIDE.md) for detailed documentation4. **Run migrations**

```bash

## 🌐 Access Pointspython manage.py migrate

python manage.py seed_rbac  # Seed RBAC roles and permissions

| Service | URL |```

|---------|-----|

| **Application** | http://localhost:8000 |5. **Create superuser**

| **Admin Panel** | http://localhost:8000/admin/ |```bash

| **API Root** | http://localhost:8000/api/ |python manage.py createsuperuser

| **Swagger UI** | http://localhost:8000/api/schema/swagger/ |```

| **ReDoc** | http://localhost:8000/api/schema/redoc/ |

| **OpenAPI Schema** | http://localhost:8000/api/schema/ |6. **Run development server**

```bash

## 🔧 Developmentpython manage.py runserver

```

### Development Mode (Hot-Reload)

## RBAC System

```bash

make devThe application includes a comprehensive Role-Based Access Control system with:

```

### Predefined Roles (Hierarchical)

Features:

- ✅ Auto-reload on code changes1. **Guest** (Level 0) - Basic read access

- ✅ Django development server2. **User** (Level 10) - Standard user permissions

- ✅ Detailed error pages3. **Premium User** (Level 20) - Enhanced features

- ✅ Development tools (iPython, django-debug-toolbar)4. **Moderator** (Level 30) - Content moderation

- ✅ File watching with `docker compose --watch`5. **Content Manager** (Level 40) - Content management

6. **Support Agent** (Level 50) - Customer support

### Environment Configuration7. **Manager** (Level 60) - Team management

8. **Admin** (Level 70) - Administrative access

Create `.env` from `.env.example`:9. **Super Admin** (Level 80) - Full system access



```env### Permission Categories

# Build Configuration

BUILD_TARGET=development  # or 'production'- **User Management** - View, create, update, delete users

DEBUG=True- **Content Management** - CRUD operations on content

- **Analytics** - View and export analytics

# Django- **Settings** - System configuration

SECRET_KEY=your-secret-key-here- **Billing** - Billing and invoices

ALLOWED_HOSTS=localhost,127.0.0.1- **Support** - Ticket management

- **API Access** - API read/write/admin

# Database- **Admin Panel** - System administration

DB_NAME=replycompass

DB_USER=replycompass_userSee [apps/rbac/README.md](apps/rbac/README.md) for detailed documentation.

DB_PASSWORD=change-this-password

## Docker Commands

# Redis

REDIS_PASSWORD=change-this-password```bash

# Start all services

# JWTdocker compose up -d

JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60

JWT_REFRESH_TOKEN_LIFETIME_DAYS=7# View logs

```docker compose logs -f



> See [`.env.example`](.env.example) for all configuration options# Stop services

docker compose down

## 🧪 Testing

# Rebuild images

```bashdocker compose build --no-cache

# Run all tests

make test# Run Django commands

docker compose exec web python manage.py <command>

# Run specific app tests

make test-app APP=rbac# Create migrations

docker compose exec web python manage.py makemigrations

# Run with coverage

make coverage# Run migrations

```docker compose exec web python manage.py migrate



## 📦 Production Deployment# Create superuser

docker compose exec web python manage.py createsuperuser

### 1. Configure Environment

# Run tests

```envdocker compose exec web python manage.py test

BUILD_TARGET=production```

DEBUG=False

SECRET_KEY=<strong-random-secret>## Project Structure

ALLOWED_HOSTS=yourdomain.com

```

# Use external managed servicesreplycompass/

DB_HOST=your-postgres-host├── apps/

REDIS_HOST=your-redis-host│   ├── accounts/       # User authentication and profiles

```│   ├── core/          # Core utilities and base classes

│   └── rbac/          # Role-Based Access Control system

### 2. Deploy├── config/            # Project settings and URLs

│   ├── settings/

```bash│   │   ├── base.py

make prod-build│   │   ├── local.py

```│   │   ├── production.py

│   │   └── docker.py

### Production Checklist│   ├── urls.py

│   ├── wsgi.py

- [ ] Change `SECRET_KEY` to strong random value│   └── asgi.py

- [ ] Set `DEBUG=False`├── scripts/           # Deployment and utility scripts

- [ ] Configure `ALLOWED_HOSTS` with your domain├── static/            # Static files

- [ ] Use strong database passwords├── media/             # User uploaded files

- [ ] Enable HTTPS/SSL├── logs/              # Application logs

- [ ] Set up external PostgreSQL (AWS RDS, etc.)├── docker-compose.yml          # Full production setup

- [ ] Set up external Redis├── docker-compose.simple.yml   # Simplified dev setup

- [ ] Configure cloud storage for media files (S3, Cloudinary)├── docker-compose.dev.yml      # Development with MailHog

- [ ] Set up error tracking (Sentry)├── Dockerfile

- [ ] Configure logging└── requirements.txt

- [ ] Set up monitoring```

- [ ] Enable backups

## Environment Variables

> See [`guides/deployment/GITHUB_CHECKLIST.md`](guides/deployment/GITHUB_CHECKLIST.md) for complete checklist

Key environment variables (see `.env.example` for full list):

## 📚 Documentation

```env

### Quick Access# Django

SECRET_KEY=your-secret-key

| Category | Guide |DEBUG=False

|----------|-------|ALLOWED_HOSTS=localhost,127.0.0.1

| **Getting Started** | [`guides/development/DEVELOPMENT.md`](guides/development/DEVELOPMENT.md) |

| **Docker** | [`guides/docker/DOCKER_SETUP_GUIDE.md`](guides/docker/DOCKER_SETUP_GUIDE.md) |# Database

| **RBAC** | [`guides/rbac/RBAC_GUIDE.md`](guides/rbac/RBAC_GUIDE.md) |DB_NAME=replycompass

| **Configuration** | [`guides/configuration/SETTINGS_CONFIGURATION_GUIDE.md`](guides/configuration/SETTINGS_CONFIGURATION_GUIDE.md) |DB_USER=replycompass_user

DB_PASSWORD=changeme

### All GuidesDB_HOST=db

DB_PORT=5432

```

guides/# Redis

├── development/          # Development workflowsREDIS_HOST=redis

│   ├── DEVELOPMENT.mdREDIS_PORT=6379

│   └── SETUP_GUIDE_MANUAL.mdREDIS_PASSWORD=changeme

├── docker/              # Docker & containerization

│   ├── DOCKER_SETUP_GUIDE.md# JWT

│   ├── DOCKER_WATCH_SETUP.mdJWT_ACCESS_TOKEN_LIFETIME_MINUTES=60

│   ├── DOCKER_FIXES.mdJWT_REFRESH_TOKEN_LIFETIME_DAYS=7

│   └── QUICK_REFERENCE.md```

├── rbac/                # RBAC system

│   ├── RBAC_GUIDE.md## API Documentation

│   ├── RBAC_IMPLEMENTATION_SUMMARY.md

│   ├── RBAC_QUICK_REFERENCE.mdAccess the interactive API documentation at:

│   └── RBAC_SELECTORS_SERVICES_GUIDE.md

├── configuration/       # Settings & config- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/

│   ├── SETTINGS_CONFIGURATION_GUIDE.md- **ReDoc**: http://localhost:8000/api/schema/redoc/

│   ├── DJANGO_CORS_HEADERS_GUIDE.md- **OpenAPI Schema**: http://localhost:8000/api/schema/

│   └── MULTIPLE_FRONTEND_SUPPORT.md

└── deployment/          # Deployment & production## Testing

    └── GITHUB_CHECKLIST.md

``````bash

# Run all tests

## 🛠️ Troubleshootingdocker compose exec web python manage.py test



### Common Issues# Run specific app tests

docker compose exec web python manage.py test apps.rbac

**Services won't start:**

```bash# Run with coverage

make health  # Check service healthdocker compose exec web pytest --cov=apps

make clean-soft && make dev-build  # Clean rebuild```

```

## Deployment

**Database errors:**

```bash### Production Considerations

make migrate  # Run migrations

make seed     # Reseed RBAC data1. **Security**:

```   - Change `SECRET_KEY` to a strong random value

   - Set `DEBUG=False`

**Permission denied:**   - Update `ALLOWED_HOSTS` with your domain

```bash   - Use strong database passwords

docker compose down -v  # Remove volumes   - Enable HTTPS/SSL

make clean-soft && make dev  # Fresh start

```2. **Database**:

   - Use managed PostgreSQL service (AWS RDS, DigitalOcean, etc.)

> See [`guides/docker/DOCKER_FIXES.md`](guides/docker/DOCKER_FIXES.md) for more solutions   - Enable automated backups

   - Set up replication if needed

## 🤝 Contributing

3. **Static/Media Files**:

1. Fork the repository   - Use cloud storage (AWS S3, Cloudinary, etc.)

2. Create feature branch (`git checkout -b feature/AmazingFeature`)   - Configure CDN for static files

3. Commit changes (`git commit -m 'Add AmazingFeature'`)

4. Push to branch (`git push origin feature/AmazingFeature`)4. **Monitoring**:

5. Open Pull Request   - Set up Sentry for error tracking

   - Configure logging aggregation

## 📄 License   - Monitor server resources



[Your License Here]## License



## 📞 Support[Your License Here]



- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)## Contributing

- **Documentation**: [`guides/`](guides/)

- **Email**: support@yourapp.com1. Fork the repository

2. Create your feature branch (`git checkout -b feature/AmazingFeature`)

---3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)

4. Push to the branch (`git push origin feature/AmazingFeature`)

Made with ❤️ by [Your Name/Team]5. Open a Pull Request


## Support

For issues and questions, please open an issue on GitHub.
