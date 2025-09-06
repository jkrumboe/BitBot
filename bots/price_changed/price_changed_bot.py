#!/usr/bin/env python3
"""
BitSkins Price Changed Bot
Monitors and processes price change events on the marketplace
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from shared.bitskins_common import WebSocketBot, ItemProcessor

class PriceChangedBot(WebSocketBot):
    """Bot that monitors price changes"""
    
    def __init__(self):
        super().__init__("PriceChangedBot", ["price_changed"])
        self.collection_name = "price_changed_items"
        self.items_collection = self.db.get_collection(self.collection_name)
        self.logger.info(f"✅ Connected to MongoDB: {self.config.database_name}.{self.collection_name}")
    
    async def process_message(self, message_data):
        """Process price changed messages"""
        action = message_data.get('action')
        
        if action == 'price_changed':
            await self.process_price_change(message_data.get('data', {}))
    
    async def process_price_change(self, raw_data):
        """Process a price change event"""
        try:
            # Extract price data
            old_price_raw = raw_data.get('old_price', 0)
            new_price_raw = raw_data.get('price', 0)
            suggested_price_raw = raw_data.get('suggested_price', 0)
            
            # Convert prices
            old_prices = self.api.convert_price(old_price_raw, self.currency_rates)
            new_prices = self.api.convert_price(new_price_raw, self.currency_rates)
            suggested_prices = self.api.convert_price(suggested_price_raw, self.currency_rates)
            
            # Calculate price change
            price_change_usd = new_prices['usd'] - old_prices['usd']
            price_change_eur = new_prices['eur'] - old_prices['eur']
            
            # Calculate percentage change
            price_change_percent = 0
            if old_prices['usd'] > 0:
                price_change_percent = (price_change_usd / old_prices['usd']) * 100
            
            # Extract item information
            item_name = raw_data.get('name', '')
            float_value = raw_data.get('float_value')
            
            wear_from_name = ItemProcessor.extract_wear_from_name(item_name)
            wear_from_float = ItemProcessor.get_wear_from_float(float_value)
            
            # Create price change document
            price_change_item = {
                'timestamp': datetime.utcnow(),
                'event_type': 'price_changed',
                'raw_data': raw_data,
                'processed_at': datetime.utcnow().isoformat(),
                'item_id': str(raw_data.get('id', '')),
                'item_name': item_name,
                'old_price_raw': old_price_raw,
                'new_price_raw': new_price_raw,
                'old_price_usd': old_prices['usd'],
                'new_price_usd': new_prices['usd'],
                'old_price_eur': old_prices['eur'],
                'new_price_eur': new_prices['eur'],
                'price_change_usd': price_change_usd,
                'price_change_eur': price_change_eur,
                'price_change_percent': price_change_percent,
                'suggested_price_raw': suggested_price_raw,
                'suggested_price_usd': suggested_prices['usd'],
                'suggested_price_eur': suggested_prices['eur'],
                'wear': wear_from_name,
                'wear_from_float': wear_from_float,
                'float_value': float_value,
                'skin_id': raw_data.get('skin_id'),
                'asset_id': str(raw_data.get('asset_id', '')),
                'app_id': raw_data.get('app_id'),
                'class_id': raw_data.get('class_id', ''),
                'paint_seed': raw_data.get('paint_seed'),
                'tradehold': raw_data.get('tradehold', 0),
                'bot_steam_id': raw_data.get('bot_steam_id', '')
            }
            
            # Store in MongoDB
            doc_id = self.db.store_document(self.collection_name, price_change_item)
            
            # Log the price change
            self.logger.info(f"✅ Stored price change in MongoDB with ID: {doc_id}")
            
            # Determine price change direction
            direction_emoji = "📈" if price_change_usd > 0 else "📉" if price_change_usd < 0 else "➡️"
            change_text = f"+${abs(price_change_usd):.3f}" if price_change_usd > 0 else f"-${abs(price_change_usd):.3f}"
            
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💲 PRICE CHANGE:")
            print(f"  🆔 Item ID: {price_change_item['item_id']}")
            print(f"  📦 Name: {price_change_item['item_name']}")
            print(f"  💰 Old Price: ${old_prices['usd']}")
            print(f"  💰 New Price: ${new_prices['usd']}")
            print(f"  {direction_emoji} Change: {change_text} ({price_change_percent:+.1f}%)")
            print(f"  💶 EUR Change: €{price_change_eur:+.3f}")
            print(f"  🏷️  Wear: {wear_from_name}")
            if float_value:
                print(f"  🎯 Float: {float_value:.6f}")
            print("-" * 60)
            
        except Exception as e:
            self.logger.error(f"Error processing price change: {e}")

def main():
    """Main execution function"""
    bot = PriceChangedBot()
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
