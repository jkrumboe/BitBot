@echo off
echo 🚀 Starting LISTED Items Bot Only...

docker-compose up -d mongodb
timeout /t 5 /nobreak > nul
docker-compose up -d bitskins_listed_bot

echo ✅ Listed Items Bot is running!
echo 📋 View logs: docker-compose logs -f bitskins_listed_bot

pause
