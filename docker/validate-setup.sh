#!/bin/bash
# Enhanced Docker setup validation script for AI Robo Advisor
# - Checks Docker/Compose availability and daemon status
# - Validates required/optional environment variables
# - Tests API connectivity for Polygon and Google AI (if keys provided)
# - Builds images and validates app import in dev and prod containers
# - Returns distinct exit codes per failure scenario

# Exit codes
EC_DOCKER_NOT_INSTALLED=1
EC_DOCKER_DAEMON_NOT_RUNNING=2
EC_COMPOSE_NOT_AVAILABLE=3
EC_ENV_MISSING=4
EC_REQUIRED_KEYS_MISSING=5
EC_API_CONNECTIVITY_FAILED=6
EC_DOCKER_BUILD_FAILED=7
EC_CONTAINER_RUN_FAILED=8
EC_DEVTOOLS_MISSING=9

set -u  # Treat unset variables as an error

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
print_separator() { echo "================================================"; }

# Ensure we run from project root (script is in docker/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || {
  print_error "Failed to change directory to project root at $PROJECT_ROOT";
  exit $EC_ENV_MISSING;
}

echo "🐳 AI Robo Advisor Docker Setup Validation"
print_separator

# Check Docker installation
print_info "Checking Docker installation..."
if command -v docker >/dev/null 2>&1; then
  DOCKER_VERSION=$(docker --version)
  print_success "Docker found: $DOCKER_VERSION"
else
  print_error "Docker not found. Install Docker first: https://docs.docker.com/engine/install/"
  exit $EC_DOCKER_NOT_INSTALLED
fi

# Check Docker daemon
print_info "Checking Docker daemon..."
if docker info >/dev/null 2>&1; then
  print_success "Docker daemon is running"
else
  print_error "Docker daemon is not running. Start it and try again."
  echo "Hints:"
  echo "- Linux: sudo systemctl start docker && sudo systemctl enable docker"
  echo "- macOS/Windows: Start Docker Desktop"
  exit $EC_DOCKER_DAEMON_NOT_RUNNING
fi

# Determine Compose command
print_info "Checking Docker Compose..."
COMPOSE_CMD=""
if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
  COMPOSE_VERSION=$(docker-compose --version)
  print_success "Docker Compose v1 found: $COMPOSE_VERSION"
elif docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
  COMPOSE_VERSION=$(docker compose version)
  print_success "Docker Compose v2 found: $COMPOSE_VERSION"
else
  print_error "Docker Compose not found. Install Compose: https://docs.docker.com/compose/install/"
  exit $EC_COMPOSE_NOT_AVAILABLE
fi

# Ensure .env exists (create from example if available)
print_info "Checking environment configuration (.env)..."
if [ -f .env ]; then
  print_success ".env file found"
else
  if [ -f .env.example ]; then
    print_warning ".env not found. Creating from .env.example..."
    cp .env.example .env
    print_info "Edit .env and set your API keys before running the application."
  else
    print_error ".env file missing and .env.example not found"
    exit $EC_ENV_MISSING
  fi
fi

# Helper to parse a key's last occurrence value from .env (supports values with '=')
get_env_value() {
  local key="$1"
  sed -n "s/^${key}=//p" .env | tail -n1
}

# Load values without exporting into shell env
POLYGON_API_KEY_VAL="$(get_env_value POLYGON_API_KEY)"
GOOGLE_API_KEY_VAL="$(get_env_value GOOGLE_API_KEY)"
OPENAI_API_KEY_VAL="$(get_env_value OPENAI_API_KEY)"
ANTHROPIC_API_KEY_VAL="$(get_env_value ANTHROPIC_API_KEY)"

# Detect placeholders or empties
is_placeholder_or_empty() {
  local v="$1"
  if [ -z "$v" ]; then return 0; fi
  case "$v" in
    your-*-api-key) return 0 ;;
    *) return 1 ;;
  esac
}

print_info "Validating required API keys..."
missing_reason=""

if is_placeholder_or_empty "$POLYGON_API_KEY_VAL"; then
  missing_reason+="- POLYGON_API_KEY is required and must be set in .env\n"
fi

has_llm=false
if ! is_placeholder_or_empty "$GOOGLE_API_KEY_VAL"; then has_llm=true; fi
if ! is_placeholder_or_empty "$OPENAI_API_KEY_VAL"; then has_llm=true; fi
if ! is_placeholder_or_empty "$ANTHROPIC_API_KEY_VAL"; then has_llm=true; fi

if [ "$has_llm" = false ]; then
  missing_reason+="- At least one LLM provider key is required: GOOGLE_API_KEY or OPENAI_API_KEY or ANTHROPIC_API_KEY\n"
fi

