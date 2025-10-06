#!/bin/bash
# Docker setup validation script for AI Robo Advisor

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_separator() {
    echo "================================================"
}

echo "🐳 AI Robo Advisor Docker Setup Validation"
print_separator

# Check if Docker is installed
print_info "Checking Docker installation..."
if command -v docker >/dev/null 2>&1; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker found: $DOCKER_VERSION"
else
    print_error "Docker not found. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
print_info "Checking Docker Compose..."
if command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1; then
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_VERSION=$(docker-compose --version)
    else
        COMPOSE_VERSION=$(docker compose version)
    fi
    print_success "Docker Compose found: $COMPOSE_VERSION"
else
    print_error "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Check if .env file exists
print_info "Checking environment configuration..."
if [ -f .env ]; then
    print_success ".env file found"
    
    # Check for required API keys
    if grep -q "POLYGON_API_KEY=your-polygon-api-key" .env || grep -q "GOOGLE_API_KEY=your-google-api-key" .env; then
        print_warning "Please update your API keys in .env file before running the application"
    else
        print_success "API keys appear to be configured"
    fi
else
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_info "Please edit .env file with your API keys"
    else
        print_error ".env.example not found"
        exit 1
    fi
fi

# Test Docker build
print_info "Testing Docker build..."
if docker-compose build >/dev/null 2>&1; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

# Test container run
print_info "Testing container execution..."
if docker-compose run --rm ai-robo-advisor python -c "import main; print('Application import successful')" >/dev/null 2>&1; then
    print_success "Container can run the application"
else
    print_error "Failed to run application in container"
    exit 1
fi

# Test pytest availability
print_info "Testing development tools..."
if docker-compose run --rm ai-robo-advisor pytest --version >/dev/null 2>&1; then
    print_success "Development tools (pytest) available"
else
    print_warning "Development tools not available"
fi

print_separator
print_success "🎉 Docker setup validation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys if not done already"
echo "2. Run: docker-compose up"
echo "3. Or use: ./docker/docker-helper.sh interactive"
echo ""
echo "For help: ./docker/docker-helper.sh help"