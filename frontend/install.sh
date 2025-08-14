#!/bin/bash

# Nova Prompt Optimizer Frontend Installation Script
# Ensures clean, operational deployment

set -e  # Exit on any error

echo "🚀 Nova Prompt Optimizer Frontend Installation"
echo "=============================================="

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ required (found $python_version)"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies with explicit output
echo "📦 Installing dependencies..."
pip install python-fasthtml starlette python-multipart boto3 pydantic_settings pydantic-settings

# Try to install Nova SDK
echo "🔍 Attempting to install Nova SDK..."
if pip install nova-prompt-optimizer > /dev/null 2>&1; then
    echo "✅ Nova SDK installed successfully"
else
    echo "⚠️ Nova SDK installation failed - demo mode will be used"
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p data uploads optimized_prompts

# Run setup script
echo "🛠️ Running setup and validation..."
python3 setup.py

# Run health check
echo "🏥 Running health check..."
if python3 health_check.py; then
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Configure AWS credentials: aws configure"
    echo "2. Request Nova model access in AWS Bedrock console"
    echo "3. Start the application: ./start.sh"
    echo "4. Open browser: http://localhost:8000"
else
    echo ""
    echo "❌ Installation validation failed"
    echo "Please check the errors above and try again"
    exit 1
fi
