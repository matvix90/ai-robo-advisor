# 🐳 Docker Setup Guide for AI Robo Advisor

This directory contains all Docker-related configurations for the AI Robo Advisor project. The setup provides a consistent, cross-platform development environment that eliminates "works on my machine" issues.

## 📁 Directory Structure

```
docker/
├── README.md              # This guide
├── Dockerfile             # Multi-stage build configuration
├── docker-helper.sh       # Management script for common operations
├── validate-setup.sh      # Setup validation and verification script
└── .env.docker           # Docker-specific environment template
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git repository cloned

### 1. Initial Setup
```bash
# Navigate to project root
cd ai-robo-advisor

# Create environment file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or your preferred editor
```

### 2. Validate Setup
```bash
# Run validation script
./docker/validate-setup.sh
```

### 3. Start Application
```bash
# Development mode (default)
docker-compose up

# Or use helper script
./docker/docker-helper.sh up
```

## 🔧 Docker Architecture

### Multi-Stage Build
The Dockerfile uses a multi-stage build approach for optimized images:

1. **Base Stage** (`base`)
   - Python 3.11 slim base image
   - System dependencies (gcc, g++)
   - Non-root user setup
   - Environment variables

2. **Dependencies Stage** (`dependencies`)
   - Application dependencies installation
   - Source code copying
   - Python package installation

3. **Development Stage** (`development`)
   - Development and testing dependencies
   - Test files and configuration
   - Hot-reload support via volume mounts

4. **Production Stage** (`production`)
   - Optimized for deployment
   - No development dependencies
   - Health checks included

5. **Interactive Stage** (`interactive`)
   - Enhanced with additional tools (curl, nano, vim)
   - Perfect for exploration and debugging

### Container Profiles
- **Default**: Development mode with hot-reload
- **Interactive**: Shell access for exploration
- **Production**: Optimized deployment configuration

## 📋 Available Commands

### Using Docker Compose Directly
```bash
# Start development environment
docker-compose up

# Start in background
docker-compose up -d

# Interactive shell
docker-compose --profile interactive up ai-robo-advisor-interactive

# Production mode
docker-compose --profile production up ai-robo-advisor-prod

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Run one-off commands
docker-compose run --rm ai-robo-advisor python -m main --help
```

### Using Helper Script
```bash
# Make executable (first time only)
chmod +x docker/docker-helper.sh

# Common operations
./docker/docker-helper.sh up              # Start development
./docker/docker-helper.sh interactive     # Interactive shell
./docker/docker-helper.sh test           # Run tests
./docker/docker-helper.sh shell          # Shell in running container
./docker/docker-helper.sh down           # Stop containers
./docker/docker-helper.sh clean          # Clean up everything
./docker/docker-helper.sh status         # Show status
./docker/docker-helper.sh help           # Show all commands
```

## 🔐 Environment Variables

### Required API Keys
- `POLYGON_API_KEY` - Financial data API (required)
- At least one LLM provider:
  - `GOOGLE_API_KEY` - Google Gemini models
  - `OPENAI_API_KEY` - OpenAI GPT models  
  - `ANTHROPIC_API_KEY` - Anthropic Claude models

### Docker-Specific Variables
- `PYTHONPATH=/app/src` - Python module resolution
- `ENVIRONMENT` - Runtime mode (development/production)
- `PYTHONDONTWRITEBYTECODE=1` - No .pyc files
- `PYTHONUNBUFFERED=1` - Real-time output

### Environment File Format
```bash
# .env file example
POLYGON_API_KEY=your-actual-polygon-key
GOOGLE_API_KEY=your-actual-google-key
OPENAI_API_KEY=your-actual-openai-key
ANTHROPIC_API_KEY=your-actual-anthropic-key
```

## 🧪 Development Workflow

### 1. Code Changes
- Source code is mounted as volumes for hot-reload
- Changes in `src/` automatically reflected in container
- No need to rebuild for source code changes

### 2. Dependency Changes
- If `pyproject.toml` changes, rebuild with:
```bash
docker-compose up --build
# or
./docker/docker-helper.sh up --rebuild
```

### 3. Testing
```bash
# Run tests in container
./docker/docker-helper.sh test

