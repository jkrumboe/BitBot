#!/usr/bin/env python3
"""
BitSkins Delisted/Sold Items Bot
Monitors and processes items that are removed from the marketplace
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.bitskins_common import WebSocketBot, ItemProcessor

class DelistedSoldBot(WebSocketBot):
    """Bot that monitors delisted/sold items"""
    
    def __init__(self):
        super().__init__("DelistedSoldBot", ["delisted_or_sold"])
        self.collection_name = "delisted_sold_items"
        self.items_collection = self.db.get_collection(self.collection_name)
        self.logger.info(f"✅ Connected to MongoDB: {self.config.database_name}.{self.collection_name}")
    
    async def process_message(self, message_data):
        """Process delisted/sold item messages"""
        action = message_data.get('action')
        
        if action == 'delisted_or_sold':
            await self.process_delisted_sold_item(message_data.get('data', {}))
    
    async def process_delisted_sold_item(self, raw_data):
        """Process a delisted or sold item"""
        try:
            # Process common item data
            processed_data = ItemProcessor.process_base_item_data(
                raw_data, self.api, self.currency_rates
            )
            
            # Determine reason for delisting (sold vs delisted)
            # This is a heuristic - BitSkins doesn't always provide explicit reason
            reason = self.determine_delisting_reason(raw_data)
            
            # Add delisting-specific data
            delisted_item = {
                'timestamp': datetime.utcnow(),
                'event_type': 'delisted_or_sold',
                'raw_data': raw_data,
                'processed_at': datetime.utcnow().isoformat(),
                'reason': reason,
                **processed_data
            }
            
            # Store in MongoDB
            doc_id = self.db.store_document(self.collection_name, delisted_item)
            
            # Log the delisting/sale
            self.logger.info(f"✅ Stored delisted/sold item in MongoDB with ID: {doc_id}")
            
            # Choose appropriate emoji based on reason
            reason_emoji = "💰" if reason == "sold" else "🗑️" if reason == "delisted" else "❓"
            
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {reason_emoji} ITEM REMOVED:")
            print(f"  🆔 Item ID: {processed_data['item_id']}")
            print(f"  📦 Name: {processed_data['item_name']}")
            print(f"  💰 Price: ${processed_data['price_usd']}")
            print(f"  💶 Price EUR: €{processed_data['price_eur']}")
            print(f"  🏷️  Wear: {processed_data['wear']}")
            print(f"  📋 Reason: {reason.title()}")
            if processed_data['float_value']:
                print(f"  🎯 Float: {processed_data['float_value']:.6f}")
            print("-" * 60)
            
        except Exception as e:
            self.logger.error(f"Error processing delisted/sold item: {e}")
    
    def determine_delisting_reason(self, raw_data):
        """Determine if item was sold or delisted"""
        # This is a heuristic approach since BitSkins doesn't always provide explicit reason
        
        # Check if there are any indicators in the data
        # For now, we'll use "Unknown" as the API doesn't provide clear indication
        # Future enhancement: analyze patterns or timing to infer reason
        
        return "Unknown"  # Could be "sold", "delisted", or "Unknown"

def main():
    """Main execution function"""
    bot = DelistedSoldBot()
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
