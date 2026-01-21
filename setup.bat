@echo off
REM AMD Stock Prediction System - Windows Setup Script
REM This script automates the setup process for local development on Windows

echo 🚀 AMD Stock Prediction System - Setup Script (Windows)
echo ==========================================================
echo.

REM Check Python version
echo 📋 Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%

REM Create virtual environment
echo.
echo 📦 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install requirements
echo.
echo 📥 Installing dependencies (this may take a few minutes)...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Create necessary directories
echo.
echo 📁 Creating data directories...
if not exist "data\cache" mkdir data\cache
if not exist "data\predictions" mkdir data\predictions
if not exist "data\nextday" mkdir data\nextday
if not exist "data\weekend" mkdir data\weekend
if not exist "logs" mkdir logs
if not exist "models" mkdir models
echo ✅ Directories created

REM Copy .env.example to .env if not exists
echo.
echo 🔐 Setting up environment variables...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo ✅ Created .env file from .env.example
        echo ⚠️  Please edit .env and add your API keys!
    ) else (
        echo ⚠️  .env.example not found, skipping .env creation
    )
) else (
    echo ✅ .env file already exists
)

REM Check for API keys
echo.
echo 🔑 Checking for API keys...
if exist ".env" (
    findstr /C:"your_" .env >nul
    if %errorlevel% equ 0 (
        echo ⚠️  WARNING: .env contains placeholder values
        echo    Please update .env with your actual API keys:
        echo    - Alpha Vantage ^(FREE^): https://www.alphavantage.co/support/#api-key
        echo    - Polygon.io: https://polygon.io/pricing
        echo    - Twilio ^(SMS^): https://www.twilio.com/try-twilio
    ) else (
        echo ✅ API keys appear to be configured
    )
)

echo.
echo ==========================================================
echo ✨ Setup Complete!
echo ==========================================================
echo.
echo Next steps:
echo 1. Edit .env and add your API keys ^(at minimum: ALPHA_VANTAGE_API_KEY^)
echo 2. Run a test prediction: python main.py --mode single --symbol AMD
echo 3. Start continuous mode: python main.py --mode run --symbol AMD --interval 10
echo.
echo 📚 Documentation:
echo - Full guide: README.md
echo - Quick setup: SETUP_GUIDE.md
echo - API keys: api_key_requirements.md
echo.
echo 🎉 Happy trading!
echo.
pause
