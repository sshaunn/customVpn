#!/bin/bash
# Setup cron job for VPN health monitoring

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_SCRIPT="$PROJECT_DIR/scripts/python/health_monitor.py"
LOG_FILE="$PROJECT_DIR/logs/health_monitor.log"
POETRY_PATH="$(which poetry)"

# Ensure log directory exists
mkdir -p "$PROJECT_DIR/logs"

# Create cron entry (every 5 minutes)
CRON_ENTRY="*/5 * * * * cd $PROJECT_DIR && $POETRY_PATH run python $PYTHON_SCRIPT >> $LOG_FILE 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "health_monitor.py"; then
    echo "Health monitor cron job already exists"
    crontab -l | grep "health_monitor.py"
    exit 0
fi

# Add cron job
(crontab -l 2>/dev/null || true; echo "$CRON_ENTRY") | crontab -

echo "Cron job added successfully:"
echo "$CRON_ENTRY"
echo ""
echo "Log file: $LOG_FILE"
echo ""
echo "To verify: crontab -l"
echo "To remove: crontab -e (then delete the line)"
