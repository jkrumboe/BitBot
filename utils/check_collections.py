#!/usr/bin/env python3
"""
Quick script to check all three collections and their document counts
"""

import os
from pymongo import MongoClient
from datetime import datetime

def main():
    # Connect to MongoDB
    mongodb_uri = "mongodb://admin:password123@localhost:27019/bitskins_bot?authSource=admin"
    client = MongoClient(mongodb_uri)
    db = client['bitskins_bot']
    
    print("🔍 BitSkins Bot Collections Status")
    print("=" * 50)
    print(f"📅 Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    collections = [
        ('listed_items', '📦 Listed Items'),
        ('price_changed_items', '💲 Price Changes'),
        ('delisted_sold_items', '🗑️ Delisted/Sold Items')
    ]
    
    total_documents = 0
    
    for collection_name, display_name in collections:
        try:
            collection = db[collection_name]
            count = collection.count_documents({})
            total_documents += count
            
            print(f"{display_name}")
            print(f"   Collection: {collection_name}")
            print(f"   Documents: {count:,}")
            
            if count > 0:
                # Get latest document
                latest = collection.find().sort("timestamp", -1).limit(1)
                latest_doc = next(latest, None)
                if latest_doc:
                    timestamp = latest_doc.get('timestamp', 'Unknown')
                    item_name = latest_doc.get('name', 'Unknown')
                    print(f"   Latest: {item_name} at {timestamp}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error checking {collection_name}: {e}")
            print()
    
    print(f"📊 Total Documents: {total_documents:,}")
    print("=" * 50)
    
    # List all collections in the database
    all_collections = db.list_collection_names()
    print(f"🗃️ All Collections: {', '.join(all_collections)}")

if __name__ == "__main__":
    main()
