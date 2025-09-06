# 🤖 BitSkins API Monitoring Bot

A specialized microservices-based monitoring system for the BitSkins marketplace using WebSocket connections and MongoDB storage.

## 🏗️ Architecture

### Specialized Bots
- **📦 Listed Bot** (`bitskins_listed_bot.py`) - Monitors new item listings
- **💲 Price Changed Bot** (`bitskins_price_changed_bot.py`) - Tracks price changes  
- **🗑️ Delisted/Sold Bot** (`bitskins_delisted_sold_bot.py`) - Monitors item removals

### Database Collections
- `listed_items` - New marketplace listings
- `price_changed_items` - Price change events with analytics
- `delisted_sold_items` - Items removed from marketplace

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- BitSkins API key

### Setup
1. **Clone and configure:**
   ```bash
   git clone <repository>
   cd BitBot
   cp .env.example .env
   # Edit .env and add your BITSKINS_API_KEY
   ```

2. **Start all bots:**
   ```bash
   docker-compose up -d
   ```

3. **Access MongoDB Web UI:**
   - URL: http://localhost:8082
   - No authentication required

## 🎛️ Individual Bot Control

### Start specific bots:
```bash
# All bots
start_all_bots.bat

# Individual bots  
start_listed_bot.bat
start_price_changed_bot.bat
start_delisted_sold_bot.bat
```

### Docker commands:
```bash
# View logs
docker-compose logs -f bitskins_listed_bot
docker-compose logs -f bitskins_price_changed_bot  
docker-compose logs -f bitskins_delisted_sold_bot

# Stop all
docker-compose down

# Restart specific service
docker-compose restart bitskins_listed_bot
```

## 📊 Monitoring

### Collection Status
```bash
python check_collections.py
```

### MongoDB Access
- **Host:** localhost:27018
- **Database:** bitskins_bot
- **Username:** admin  
- **Password:** password123

## 🔧 Configuration

### Environment Variables
- `BITSKINS_API_KEY` - Your BitSkins API key
- `MONGODB_URI` - MongoDB connection string
- `DATABASE_NAME` - Database name (default: bitskins_bot)

### Port Configuration
- **MongoDB:** 27018
- **Mongo Express:** 8082

## 📁 File Structure

```
BitBot/
├── 🤖 Bot Files
│   ├── bitskins_listed_bot.py
│   ├── bitskins_price_changed_bot.py
│   └── bitskins_delisted_sold_bot.py
├── 🐳 Docker Configuration  
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── .dockerignore
├── 🗄️ Database
│   └── mongo-init.js
├── 📦 Dependencies
│   └── requirements.txt
├── ⚙️ Configuration
│   ├── .env
│   └── .env.docker
├── 🚀 Startup Scripts
│   ├── start_all_bots.bat
│   ├── start_listed_bot.bat
│   ├── start_price_changed_bot.bat
│   └── start_delisted_sold_bot.bat
├── 🔍 Utilities
│   └── check_collections.py
└── 📝 Logs
    └── logs/
```

## 🎯 Features

- **Real-time WebSocket monitoring** of BitSkins marketplace
- **Specialized microservices** for different event types
- **MongoDB storage** with individual collections
- **Currency conversion** to EUR with proper formatting
- **Wear condition detection** from float values
- **Docker containerization** for easy deployment
- **Web-based MongoDB interface** for data exploration
- **Structured logging** with emoji indicators

## 🔄 Data Flow

1. **WebSocket Connection** → BitSkins API
2. **Event Filtering** → Specialized bots process specific event types
3. **Data Processing** → Currency conversion, wear detection, analytics
4. **MongoDB Storage** → Individual collections per event type
5. **Web Interface** → Mongo Express for data exploration

## 📈 Monitoring Output

Each bot provides real-time formatted output:

```
[2025-09-06 01:25:27] 💲 PRICE CHANGE:
  🆔 Item ID: 6237035
  📦 Name: Sticker | Virtus.pro (Glitter) | Copenhagen 2024
  💰 Old Price: $0.330
  💰 New Price: $0.320  
  📉 Change: $-0.010
  🏷️  Wear: Unknown
```

---

**🎮 Happy Trading! Monitor the BitSkins marketplace like a pro! 🚀**
