import asyncio
import json
import websockets
import os
import time
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient

BITSKINS_WS_URL = "wss://ws.bitskins.com"
load_dotenv()
API_KEY = os.getenv("BITSKINS_API_KEY")

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "bitskins_bot")

def get_mongodb_connection():
    """Get MongoDB connection with retry logic"""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            db = client[DATABASE_NAME]
            items_collection = db["delisted_sold_items"]
            print(f"✅ Connected to MongoDB: {DATABASE_NAME}.delisted_sold_items")
            return client, db, items_collection
        except Exception as e:
            print(f"❌ MongoDB connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ Failed to connect to MongoDB after all retries")
                return None, None, None

client, db, items_collection = get_mongodb_connection()

def get_wear_from_float(float_value):
    """Convert float value to wear condition name"""
    if float_value is None:
        return "Unknown"
    
    if float_value <= 0.07:
        return "Factory New"
    elif float_value <= 0.15:
        return "Minimal Wear"
    elif float_value <= 0.38:
        return "Field-Tested"
    elif float_value <= 0.45:
        return "Well-Worn"
    else:
        return "Battle-Scarred"

def store_delisted_sold_item(data):
    """Store delisted/sold item in MongoDB and log to console"""
    timestamp = datetime.now()
    
    document = {
        "timestamp": timestamp,
        "event_type": "delisted_or_sold",
        "raw_data": data,
        "processed_at": timestamp.isoformat()
    }
    
    if isinstance(data, dict):
        float_value = data.get('float_value')
        wear_from_float = get_wear_from_float(float_value)
        wear_from_name = data.get('wear_name', data.get('wear'))
        final_wear = wear_from_name if wear_from_name else wear_from_float
        
        document.update({
            "item_id": data.get('id'),
            "item_name": data.get('market_name', data.get('name')),
            "price_raw": data.get('price'),
            "price_usd": data.get('price', 0) / 1000 if data.get('price') else None,
            "suggested_price_usd": data.get('suggested_price', 0) / 1000 if data.get('suggested_price') else None,
            "wear": final_wear,
            "wear_from_float": wear_from_float,
            "float_value": float_value,
            "reason": data.get('reason', 'Unknown'),
            "skin_id": data.get('skin_id'),
            "asset_id": data.get('asset_id')
        })
    
    if items_collection is not None:
        try:
            result = items_collection.insert_one(document)
            print(f"✅ Stored delisted/sold item in MongoDB with ID: {result.inserted_id}")
        except Exception as e:
            print(f"❌ Failed to store in MongoDB: {e}")
    
    log_delisted_sold_item(data)

def log_delisted_sold_item(data):
    """Log delisted/sold item with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] 🔴 DELISTED/SOLD:")
    
    if isinstance(data, dict):
        item_id = data.get('id', 'Unknown')
        item_name = data.get('market_name', data.get('name', 'Unknown Item'))
        price = data.get('price', 0)
        reason = data.get('reason', 'Unknown')
        float_value = data.get('float_value')
        wear = data.get('wear_name', data.get('wear'))
        
        if not wear or wear == 'Unknown':
            wear = get_wear_from_float(float_value)
        
        # Determine if it was sold or delisted
        status_emoji = "💰" if "sold" in reason.lower() else "❌"
        
        print(f"  🆔 Item ID: {item_id}")
        print(f"  📦 Name: {item_name}")
        print(f"  💰 Price: ${price/1000:.3f}" if price else "  💰 Price: Unknown")
        print(f"  {status_emoji} Reason: {reason}")
        print(f"  🏷️  Wear: {wear}")
        
        if float_value is not None:
            print(f"  🔢 Float: {float_value:.6f}")
    
    print("-" * 60)

async def bitskins_delisted_sold_bot():
    async with websockets.connect(BITSKINS_WS_URL) as ws:
        await ws.send(json.dumps(["WS_AUTH_APIKEY", API_KEY]))
        print("🔐 Authenticated for DELISTED/SOLD items monitoring")

        authenticated = False
        while True:
            response = await ws.recv()
            try:
                action, data = json.loads(response)
            except Exception as e:
                print("❌ Error parsing message:", response)
                continue

            if not authenticated and action and action.startswith("WS_AUTH"):
                authenticated = True
                await ws.send(json.dumps(["WS_SUB", "delisted_or_sold"]))
                print("📡 Subscribed to 'delisted_or_sold' events only")

            elif authenticated and action == "delisted_or_sold":
                store_delisted_sold_item(data)

if __name__ == "__main__":
    print("🚀 Starting BitSkins DELISTED/SOLD Items Bot...")
    asyncio.run(bitskins_delisted_sold_bot())
