@echo off
echo 🚀 Starting PRICE CHANGED Items Bot Only...

docker-compose up -d mongodb
timeout /t 5 /nobreak > nul
docker-compose up -d bitskins_price_changed_bot

echo ✅ Price Changed Items Bot is running!
echo 📋 View logs: docker-compose logs -f bitskins_price_changed_bot

pause
