#!/bin/bash
# Script to run API tests with proper environment variables

# Set test environment variables
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export SECRET_KEY="test-secret-key-for-testing-only-min-32-chars"
export ENVIRONMENT="development"

# Run pytest with provided arguments
poetry run pytest tests/test_api/ "$@"
