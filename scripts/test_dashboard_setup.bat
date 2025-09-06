@echo off
echo Testing BitBot Dashboard Setup...
echo.

echo Checking if Node.js is installed...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js is installed

echo.
echo Checking if Python is installed...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed. Please install Python 3.11+ from https://python.org/
    pause
    exit /b 1
)
echo ✓ Python is installed

echo.
echo Checking if MongoDB is accessible...
cd /d "%~dp0\..\api"
python -c "from pymongo import MongoClient; MongoClient('mongodb://admin:password123@localhost:27019/bitskins_bot?authSource=admin').admin.command('ping')" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: MongoDB is not accessible. Please start MongoDB with docker-compose up -d mongodb
    echo You can still test the dashboard, but it will show empty data.
) else (
    echo ✓ MongoDB is accessible
)

echo.
echo Testing API dependencies...
cd /d "%~dp0\..\api"
python -c "import flask, pymongo, pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Python dependencies
        pause
        exit /b 1
    )
)
echo ✓ Python dependencies are available

echo.
echo Testing React dependencies...
cd /d "%~dp0\..\web-dashboard"
if not exist node_modules (
    echo Installing React dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install React dependencies
        pause
        exit /b 1
    )
)
echo ✓ React dependencies are available

echo.
echo ==========================================
echo All checks passed! ✓
echo ==========================================
echo.
echo To start the dashboard:
echo 1. Run: .\scripts\start_dashboard.bat
echo 2. Open: http://localhost:3001
echo.
echo To start with Docker:
echo 1. Run: docker-compose up -d
echo 2. Open: http://localhost:3001
echo.
pause
