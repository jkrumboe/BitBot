@echo off
echo 📊 Starting BitSkins Market Analytics...

cd /d "c:\repos\BitBot"

echo.
echo Running Analytics Dashboard...
python analytics\analytics_dashboard.py

echo.
echo Generating Market Report...
python analytics\market_report.py

echo.
echo ✅ Analytics complete! Check the output files for results.
pause
