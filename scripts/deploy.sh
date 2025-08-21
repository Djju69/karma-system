#!/bin/bash

# Karma System Bot Deployment Script

set -e

echo "🚀 Starting Karma System deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found! Please create it first."
    exit 1
fi

print_status "Checking environment variables..."
source .env

required_vars=("BOT_TOKEN" "DATABASE_URL" "FERNET_KEY_HEX")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set!"
        exit 1
    fi
done

# Stop existing services
print_status "Stopping existing services..."
docker-compose down || true

# Pull latest changes (if using git)
if [ -d ".git" ]; then
    print_status "Pulling latest changes from git..."
    git pull origin main || print_warning "Git pull failed, continuing with local files"
fi

# Build and start services
print_status "Building and starting services..."
docker-compose up -d --build

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Run database migrations
print_status "Running database migrations..."
docker-compose exec -T api alembic upgrade head

# Check service health
print_status "Checking service health..."
sleep 5

# Check bot status
if docker-compose ps bot | grep -q "Up"; then
    print_status "✅ Bot is running"
else
    print_error "❌ Bot failed to start"
    docker-compose logs bot
    exit 1
fi

# Check API status
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ API is healthy"
else
    print_warning "⚠️ API health check failed"
fi

# Check database connection
if docker-compose exec -T postgres pg_isready -U karma_user -d karma_db > /dev/null 2>&1; then
    print_status "✅ Database is ready"
else
    print_error "❌ Database connection failed"
fi

# Check Redis connection
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_status "✅ Redis is ready"
else
    print_error "❌ Redis connection failed"
fi

print_status "🎉 Deployment completed!"
print_status "Bot logs: docker-compose logs -f bot"
print_status "API docs: http://localhost:8000/docs"
print_status "Grafana: http://localhost:3000 (admin/admin)"
