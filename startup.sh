#!/bin/bash
# NBFCSUITE Docker Compose Startup Script

set -e

echo "🚀 Starting NBFCSUITE with Docker Compose..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/postgres
mkdir -p logs

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose pull

# Build services
echo "🔨 Building services..."
docker-compose build

# Start services
echo "🏗️  Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

services=(
    "postgres:5432"
    "auth-service:8000"
    "los-service:8000"
    "lms-service:8000"
    "collections-service:8000"
    "customer-service:8000"
    "findna-service:8000"
    "web-app:3000"
)

for service in "${services[@]}"; do
    host=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if [ "$host" == "postgres" ]; then
        echo -n "Checking $host:$port... "
        if docker-compose exec -T postgres pg_isready -U nbfc_user > /dev/null 2>&1; then
            echo "✅"
        else
            echo "⏳ (still starting)"
        fi
    else
        echo -n "Checking $host:$port... "
        if curl -s http://localhost:$port/health > /dev/null 2>&1; then
            echo "✅"
        else
            echo "⏳ (still starting)"
        fi
    fi
done

# Print access information
echo ""
echo "✅ NBFCSUITE is running!"
echo ""
echo "📍 Service URLs:"
echo "   - Web App:           http://localhost:3000"
echo "   - Auth Service:      http://localhost:8001"
echo "   - LOS Service:       http://localhost:8002"
echo "   - LMS Service:       http://localhost:8003"
echo "   - Collections:       http://localhost:8004"
echo "   - Customer Service:  http://localhost:8005"
echo "   - FinDNA Service:    http://localhost:8006"
echo "   - PostgreSQL:        localhost:5432"
echo ""
echo "📊 Database Credentials:"
echo "   - User: nbfc_user"
echo "   - Password: nbfc_pass"
echo "   - Database: nbfcsuite"
echo ""
echo "📖 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Login with test credentials"
echo "   3. Check logs: docker-compose logs -f <service-name>"
echo "   4. Stop services: docker-compose down"
echo ""
echo "🎯 Useful commands:"
echo "   docker-compose ps              # View running services"
echo "   docker-compose logs -f         # View all logs"
echo "   docker-compose logs -f auth    # View auth service logs"
echo "   docker-compose down            # Stop all services"
echo "   docker-compose down -v         # Stop and remove volumes"
echo ""
