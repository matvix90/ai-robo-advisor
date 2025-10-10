#!/bin/bash
# Docker convenience script for AI Robo Advisor

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_info "Please edit .env file with your API keys before running the application"
        else
            print_error ".env.example file not found. Please create .env manually"
            exit 1
        fi
    fi
}

# Function to show usage
usage() {
    echo "AI Robo Advisor Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build       Build Docker images"
    echo "  up          Start the application (development mode)"
    echo "  up-prod     Start the application (production mode)"
    echo "  interactive Start interactive shell container"
    echo "  down        Stop and remove containers"
    echo "  logs        Show application logs"
    echo "  shell       Open shell in running container"
    echo "  test        Run tests in container"
    echo "  clean       Remove all containers, images and volumes"
    echo "  status      Show container status"
    echo ""
    echo "Options:"
    echo "  --rebuild   Force rebuild images"
    echo "  --help, -h  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 up                    # Start in development mode"
    echo "  $0 interactive           # Start interactive session"
    echo "  $0 up-prod               # Start in production mode"
    echo "  $0 test                  # Run tests"
    echo "  $0 shell                 # Open shell in running container"
}

# Function to build images
build_images() {
    print_info "Building Docker images..."
    docker-compose build "$@"
    print_success "Docker images built successfully"
}

# Function to start development mode
start_dev() {
    check_env_file
    print_info "Starting AI Robo Advisor in development mode..."
    docker-compose up "$@" ai-robo-advisor
}

# Function to start production mode
start_prod() {
    check_env_file
    print_info "Starting AI Robo Advisor in production mode..."
    docker-compose --profile production up "$@" ai-robo-advisor-prod
}

# Function to start interactive mode
start_interactive() {
    check_env_file
    print_info "Starting AI Robo Advisor in interactive mode..."
    print_info "You can run the application with: python -m main"
    docker-compose --profile interactive up ai-robo-advisor-interactive
}

# Function to stop containers
stop_containers() {
    print_info "Stopping containers..."
    docker-compose down
    print_success "Containers stopped"
}

# Function to show logs
show_logs() {
    docker-compose logs -f "$@"
}

# Function to open shell
open_shell() {
    container_name="ai-robo-advisor-dev"
    if ! docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        print_warning "Container ${container_name} is not running. Starting interactive container..."
        start_interactive
    else
        print_info "Opening shell in ${container_name}..."
        docker exec -it "${container_name}" /bin/bash
    fi
}

# Function to run tests
run_tests() {
    check_env_file
    print_info "Running tests in container..."
    docker-compose run --rm ai-robo-advisor pytest tests/ -v
    print_success "Tests completed"
}

# Function to clean up
clean_up() {
    print_warning "This will remove ALL containers, images, and volumes for this project"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up Docker resources..."
        docker-compose down -v --rmi all --remove-orphans
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

# Function to show status
show_status() {
    print_info "Container status:"
    docker-compose ps
    echo ""
    print_info "Images:"
    docker images | grep -E "(ai-robo-advisor|python)"
}

# Parse command line arguments
REBUILD=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --rebuild)
            REBUILD="--build"
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

# Main command handling
case "${1:-help}" in
    build)
        shift
        build_images "$@"
        ;;
    up)
        shift
        start_dev $REBUILD "$@"
        ;;
    up-prod)
        shift
        start_prod $REBUILD "$@"
        ;;
    interactive)
        shift
        start_interactive
        ;;
    down)
        stop_containers
        ;;
    logs)
        shift
        show_logs "$@"
        ;;
    shell)
        open_shell
        ;;
    test)
        run_tests
        ;;
    clean)
        clean_up
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        usage
        exit 1
        ;;
esac