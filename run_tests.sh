#!/bin/bash
# Test runner script for AI Robo Advisor
# Usage: ./run_tests.sh [options]

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
COVERAGE=true
VERBOSE=false
MARKERS=""
SPECIFIC_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--unit)
            TEST_TYPE="unit"
            MARKERS="-m unit"
            shift
            ;;
        -i|--integration)
            TEST_TYPE="integration"
            MARKERS="-m integration"
            shift
            ;;
        -f|--fast)
            TEST_TYPE="fast"
            MARKERS="-m 'not slow'"
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-cov)
            COVERAGE=false
            shift
            ;;
        --file)
            SPECIFIC_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -u, --unit          Run only unit tests"
            echo "  -i, --integration   Run only integration tests"
            echo "  -f, --fast          Run only fast tests (exclude slow)"
            echo "  -v, --verbose       Verbose output"
            echo "  --no-cov            Skip coverage reporting"
            echo "  --file FILE         Run specific test file"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                      # Run all tests with coverage"
            echo "  ./run_tests.sh -u                   # Run only unit tests"
            echo "  ./run_tests.sh -v                   # Run with verbose output"
            echo "  ./run_tests.sh --file test_models.py  # Run specific file"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}AI Robo Advisor Test Suite${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""

# Check if pytest is installed
if ! python -m pytest --version &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install test dependencies with: pip install -e \".[test]\""
    exit 1
fi

# Build pytest command
PYTEST_CMD="python -m pytest tests/"

# Add specific file if provided
if [ -n "$SPECIFIC_FILE" ]; then
    PYTEST_CMD="python -m pytest tests/$SPECIFIC_FILE"
fi

# Add markers
if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD $MARKERS"
fi

# Add verbose flag
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=term-missing --cov-report=html"
fi

echo -e "${YELLOW}Running: $TEST_TYPE tests${NC}"
echo -e "${YELLOW}Command: $PYTEST_CMD${NC}"
echo ""

# Run tests
if eval $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}=================================${NC}"
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo -e "${GREEN}=================================${NC}"
    
    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${YELLOW}Coverage report generated in: htmlcov/index.html${NC}"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}=================================${NC}"
    echo -e "${RED}✗ Tests failed${NC}"
    echo -e "${RED}=================================${NC}"
    exit 1
fi
