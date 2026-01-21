#!/bin/bash

# AMD Stock Prediction System - Automated Setup Script
# This script automates the setup process for local development

set -e  # Exit on any error

echo "🚀 AMD Stock Prediction System - Setup Script"
echo "=============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    PIP_CMD=pip
else
    echo "❌ Python not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"

# Check Python version is 3.8+
REQUIRED_VERSION="3.8"
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
$PIP_CMD install --upgrade pip --quiet

# Install requirements
echo ""
echo "📥 Installing dependencies (this may take a few minutes)..."
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt --quiet
    echo "✅ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating data directories..."
mkdir -p data/cache
mkdir -p data/predictions
mkdir -p data/nextday
mkdir -p data/weekend
mkdir -p logs
mkdir -p models
echo "✅ Directories created"

# Copy .env.example to .env if not exists
echo ""
echo "🔐 Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "⚠️  Please edit .env and add your API keys!"
    else
        echo "⚠️  .env.example not found, skipping .env creation"
    fi
else
    echo "✅ .env file already exists"
fi

# Check for API keys
echo ""
echo "🔑 Checking for API keys..."
if [ -f ".env" ]; then
    if grep -q "your_.*_key_here" .env; then
        echo "⚠️  WARNING: .env contains placeholder values"
        echo "   Please update .env with your actual API keys:"
        echo "   - Alpha Vantage (FREE): https://www.alphavantage.co/support/#api-key"
        echo "   - Polygon.io: https://polygon.io/pricing"
        echo "   - Twilio (SMS): https://www.twilio.com/try-twilio"
    else
        echo "✅ API keys appear to be configured"
    fi
fi

# Test installation
echo ""
echo "🧪 Testing installation..."
if $PYTHON_CMD main.py --mode test 2>/dev/null; then
    echo "✅ System test passed!"
else
    echo "⚠️  System test failed. Please check logs/errors.log for details"
fi

echo ""
echo "=============================================="
echo "✨ Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys (at minimum: ALPHA_VANTAGE_API_KEY)"
echo "2. Run a test prediction: python main.py --mode single --symbol AMD"
echo "3. Start continuous mode: python main.py --mode run --symbol AMD --interval 10"
echo ""
echo "📚 Documentation:"
echo "- Full guide: README.md"
echo "- Quick setup: SETUP_GUIDE.md"
echo "- API keys: api_key_requirements.md"
echo ""
echo "🎉 Happy trading!"
