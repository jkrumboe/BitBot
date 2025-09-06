#!/usr/bin/env python3
"""
BitSkins API Test Script
Tests the new API endpoints and WebSocket connections
"""

import os
import sys
import asyncio
import json
import websockets
from datetime import datetime

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from bitskins_common import BitSkinsConfig, BitSkinsAPI

async def test_websocket():
    """Test WebSocket connection with new format"""
    config = BitSkinsConfig()
    
    if not config.api_key:
        print("❌ No API key available for WebSocket test")
        return
    
    print("🔌 Testing WebSocket connection...")
    
    try:
        async with websockets.connect(config.websocket_url) as websocket:
            # Authenticate using new format
            auth_message = ["WS_AUTH_APIKEY", config.api_key]
            await websocket.send(json.dumps(auth_message))
            
            # Wait for auth response
            auth_response = await websocket.recv()
            auth_data = json.loads(auth_response)
            
            print(f"🔐 Auth response: {auth_data}")
            
            if isinstance(auth_data, list) and len(auth_data) >= 2:
                action, data = auth_data[0], auth_data[1]
                if action and action.startswith('WS_AUTH'):
                    print("✅ WebSocket authentication successful")
                    
                    # Subscribe to channels
                    channels = ["listed", "price_changed", "delisted_or_sold"]
                    for channel in channels:
                        subscribe_message = ["WS_SUB", channel]
                        await websocket.send(json.dumps(subscribe_message))
                        print(f"📡 Subscribed to {channel}")
                    
                    # Listen for a few messages
                    print("👂 Listening for messages (10 seconds)...")
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        print(f"📨 Received message: {message}")
                    except asyncio.TimeoutError:
                        print("⏰ No messages received in 10 seconds (this is normal if market is quiet)")
                        
                else:
                    print(f"❌ Authentication failed: {auth_data}")
            else:
                print(f"❌ Unexpected auth response format: {auth_data}")
                
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

def test_api_endpoints():
    """Test the new API endpoints"""
    config = BitSkinsConfig()
    api = BitSkinsAPI(config)
    
    print("🧪 Testing API endpoints...")
    
    # Test currency rates
    print("\n💱 Testing currency rates...")
    rates = api.get_currency_rates()
    if rates:
        print(f"✅ Currency rates: {list(rates.keys())[:5]}...")  # Show first 5 currencies
    else:
        print("❌ Could not retrieve currency rates")
    
    if not config.api_key:
        print("⚠️  No API key - skipping authenticated endpoint tests")
        return
    
    # Test account profile
    print("\n👤 Testing account profile...")
    profile = api.get_account_profile()
    if profile:
        print(f"✅ Profile retrieved: {profile.get('data', {}).get('username', 'Unknown user')}")
    else:
        print("❌ Could not retrieve profile")
    
    # Test account balance
    print("\n💰 Testing account balance...")
    balance = api.get_account_balance()
    if balance:
        balance_amount = balance.get('data', {}).get('balance', 'Unknown')
        print(f"✅ Balance retrieved: ${balance_amount}")
    else:
        print("❌ Could not retrieve balance")
    
    # Test searching owned items
    print("\n🎮 Testing owned items search...")
    items = api.search_my_items(limit=5)
    if items and 'data' in items:
        item_count = len(items['data'])
        print(f"✅ Found {item_count} owned items")
    else:
        print("❌ Could not retrieve owned items")

def main():
    """Run all tests"""
    print("🚀 BitSkins API Test Suite")
    print("=" * 50)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test regular API endpoints
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    
    # Test WebSocket
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    
    print("\n🏁 Test suite completed!")

if __name__ == "__main__":
    main()
