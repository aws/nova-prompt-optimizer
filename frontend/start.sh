#!/bin/bash

# Nova Prompt Optimizer Frontend Startup Script
# Includes validation and error handling

set -e

echo "🚀 Starting Nova Prompt Optimizer Frontend"
echo "=========================================="

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found"
    echo "💡 Run: ./install.sh first"
    exit 1
fi

# Quick health check
echo "🏥 Running startup health check..."
if ! python3 health_check.py > /dev/null 2>&1; then
    echo "❌ Health check failed"
    echo "💡 Run: python3 health_check.py for details"
    echo "💡 Or run: ./install.sh to reinstall"
    exit 1
fi

echo "✅ Health check passed"

# Start the application
echo "🌐 Starting web server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

python3 app.py
