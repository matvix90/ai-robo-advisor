#!/bin/bash
# Docker setup validation script for AI Robo Advisor
set -euo pipefail

# Exit codes & Configuration
readonly EC_DOCKER=1 EC_COMPOSE=2 EC_ENV=3 EC_KEYS=4 EC_API=5
readonly RED='\033[0;31m' GREEN='\033[0;32m' YELLOW='\033[1;33m' BLUE='\033[0;34m' NC='\033[0m'
QUIET=false VERBOSE=false COMPOSE_CMD=""

# Logging functions
log() { [[ $QUIET == false ]] && echo -e "${BLUE}[INFO]${NC} $1"; }
success() { [[ $QUIET == false ]] && echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
verbose() { [[ $VERBOSE == true ]] && echo -e "${BLUE}[VERBOSE]${NC} $1"; }

usage() {
    cat << 'EOF'
🐳 AI Robo Advisor Docker Setup Validation

USAGE: ./docker/validate-setup.sh [OPTIONS]

OPTIONS:
    -h, --help     Show help
    -q, --quiet    Errors only
    -v, --verbose  Debug output

CHECKS: Docker, Compose, .env, API keys, connectivity

EXIT CODES: 0=Success, 1=Docker, 2=Compose, 3=Env, 4=Keys, 5=API

EXAMPLES:
    ./docker/validate-setup.sh           # Full validation
    ./docker/validate-setup.sh --quiet   # Errors only
    ../docker-run.sh validate            # Via wrapper
EOF
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help) usage; exit 0 ;;
            -q|--quiet) QUIET=true; shift ;;
            -v|--verbose) VERBOSE=true; shift ;;
            *) error "Unknown option: $1"; usage; exit 1 ;;
        esac
    done
}

# Setup environment
setup_env() {
    cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" || { error "Failed to find project root"; exit $EC_ENV; }
    verbose "Working directory: $(pwd)"
}

# Validation functions
check_docker() {
    log "Checking Docker..."
    command -v docker >/dev/null || { error "Docker not found. Install: https://docs.docker.com/engine/install/"; exit $EC_DOCKER; }
    docker info >/dev/null 2>&1 || { error "Docker daemon not running. Start Docker and try again."; exit $EC_DOCKER; }
    success "Docker: $(docker --version | cut -d' ' -f3 | tr -d ',')"
}

check_compose() {
    log "Checking Docker Compose..."
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
        success "Docker Compose: $(docker-compose --version | cut -d' ' -f3 | tr -d ',')"
    elif docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
        success "Docker Compose: $(docker compose version --short)"
    else
        error "Docker Compose not found. Install: https://docs.docker.com/compose/install/"
        exit $EC_COMPOSE
    fi
}

check_env() {
    log "Checking environment..."
    if [[ ! -f .env ]]; then
        [[ -f .env.example ]] && cp .env.example .env && warn "Created .env from example. Edit with your API keys."
        [[ ! -f .env ]] && { error ".env missing and no .env.example found"; exit $EC_ENV; }
    fi
    success ".env file found"
}

get_env() { sed -n "s/^${1}=//p" .env | tail -n1 | sed 's/^"//;s/"$//'; }
is_empty() { [[ -z "$1" || "$1" == your-*-api-key ]]; }

check_keys() {
    log "Validating API keys..."
    local polygon google openai anthropic
    polygon=$(get_env POLYGON_API_KEY)
    google=$(get_env GOOGLE_API_KEY)
    openai=$(get_env OPENAI_API_KEY)
    anthropic=$(get_env ANTHROPIC_API_KEY)
    
    is_empty "$polygon" && { error "POLYGON_API_KEY required"; exit $EC_KEYS; }
    
    local llm_found=false
    for key in "$google" "$openai" "$anthropic"; do
        ! is_empty "$key" && llm_found=true && break
    done
    [[ $llm_found == false ]] && { error "At least one LLM API key required (Google/OpenAI/Anthropic)"; exit $EC_KEYS; }
    
    local configured=()
    ! is_empty "$polygon" && configured+=(POLYGON)
    ! is_empty "$google" && configured+=(GOOGLE)
    ! is_empty "$openai" && configured+=(OPENAI)
    ! is_empty "$anthropic" && configured+=(ANTHROPIC)
    success "API keys configured: ${configured[*]}"
}

test_api() {
    log "Testing API connectivity..."
    command -v curl >/dev/null || { warn "curl not found, skipping connectivity tests"; return 0; }
    
    local polygon google status
    polygon=$(get_env POLYGON_API_KEY)
    google=$(get_env GOOGLE_API_KEY)
    
    if ! is_empty "$polygon"; then
        status=$(curl -s -o /dev/null -w '%{http_code}' "https://api.polygon.io/v3/reference/tickers?limit=1&apiKey=${polygon}")
        if [[ "$status" == "200" ]]; then
            success "Polygon API: Connected"
        else
            error "Polygon API failed (HTTP $status)"
            exit $EC_API
        fi
    fi
    
    if ! is_empty "$google"; then
        status=$(curl -s -o /dev/null -w '%{http_code}' "https://generativelanguage.googleapis.com/v1beta/models?key=${google}")
        if [[ "$status" == "200" ]]; then
            success "Google AI API: Connected"
        else
            error "Google AI API failed (HTTP $status)"
            exit $EC_API
        fi
    fi
}

check_config() {
    log "Validating Docker configuration..."
    if (cd docker && $COMPOSE_CMD config >/dev/null 2>&1); then
        success "Docker Compose configuration valid"
        return 0
    else
        warn "Docker Compose config issue"
        return 1
    fi
}

check_images() {
    log "Checking Docker images..."
    if (cd docker && $COMPOSE_CMD images 2>/dev/null | grep -q ai-robo-advisor); then
        success "Docker images found"
        return 0
    else
        warn "No Docker images built (normal on first setup)"
        return 1
    fi
}

# Main execution
main() {
    parse_args "$@"
    setup_env
    
    [[ $QUIET == false ]] && echo "🐳 AI Robo Advisor Docker Setup Validation" && echo "================================================"
    
    # Critical validations - must pass
    check_docker
    check_compose
    check_env
    check_keys
    test_api
    
    [[ $QUIET == false ]] && echo "================================================"
    success "🎉 Docker setup validation passed!"
    
    if [[ $QUIET == false ]]; then
        echo ""
        echo "✅ Ready to use! Try:"
        echo "  ../docker-run.sh           # Start application"
        echo "  ../docker-run.sh test      # Run tests"
        echo "  ../docker-run.sh shell     # Interactive shell"
    fi
}

# Ensure clean exit
main "$@"
exit 0