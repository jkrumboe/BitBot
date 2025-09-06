@echo off
echo Starting BitBot Dashboard...
echo.

echo Installing Python API dependencies...
cd /d "%~dp0\..\api"
pip install -r requirements.txt

echo.
echo Installing React dependencies...
cd /d "%~dp0\..\web-dashboard"
call npm install

echo.
echo Starting API server...
cd /d "%~dp0\..\api"
start /B python dashboard_api.py

echo.
echo Starting React development server...
cd /d "%~dp0\..\web-dashboard"
timeout /t 3 /nobreak >nul
call npm start

echo.
echo Dashboard should be available at:
echo Frontend: http://localhost:3001
echo API: http://localhost:5000/api/dashboard
pause
