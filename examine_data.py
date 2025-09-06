#!/usr/bin/env python3
"""
Quick script to examine the actual data structure in MongoDB collections
"""

from pymongo import MongoClient
import pandas as pd

def examine_data_structure():
    # Connect to MongoDB
    mongodb_uri = "mongodb://admin:password123@localhost:27018/bitskins_bot?authSource=admin"
    client = MongoClient(mongodb_uri)
    db = client['bitskins_bot']
    
    print("🔍 EXAMINING DATA STRUCTURE")
    print("=" * 50)
    
    collections = {
        'listed_items': db['listed_items'],
        'price_changed_items': db['price_changed_items'],
        'delisted_sold_items': db['delisted_sold_items']
    }
    
    for name, collection in collections.items():
        print(f"\n📊 {name.upper()}:")
        print("-" * 30)
        
        # Get sample document
        sample = collection.find_one()
        if sample:
            print("Sample document structure:")
            for key, value in sample.items():
                if key != '_id':  # Skip MongoDB ObjectId
                    print(f"  {key}: {type(value).__name__} = {value}")
        else:
            print("  No documents found")
        
        # Get document count
        count = collection.count_documents({})
        print(f"  Total documents: {count}")

if __name__ == "__main__":
    examine_data_structure()