# Or directly
docker-compose run --rm ai-robo-advisor pytest tests/ -v

# With coverage
docker-compose run --rm ai-robo-advisor pytest tests/ --cov=src
```

### 4. Interactive Development
```bash
# Start interactive session
./docker/docker-helper.sh interactive

# Inside container, you can:
python -m main                    # Run application
pytest tests/                     # Run tests
python -c "import main; help(main)"  # Explore code
```

## 🔍 Troubleshooting

### Common Issues

#### Docker Daemon Not Running
```bash
# Error: Cannot connect to Docker daemon
# Solution: Start Docker service
sudo systemctl start docker        # Linux
# or start Docker Desktop           # Windows/Mac
```

#### Permission Denied
```bash
# Error: Permission denied for docker commands
# Solution: Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in
```

#### Port Already in Use
```bash
# Error: Port already allocated
# Solution: Stop existing containers
docker-compose down
docker ps  # Check for other containers
```

#### Environment Variables Not Loading
```bash
# Check .env file exists and has correct format
cat .env
# Ensure no spaces around = in .env file
```

#### Build Failures
```bash
# Clean build
./docker/docker-helper.sh clean
docker-compose build --no-cache

# Check Docker space
docker system df
docker system prune  # if needed
```

### Debugging Commands
```bash
# Check container logs
docker-compose logs ai-robo-advisor

# Check container status
docker-compose ps

# Enter running container
docker exec -it ai-robo-advisor-dev /bin/bash

# Check environment inside container
docker-compose run --rm ai-robo-advisor env

# Test specific functionality
docker-compose run --rm ai-robo-advisor python -c "import sys; print(sys.path)"
```

## 🔧 Customization

### Adding New Dependencies
1. Update `pyproject.toml`
2. Rebuild container: `docker-compose up --build`

### Modifying Container Configuration
- Edit `docker/Dockerfile` for image changes
- Edit `docker-compose.yml` for service configuration
- Test changes with validation script

### Adding New Services
```yaml
# In docker-compose.yml
services:
  database:
    image: postgres:15
    environment:
      - POSTGRES_DB=robo_advisor
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## 📊 Performance Tips

### Faster Builds
- Use `.dockerignore` to exclude unnecessary files
- Multi-stage builds already optimize layer caching
- Consider using Docker BuildKit: `DOCKER_BUILDKIT=1 docker-compose build`

### Smaller Images
- Debian slim base images used
- `apt-get clean` removes package cache
- Multi-stage builds exclude development dependencies in production

### Development Speed
- Volume mounts enable hot-reload
- Dependencies cached in Docker layers
- Use `docker-compose up -d` for background running

## 🔒 Security Considerations

### Container Security
- Non-root user (`appuser`) execution
- No secrets in Dockerfile or images
- Environment variable injection only

### API Key Management
- Use `.env` file (never committed)
- Validate keys with validation script
- Separate development/production environments

### Network Security
- Containers isolated in custom network
- Only necessary ports exposed
- No privileged containers

---

## 🆘 Getting Help

If you encounter issues:

1. **Run validation script**: `./docker/validate-setup.sh`
2. **Check logs**: `docker-compose logs`
3. **Verify environment**: Ensure `.env` file has valid API keys
4. **Clean restart**: `./docker/docker-helper.sh clean && ./docker/docker-helper.sh up`
5. **Check GitHub issues**: Search for similar problems
6. **Create new issue**: Provide validation script output and error logs

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)
- [AI Robo Advisor Main README](../README.md)
- [Contributing Guidelines](../CONTRIBUTING.md)