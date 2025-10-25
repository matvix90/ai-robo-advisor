#!/bin/bash
# Docker convenience script for AI Robo Advisor
# Usage: ./docker-run.sh [command] [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Ensure we're in project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for docker compose command (newer) or docker-compose (legacy)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    print_error "Neither 'docker compose' nor 'docker-compose' found!"
    echo "Please install Docker and Docker Compose"
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Function to show usage
usage() {
    echo "🐳 AI Robo Advisor Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Quick Commands:"
    echo "  $0                       # Start development environment"
    echo "  $0 up                    # Start development environment" 
    echo "  $0 down                  # Stop all containers"
    echo "  $0 logs                  # View logs"
    echo "  $0 shell                 # Interactive shell"
    echo "  $0 test                  # Run tests"
    echo ""
    echo "Advanced Commands:"
    echo "  $0 interactive           # Interactive development container"
    echo "  $0 prod                  # Production mode"
    echo "  $0 build                 # Build images"
    echo "  $0 clean                 # Clean up containers and images"
    echo "  $0 validate              # Validate Docker setup"
    echo ""
    echo "Options:"
    echo "  --build                  # Force rebuild images"
    echo "  --detach, -d             # Run in background"
    echo ""
    echo "Examples:"
    echo "  $0 up --build            # Start with fresh build"
    echo "  $0 up --detach           # Start in background"
    echo "  $0 logs -f ai-robo-advisor  # Follow logs for specific service"
    echo ""
    echo "For more details, see: docker/README.md"
}

# Source environment variables if .env exists
if [ -f ".env" ]; then
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
    print_info "📄 Loaded environment variables from .env"
fi

# Change to docker directory for compose operations
cd docker

# Default to up if no command provided
if [ $# -eq 0 ]; then
    print_info "� Starting AI Robo Advisor development environment..."
    exec $DOCKER_COMPOSE up --build
fi

# Handle commands
case "${1:-help}" in
    up|start)
        shift
        print_info "🚀 Starting development environment..."
        exec $DOCKER_COMPOSE up "$@"
        ;;
    down|stop)
        shift
        print_info "🛑 Stopping containers..."
        exec $DOCKER_COMPOSE down "$@"
        ;;
    logs)
        shift
        exec $DOCKER_COMPOSE logs "$@"
        ;;
    shell|bash)
        print_info "🐚 Opening interactive shell..."
        exec $DOCKER_COMPOSE exec ai-robo-advisor /bin/bash
        ;;
    test)
        shift
        print_info "🧪 Running tests..."
        exec $DOCKER_COMPOSE run --rm ai-robo-advisor pytest tests/ -v "$@"
        ;;
    interactive|dev)
        print_info "🔧 Starting interactive development container..."
        exec $DOCKER_COMPOSE --profile interactive up ai-robo-advisor-interactive
        ;;
    prod|production)
        shift
        print_info "🚀 Starting production environment..."
        exec $DOCKER_COMPOSE --profile production up "$@" ai-robo-advisor-prod
        ;;
    build)
        shift
        print_info "🏗️ Building Docker images..."
        exec $DOCKER_COMPOSE build "$@"
        ;;
    clean)
        print_warning "This will remove containers, images, and volumes"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            exec $DOCKER_COMPOSE down -v --rmi all --remove-orphans
        else
            print_info "Clean cancelled"
        fi
        ;;
    validate)
        shift
        print_info "🔍 Validating Docker setup..."
        cd .. && exec ./docker/validate-setup.sh "$@"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        # Pass through any other docker-compose commands
        print_info "🐳 Running: $DOCKER_COMPOSE $*"
        exec $DOCKER_COMPOSE "$@"
        ;;
esac