#!/usr/bin/env python3
"""
Shared utilities and common functions for BitSkins bots
"""

import os
import asyncio
import json
import websockets
import requests
from datetime import datetime
from pymongo import MongoClient
from typing import Dict, Any, Optional
import logging

class BitSkinsConfig:
    """Configuration management for BitSkins bots"""
    
    def __init__(self):
        self.api_key = os.getenv('BITSKINS_API_KEY')
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://admin:password123@localhost:27019/bitskins_bot?authSource=admin')
        self.database_name = os.getenv('DATABASE_NAME', 'bitskins_bot')
        self.websocket_url = "wss://ws.bitskins.com"
        self.api_base_url = "https://api.bitskins.com"
        
        if not self.api_key:
            logging.warning("BITSKINS_API_KEY environment variable not set - using demo mode")

class BitSkinsDatabase:
    """Database operations for BitSkins data"""
    
    def __init__(self, config: BitSkinsConfig):
        self.config = config
        self.client = MongoClient(config.mongodb_uri)
        self.db = self.client[config.database_name]
    
    def get_collection(self, collection_name: str):
        """Get a MongoDB collection"""
        return self.db[collection_name]
    
    def store_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Store a document in the specified collection"""
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    def close(self):
        """Close database connection"""
        self.client.close()

class BitSkinsAPI:
    """BitSkins API utilities"""
    
    def __init__(self, config: BitSkinsConfig):
        self.config = config
    
    def get_currency_rates(self) -> Dict[str, float]:
        """Get current currency exchange rates"""
        # Default currency rates as fallback
        default_rates = {'EUR': 0.92, 'GBP': 0.81, 'CAD': 1.35, 'AUD': 1.45}
        
        try:
            # Check if API key is available
            if not self.config.api_key:
                logging.warning("No API key provided, using default currency rates")
                return default_rates
            
            # Use new currency API endpoint with proper headers
            headers = {'x-apikey': self.config.api_key}
            response = requests.get(f"{self.config.api_base_url}/config/currency/list", 
                                  headers=headers, 
                                  timeout=10)
            
            # Check if response is successful
            if response.status_code != 200:
                logging.error(f"Currency API request failed with status {response.status_code}: {response.text}")
                return default_rates
            
            # Check if response has content
            if not response.text.strip():
                logging.error("Currency API returned empty response")
                return default_rates
            
            # Try to parse JSON
            try:
                data = response.json()
            except json.JSONDecodeError as json_error:
                logging.error(f"Failed to parse currency JSON response: {json_error}")
                logging.error(f"Response content: {response.text[:200]}...")  # Log first 200 chars
                return default_rates
            
            # Extract currency rates from new API format
            if data and isinstance(data, dict):
                # The new API likely returns rates in a different format
                # We'll need to adapt based on actual response structure
                rates = {}
                
                # Try to extract rates from common response formats
                if 'data' in data and isinstance(data['data'], dict):
                    rates = data['data']
                elif 'rates' in data and isinstance(data['rates'], dict):
                    rates = data['rates']
                elif isinstance(data, dict):
                    rates = data
                
                if rates:
                    logging.info(f"Successfully retrieved {len(rates)} currency rates from API")
                    return rates
                else:
                    logging.warning("No currency rates found in API response, using defaults")
                    return default_rates
            else:
                logging.error(f"Unexpected currency API response format: {data}")
                return default_rates
                
        except requests.exceptions.RequestException as req_error:
            logging.error(f"Currency request failed: {req_error}")
            return default_rates
        except Exception as e:
            logging.error(f"Failed to get currency rates: {e}")
            return default_rates
    
    def convert_price(self, price_cents: int, rates: Dict[str, float]) -> Dict[str, float]:
        """Convert price from cents to USD and EUR"""
        price_usd = price_cents / 1000  # BitSkins uses different scale
        price_eur = price_usd * rates.get('EUR', 0.92)  # Default EUR rate if not available
        
        return {
            'usd': round(price_usd, 3),
            'eur': round(price_eur, 3)
        }
    
    def get_account_profile(self) -> Dict[str, Any]:
        """Get current session information"""
        try:
            if not self.config.api_key:
                logging.warning("No API key provided for profile request")
                return {}
            
            headers = {'x-apikey': self.config.api_key}
            response = requests.get(f"{self.config.api_base_url}/account/profile/me", 
                                  headers=headers, 
                                  timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logging.info("Successfully retrieved account profile")
                return data
            else:
                logging.error(f"Profile request failed with status {response.status_code}: {response.text}")
                return {}
                
        except Exception as e:
            logging.error(f"Failed to get account profile: {e}")
            return {}
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        try:
            if not self.config.api_key:
                logging.warning("No API key provided for balance request")
                return {}
            
            headers = {'x-apikey': self.config.api_key}
            data = {}
            response = requests.post(f"{self.config.api_base_url}/account/profile/balance", 
                                   headers=headers, 
                                   json=data,
                                   timeout=10)
            
            if response.status_code == 200:
                balance_data = response.json()
                logging.info("Successfully retrieved account balance")
                return balance_data
            else:
                logging.error(f"Balance request failed with status {response.status_code}: {response.text}")
                return {}
                
        except Exception as e:
            logging.error(f"Failed to get account balance: {e}")
            return {}
    
    def search_my_items(self, limit: int = 30, offset: int = 0, search_filters: Dict = None) -> Dict[str, Any]:
        """Search for CS2 items you own"""
        try:
            if not self.config.api_key:
                logging.warning("No API key provided for item search")
                return {}
            
            headers = {'x-apikey': self.config.api_key}
            data = {
                "limit": limit,
                "offset": offset
            }
            
            if search_filters:
                data.update(search_filters)
            
            response = requests.post(f"{self.config.api_base_url}/market/search/mine/730", 
                                   headers=headers, 
                                   json=data,
                                   timeout=10)
            
            if response.status_code == 200:
                items_data = response.json()
                logging.info(f"Successfully retrieved {len(items_data.get('data', []))} owned items")
                return items_data
            else:
                logging.error(f"Item search failed with status {response.status_code}: {response.text}")
                return {}
                
        except Exception as e:
            logging.error(f"Failed to search owned items: {e}")
            return {}

class ItemProcessor:
    """Common item processing utilities"""
    
    @staticmethod
    def get_wear_from_float(float_value: Optional[float]) -> str:
        """Convert float value to wear condition"""
        if float_value is None:
            return "Unknown"
        
        if float_value < 0.07:
            return "Factory New"
        elif float_value < 0.15:
            return "Minimal Wear"
        elif float_value < 0.38:
            return "Field-Tested"
        elif float_value < 0.45:
            return "Well-Worn"
        else:
            return "Battle-Scarred"
    
    @staticmethod
    def extract_wear_from_name(item_name: str) -> str:
        """Extract wear condition from item name"""
        if not item_name:
            return "Unknown"
        
        wear_conditions = [
            ("(Factory New)", "Factory New"),
            ("(Minimal Wear)", "Minimal Wear"), 
            ("(Field-Tested)", "Field-Tested"),
            ("(Well-Worn)", "Well-Worn"),
            ("(Battle-Scarred)", "Battle-Scarred")
        ]
        
        for pattern, wear in wear_conditions:
            if pattern in item_name:
                return wear
        
        return "Unknown"
    
    @staticmethod
    def process_base_item_data(raw_data: Dict[str, Any], api: BitSkinsAPI, rates: Dict[str, float]) -> Dict[str, Any]:
        """Process common item data fields"""
        # Convert prices
        price_raw = raw_data.get('price', 0)
        suggested_price_raw = raw_data.get('suggested_price', 0)
        
        prices = api.convert_price(price_raw, rates)
        suggested_prices = api.convert_price(suggested_price_raw, rates)
        
        # Extract wear information
        item_name = raw_data.get('name', '')
        float_value = raw_data.get('float_value')
        
        wear_from_name = ItemProcessor.extract_wear_from_name(item_name)
        wear_from_float = ItemProcessor.get_wear_from_float(float_value)
        
        return {
            'item_id': str(raw_data.get('id', '')),
            'item_name': item_name,
            'price_raw': price_raw,
            'price_usd': prices['usd'],
            'price_eur': prices['eur'],
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

class WebSocketBot:
    """Base class for WebSocket bots"""
    
    def __init__(self, bot_name: str, event_types: list):
        self.bot_name = bot_name
        self.event_types = event_types
        self.config = BitSkinsConfig()
        self.db = BitSkinsDatabase(self.config)
        self.api = BitSkinsAPI(self.config)
        self.currency_rates = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.bot_name)
    
    async def authenticate_and_subscribe(self, websocket):
        """Authenticate and subscribe to events using new WebSocket format"""
        # Authenticate using new format: [action, data]
        if self.config.api_key:
            auth_message = ["WS_AUTH_APIKEY", self.config.api_key]
        else:
            self.logger.warning("No API key available, cannot authenticate WebSocket")
            return
        
        await websocket.send(json.dumps(auth_message))
        auth_response = await websocket.recv()
        
        try:
            auth_data = json.loads(auth_response)
            # New format returns [action, data]
            if isinstance(auth_data, list) and len(auth_data) >= 2:
                action, data = auth_data[0], auth_data[1]
                if action and action.startswith('WS_AUTH'):
                    self.logger.info(f"🔐 Authenticated for {', '.join(self.event_types)} monitoring")
                else:
                    raise Exception(f"Authentication failed: {auth_data}")
            else:
                raise Exception(f"Unexpected authentication response format: {auth_data}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid authentication response: {auth_response}")
        
        # Subscribe to events using new format
        # Note: Authentication clears previous subscriptions, so we subscribe after auth
        for event_type in self.event_types:
            subscribe_message = ["WS_SUB", event_type]
            await websocket.send(json.dumps(subscribe_message))
        
        self.logger.info(f"📡 Subscribed to {', '.join(self.event_types)} events")
    
    async def get_currency_rates(self):
        """Fetch current currency rates"""
        self.currency_rates = self.api.get_currency_rates()
        if not self.currency_rates:
            self.logger.warning("Failed to get currency rates, using defaults")
            self.currency_rates = {'EUR': 0.92, 'GBP': 0.81, 'CAD': 1.35, 'AUD': 1.45}  # Default rates
    
    async def process_message(self, message_data: Dict[str, Any]):
        """Process incoming WebSocket message - to be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement process_message")
    
    async def run(self):
        """Main bot execution loop"""
        self.logger.info(f"🚀 Starting {self.bot_name}...")
        
        # Get currency rates and account info
        await self.get_currency_rates()
        await self.get_account_info()
        
        while True:
            try:
                async with websockets.connect(self.config.websocket_url) as websocket:
                    await self.authenticate_and_subscribe(websocket)
                    
                    async for message in websocket:
                        try:
                            # New format: [action, data]
                            message_data = json.loads(message)
                            
                            if isinstance(message_data, list) and len(message_data) >= 2:
                                action, data = message_data[0], message_data[1]
                                
                                # Convert to old format for compatibility with existing processing
                                processed_message = {
                                    'action': action,
                                    'data': data
                                }
                                
                                await self.process_message(processed_message)
                            else:
                                self.logger.warning(f"Unexpected message format: {message_data}")
                                
                        except json.JSONDecodeError:
                            self.logger.error(f"Invalid JSON received: {message}")
                        except Exception as e:
                            self.logger.error(f"Error processing message: {e}")
                            
            except websockets.exceptions.ConnectionClosed:
                self.logger.warning("WebSocket connection closed, reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(10)
    
    async def get_account_info(self):
        """Get account information for additional context"""
        try:
            profile = self.api.get_account_profile()
            balance = self.api.get_account_balance()
            
            if profile:
                self.logger.info(f"📋 Account Profile: {profile.get('data', {}).get('username', 'Unknown')}")
            if balance:
                self.logger.info(f"💰 Account Balance: ${balance.get('data', {}).get('balance', 0)}")
                
        except Exception as e:
            self.logger.warning(f"Could not retrieve account info: {e}")
    
    def close(self):
        """Clean up resources"""
        self.db.close()
