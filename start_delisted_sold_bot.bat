@echo off
echo 🚀 Starting DELISTED/SOLD Items Bot Only...

docker-compose up -d mongodb
timeout /t 5 /nobreak > nul
docker-compose up -d bitskins_delisted_sold_bot

echo ✅ Delisted/Sold Items Bot is running!
echo 📋 View logs: docker-compose logs -f bitskins_delisted_sold_bot

pause
