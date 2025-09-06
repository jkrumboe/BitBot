#!/usr/bin/env python3
"""
BitSkins Listed Items Bot
Monitors and processes newly listed items on the marketplace
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.bitskins_common import WebSocketBot, ItemProcessor

class ListedItemsBot(WebSocketBot):
    """Bot that monitors newly listed items"""
    
    def __init__(self):
        super().__init__("ListedItemsBot", ["listed"])
        self.collection_name = "listed_items"
        self.items_collection = self.db.get_collection(self.collection_name)
        self.logger.info(f"✅ Connected to MongoDB: {self.config.database_name}.{self.collection_name}")
    
    async def process_message(self, message_data):
        """Process listed item messages"""
        action = message_data.get('action')
        
        if action == 'listed':
            await self.process_listed_item(message_data.get('data', {}))
    
    async def process_listed_item(self, raw_data):
        """Process a newly listed item"""
        try:
            # Process common item data
            processed_data = ItemProcessor.process_base_item_data(
                raw_data, self.api, self.currency_rates
            )
            
            # Add listing-specific data
            listed_item = {
                'timestamp': datetime.utcnow(),
                'event_type': 'listed',
                'raw_data': raw_data,
                'processed_at': datetime.utcnow().isoformat(),
                **processed_data
            }
            
            # Store in MongoDB
            doc_id = self.db.store_document(self.collection_name, listed_item)
            
            # Log the listing
            self.logger.info(f"✅ Stored listed item in MongoDB with ID: {doc_id}")
            
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📦 NEW LISTING:")
            print(f"  🆔 Item ID: {processed_data['item_id']}")
            print(f"  📦 Name: {processed_data['item_name']}")
            print(f"  💰 Price: ${processed_data['price_usd']}")
            print(f"  💶 Price EUR: €{processed_data['price_eur']}")
            print(f"  🏷️  Wear: {processed_data['wear']}")
            if processed_data['float_value']:
                print(f"  🎯 Float: {processed_data['float_value']:.6f}")
            print(f"  🤖 Seller: {processed_data['bot_steam_id']}")
            print("-" * 60)
            
        except Exception as e:
            self.logger.error(f"Error processing listed item: {e}")

def main():
    """Main execution function"""
    bot = ListedItemsBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