if [ -n "$missing_reason" ]; then
  print_error "Missing required configuration:\n$missing_reason"
  echo "Fix: Edit .env and provide valid keys."
  exit $EC_REQUIRED_KEYS_MISSING
else
  configured=( )
  [ ! -z "$POLYGON_API_KEY_VAL" ] && configured+=("POLYGON_API_KEY")
  [ ! -z "$GOOGLE_API_KEY_VAL" ] && configured+=("GOOGLE_API_KEY")
  [ ! -z "$OPENAI_API_KEY_VAL" ] && configured+=("OPENAI_API_KEY")
  [ ! -z "$ANTHROPIC_API_KEY_VAL" ] && configured+=("ANTHROPIC_API_KEY")
  print_success "Required keys present. Configured: ${configured[*]}"
fi

# Connectivity tests (optional but recommended)
print_info "Testing API connectivity (lightweight requests)..."
if ! command -v curl >/dev/null 2>&1; then
  print_warning "curl not found on host. Skipping connectivity tests. Install curl for better validation."
else
  api_fail=false
  # Polygon: expect 200
  if ! is_placeholder_or_empty "$POLYGON_API_KEY_VAL"; then
    code=$(curl -s -o /dev/null -w '%{http_code}' "https://api.polygon.io/v3/reference/tickers?limit=1&apiKey=${POLYGON_API_KEY_VAL}")
    if [ "$code" = "200" ]; then
      print_success "Polygon API reachable (HTTP $code)"
    else
      print_error "Polygon connectivity failed (HTTP $code). Check key, network, or service status."
      echo "Hint: Verify key at https://polygon.io/ and confirm it has access."
      api_fail=true
    fi
  fi
  # Google AI: expect 200 if key provided
  if ! is_placeholder_or_empty "$GOOGLE_API_KEY_VAL"; then
    code=$(curl -s -o /dev/null -w '%{http_code}' "https://generativelanguage.googleapis.com/v1beta/models?key=${GOOGLE_API_KEY_VAL}")
    if [ "$code" = "200" ]; then
      print_success "Google AI API reachable (HTTP $code)"
    else
      print_error "Google AI connectivity failed (HTTP $code). Check key, network, or service status."
      echo "Hint: Generate key at https://ai.dev/ and ensure API is enabled for the project."
      api_fail=true
    fi
  fi
  # We do not contact OpenAI/Anthropic here to avoid causing auth calls unnecessarily.
  if [ "$api_fail" = true ]; then
    exit $EC_API_CONNECTIVITY_FAILED
  fi
fi

# Build images
print_info "Testing Docker build..."
if $COMPOSE_CMD build >/dev/null 2>&1; then
  print_success "Docker images built successfully"
else
  print_error "Failed to build Docker images"
  echo "Hints: Use --no-cache if cache is corrupted, check pyproject.toml dependencies, ensure internet access."
  exit $EC_DOCKER_BUILD_FAILED
fi

# Test dev container import
print_info "Testing dev container can import application..."
if $COMPOSE_CMD run --rm ai-robo-advisor python -c "import main; print('Dev import OK')" >/dev/null 2>&1; then
  print_success "Dev container can import application"
else
  print_error "Dev container failed to import application (PYTHONPATH/import issue?)"
  echo "Hints: Ensure PYTHONPATH is set to /app:/app/src and main.py exists under src/."
  exit $EC_CONTAINER_RUN_FAILED
fi

# Test production-like container import via profile
print_info "Testing production container can import application..."
if $COMPOSE_CMD --profile production run --rm ai-robo-advisor-prod python -c "import main; print('Prod import OK')" >/dev/null 2>&1; then
  print_success "Production container can import application"
else
  print_error "Production container failed to import application"
  echo "Hints: Rebuild images, verify PYTHONPATH in Dockerfile, and that package installs correctly."
  exit $EC_CONTAINER_RUN_FAILED
fi

# Test dev tools (non-fatal)
print_info "Testing development tools (pytest)..."
if $COMPOSE_CMD run --rm ai-robo-advisor pytest --version >/dev/null 2>&1; then
  print_success "Development tools (pytest) available"
else
  print_warning "Development tools not available. If needed, ensure dev/test extras are installed in the dev image."
fi

print_separator
print_success "🎉 Docker setup validation completed successfully!"
echo ""
echo "Next steps:"
echo "1) Edit .env with your actual API keys if you used the template"
echo "2) Start development: docker-compose up (or: ./docker/docker-helper.sh up)"
echo "3) Interactive shell: ./docker/docker-helper.sh interactive"
echo "4) Production profile: docker-compose --profile production up ai-robo-advisor-prod"
echo ""
echo "For help: ./docker/docker-helper.sh help"