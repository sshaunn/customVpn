#!/bin/bash
# Manual health check script for testing

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_DIR"

# Load environment variables
if [ -f "config.env" ]; then
    export $(grep -v '^#' config.env | xargs)
fi

# Run health check
poetry run python scripts/python/health_monitor.py --check-only
