@echo off
echo 🚀 Starting ALL BitSkins Bots with Docker...

REM Copy environment file
copy .env.docker .env

REM Build and start all containers
docker-compose up --build -d

REM Show status
echo 📊 Container Status:
docker-compose ps

echo.
echo ✅ All BitSkins Bots are now running!
echo.
echo 📋 Useful commands:
echo   View all logs:           docker-compose logs -f
echo   View listed bot logs:    docker-compose logs -f bitskins_listed_bot
echo   View price bot logs:     docker-compose logs -f bitskins_price_changed_bot
echo   View delisted bot logs:  docker-compose logs -f bitskins_delisted_sold_bot
echo   Stop all containers:     docker-compose down
echo   Query database:          docker-compose exec bitskins_listed_bot python query_collections.py
echo.
echo 🌐 MongoDB Web UI:         http://localhost:8082
echo 📊 Query specific collection: python query_collections.py [collection_name]

pause
