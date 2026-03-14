#!/bin/bash
# Setup script for local development

set -e

echo "================================"
echo "Resume Builder - Local Setup"
echo "================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Create storage directory
mkdir -p storage

# Start services
echo ""
echo "🚀 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."

BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
if [ "$BACKEND_HEALTH" = "200" ]; then
    echo "✅ Backend is healthy (http://localhost:8000)"
else
    echo "⚠️  Backend health check returned $BACKEND_HEALTH"
fi

FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")
if [ "$FRONTEND_HEALTH" = "200" ] || [ "$FRONTEND_HEALTH" = "000" ]; then
    echo "✅ Frontend is running (http://localhost:3000)"
else
    echo "⚠️  Frontend health check returned $FRONTEND_HEALTH"
fi

echo ""
echo "================================"
echo "Setup Complete! 🎉"
echo "================================"
echo ""
echo "Services:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:3000"
echo "  - Database: localhost:5432"
echo "  - PgAdmin: http://localhost:5050"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Sign up for an account"
echo "3. Start adding career data"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f"
