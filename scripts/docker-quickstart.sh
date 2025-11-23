#!/bin/bash
# Quick Start Script for ReplyCompass Docker Setup

echo "🚀 ReplyCompass Docker Quick Start"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.docker..."
    cp .env.docker .env
    echo "⚠️  Please edit .env file with your configuration before continuing"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Ask user which environment to start
echo "Which environment do you want to start?"
echo "1) Development (with hot reload, debug tools)"
echo "2) Production (optimized, with Nginx)"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "🔧 Starting Development Environment..."
        echo ""
        docker-compose -f docker-compose.dev.yml down -v
        docker-compose -f docker-compose.dev.yml build
        docker-compose -f docker-compose.dev.yml up -d
        
        echo ""
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        echo ""
        echo "🗄️  Running migrations..."
        docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
        
        echo ""
        echo "🌱 Seeding RBAC data..."
        docker-compose -f docker-compose.dev.yml exec web python manage.py seed_rbac
        
        echo ""
        echo "✅ Development environment is ready!"
        echo ""
        echo "📍 Access your application:"
        echo "   - Web: http://localhost:8000"
        echo "   - Admin: http://localhost:8000/admin/"
        echo "   - API: http://localhost:8000/api/"
        echo "   - MailHog: http://localhost:8025"
        echo ""
        echo "🛠️  Useful commands:"
        echo "   - View logs: docker-compose -f docker-compose.dev.yml logs -f"
        echo "   - Create superuser: docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser"
        echo "   - Django shell: docker-compose -f docker-compose.dev.yml exec web python manage.py shell"
        echo "   - Stop: docker-compose -f docker-compose.dev.yml down"
        ;;
    2)
        echo ""
        echo "🚀 Starting Production Environment..."
        echo ""
        docker-compose down -v
        docker-compose build
        docker-compose up -d
        
        echo ""
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        echo ""
        echo "🗄️  Running migrations..."
        docker-compose exec web python manage.py migrate
        
        echo ""
        echo "🌱 Seeding RBAC data..."
        docker-compose exec web python manage.py seed_rbac
        
        echo ""
        echo "📦 Collecting static files..."
        docker-compose exec web python manage.py collectstatic --noinput
        
        echo ""
        echo "✅ Production environment is ready!"
        echo ""
        echo "📍 Access your application:"
        echo "   - Web: http://localhost (via Nginx)"
        echo "   - Admin: http://localhost/admin/"
        echo "   - API: http://localhost/api/"
        echo ""
        echo "🛠️  Useful commands:"
        echo "   - View logs: docker-compose logs -f"
        echo "   - Create superuser: docker-compose exec web python manage.py createsuperuser"
        echo "   - Restart: docker-compose restart"
        echo "   - Stop: docker-compose down"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete! Happy coding!"
