#!/bin/bash

# SmartPot Waterer API Startup Script (macOS/Linux)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🌱 SmartPot Waterer API${NC}"
echo "========================"

# ============================================================================
# Check Python installation
# ============================================================================
PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Verify Python version (need 3.8+)
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}Error: Python 3.8+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "Using Python $PYTHON_VERSION"

# ============================================================================
# Setup virtual environment
# ============================================================================
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        echo "Try: $PYTHON_CMD -m pip install --user virtualenv"
        exit 1
    fi
fi

# Activate virtual environment (Unix)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo -e "${RED}Error: Virtual environment activation script not found${NC}"
    echo "Try deleting the venv folder and running this script again"
    exit 1
fi

# ============================================================================
# Upgrade pip and install dependencies
# ============================================================================
echo -e "${YELLOW}Checking pip...${NC}"

# Upgrade pip first to avoid issues
python -m pip install --upgrade pip --quiet 2>/dev/null || {
    echo -e "${YELLOW}Warning: Could not upgrade pip, continuing...${NC}"
}

# Install/upgrade setuptools and wheel (common dependency issues)
python -m pip install --upgrade setuptools wheel --quiet 2>/dev/null || {
    echo -e "${YELLOW}Warning: Could not upgrade setuptools/wheel${NC}"
}

# Install requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    python -m pip install -r requirements.txt --quiet || {
        echo -e "${RED}Error: Failed to install dependencies${NC}"
        echo ""
        echo "Common fixes:"
        echo "  1. Check your internet connection"
        echo "  2. Try: python -m pip install -r requirements.txt --verbose"
        echo "  3. If SSL errors: python -m pip install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt"
        exit 1
    }
else
    echo -e "${RED}Error: requirements.txt not found${NC}"
    exit 1
fi

echo -e "${GREEN}Dependencies installed successfully${NC}"

# ============================================================================
# Load environment variables
# ============================================================================
if [ -f ".env" ]; then
    echo "Loading .env file..."
    set -a
    source .env
    set +a
fi

# Default values
HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8001}"
ENV="${API_ENV:-dev}"

# ============================================================================
# Start server
# ============================================================================
echo ""
echo -e "${GREEN}Starting server on http://${HOST}:${PORT}${NC}"
echo "Environment: ${ENV}"
echo "Press Ctrl+C to stop"
echo ""

if [ "$ENV" = "dev" ]; then
    python -m uvicorn api.src.main:app --host "$HOST" --port "$PORT" --reload
else
    python -m uvicorn api.src.main:app --host "$HOST" --port "$PORT"
fi
