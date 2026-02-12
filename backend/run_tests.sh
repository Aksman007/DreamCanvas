#!/bin/bash

# DreamCanvas Backend Test Runner
# Convenience script for running tests with common options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print header
print_header() {
    echo ""
    print_message "$BLUE" "================================"
    print_message "$BLUE" "$1"
    print_message "$BLUE" "================================"
    echo ""
}

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    print_message "$RED" "Error: Poetry is not installed"
    echo "Install poetry: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Parse command line arguments
COVERAGE=false
VERBOSE=false
FAST=false
TARGET="tests/test_core/"

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--fast)
            FAST=true
            shift
            ;;
        -h|--help)
            print_header "DreamCanvas Test Runner"
            echo "Usage: ./run_tests.sh [options] [target]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage    Run with coverage report"
            echo "  -v, --verbose     Run with verbose output"
            echo "  -f, --fast        Skip slow tests"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                           # Run all core tests"
            echo "  ./run_tests.sh -c                        # Run with coverage"
            echo "  ./run_tests.sh -v tests/test_core/       # Verbose output"
            echo "  ./run_tests.sh tests/test_core/test_security.py  # Specific file"
            echo ""
            exit 0
            ;;
        *)
            TARGET=$1
            shift
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="poetry run pytest"

# Add target
PYTEST_CMD="$PYTEST_CMD $TARGET"

# Add options
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$FAST" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=html --cov-report=term-missing"
fi

# Run tests
print_header "Running DreamCanvas Tests"

print_message "$YELLOW" "Target: $TARGET"
if [ "$COVERAGE" = true ]; then
    print_message "$YELLOW" "Coverage: Enabled"
fi
if [ "$FAST" = true ]; then
    print_message "$YELLOW" "Mode: Fast (skipping slow tests)"
fi
echo ""

# Execute pytest
eval $PYTEST_CMD

# Check exit code
if [ $? -eq 0 ]; then
    print_message "$GREEN" "✓ All tests passed!"

    if [ "$COVERAGE" = true ]; then
        echo ""
        print_message "$BLUE" "Coverage report generated: htmlcov/index.html"
        print_message "$BLUE" "Open in browser: open htmlcov/index.html"
    fi
else
    print_message "$RED" "✗ Tests failed!"
    exit 1
fi

echo ""
