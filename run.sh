#!/bin/bash

# SmartPot Waterer API Startup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌱 SmartPot Waterer API${NC}"
echo "========================"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Load environment variables if .env exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Default values
HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8001}"
ENV="${API_ENV:-dev}"

echo -e "${GREEN}Starting server on http://${HOST}:${PORT}${NC}"
echo "Environment: ${ENV}"
echo "Press Ctrl+C to stop"
echo ""

# Run uvicorn
if [ "$ENV" = "dev" ]; then
    uvicorn api.src.main:app --host "$HOST" --port "$PORT" --reload
else
    uvicorn api.src.main:app --host "$HOST" --port "$PORT"
fi
