#!/usr/bin/env python3
"""
BitSkins Market Analytics Dashboard
Analyzes seller and buyer behavior patterns across all collections
"""

import os
import sys
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set up matplotlib for better plotting
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class BitSkinsAnalytics:
    def __init__(self):
        # Connect to MongoDB
        self.mongodb_uri = "mongodb://admin:password123@localhost:27018/bitskins_bot?authSource=admin"
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client['bitskins_bot']
        
        # Collection references
        self.listed_items = self.db['listed_items']
        self.price_changes = self.db['price_changed_items']
        self.delisted_sold = self.db['delisted_sold_items']
        
        print("🔗 Connected to BitSkins Analytics Database")
        print("=" * 60)
    
    def load_data(self):
        """Load all data from collections into pandas DataFrames"""
        print("📊 Loading data from all collections...")
        
        # Load listed items
        listed_cursor = self.listed_items.find()
        self.df_listed = pd.DataFrame(list(listed_cursor))
        
        # Load price changes
        price_cursor = self.price_changes.find()
        self.df_price_changes = pd.DataFrame(list(price_cursor))
        
        # Load delisted/sold items
        delisted_cursor = self.delisted_sold.find()
        self.df_delisted = pd.DataFrame(list(delisted_cursor))
        
        print(f"✅ Listed Items: {len(self.df_listed):,} records")
        print(f"✅ Price Changes: {len(self.df_price_changes):,} records")
        print(f"✅ Delisted/Sold: {len(self.df_delisted):,} records")
        print(f"📈 Total Records: {len(self.df_listed) + len(self.df_price_changes) + len(self.df_delisted):,}")
        print()
    
    def analyze_pricing_behavior(self):
        """Analyze pricing patterns and seller behavior"""
        print("💰 PRICING BEHAVIOR ANALYSIS")
        print("-" * 40)
        
        if len(self.df_price_changes) == 0:
            print("❌ No price change data available")
            return
        
        # Convert prices to numeric
        self.df_price_changes['new_price_usd'] = pd.to_numeric(self.df_price_changes['new_price_usd'], errors='coerce')
        self.df_price_changes['old_price_usd'] = pd.to_numeric(self.df_price_changes['old_price_usd'], errors='coerce')
        self.df_price_changes['price_change_usd'] = pd.to_numeric(self.df_price_changes['price_change_usd'], errors='coerce')
        
        # Price change distribution
        price_increases = len(self.df_price_changes[self.df_price_changes['price_change_usd'] > 0])
        price_decreases = len(self.df_price_changes[self.df_price_changes['price_change_usd'] < 0])
        no_change = len(self.df_price_changes[self.df_price_changes['price_change_usd'] == 0])
        
        print(f"📈 Price Increases: {price_increases:,} ({price_increases/len(self.df_price_changes)*100:.1f}%)")
        print(f"📉 Price Decreases: {price_decreases:,} ({price_decreases/len(self.df_price_changes)*100:.1f}%)")
        print(f"➡️  No Change: {no_change:,} ({no_change/len(self.df_price_changes)*100:.1f}%)")
        
        # Average price change
        avg_change = self.df_price_changes['price_change_usd'].mean()
        print(f"💵 Average Price Change: ${avg_change:.3f}")
        
        # Price ranges analysis
        price_ranges = {
            "Under $1": len(self.df_price_changes[self.df_price_changes['new_price_usd'] < 1]),
            "$1-$10": len(self.df_price_changes[(self.df_price_changes['new_price_usd'] >= 1) & (self.df_price_changes['new_price_usd'] < 10)]),
            "$10-$50": len(self.df_price_changes[(self.df_price_changes['new_price_usd'] >= 10) & (self.df_price_changes['new_price_usd'] < 50)]),
            "$50-$100": len(self.df_price_changes[(self.df_price_changes['new_price_usd'] >= 50) & (self.df_price_changes['new_price_usd'] < 100)]),
            "$100+": len(self.df_price_changes[self.df_price_changes['new_price_usd'] >= 100])
        }
        
        print("\n🏷️ Price Range Distribution:")
        for range_name, count in price_ranges.items():
            percentage = count / len(self.df_price_changes) * 100
            print(f"   {range_name}: {count:,} items ({percentage:.1f}%)")
        print()
    
    def analyze_item_categories(self):
        """Analyze most popular item types and categories"""
        print("🎮 ITEM CATEGORY ANALYSIS")
        print("-" * 40)
        
        all_items = []
        
        # Combine all item names
        if len(self.df_listed) > 0:
            all_items.extend(self.df_listed['item_name'].tolist())
        if len(self.df_price_changes) > 0:
            all_items.extend(self.df_price_changes['item_name'].tolist())
        if len(self.df_delisted) > 0:
            all_items.extend(self.df_delisted['item_name'].tolist())
        
        if not all_items:
            print("❌ No item data available")
            return
        
        # Categorize items
        weapon_types = defaultdict(int)
        skin_types = defaultdict(int)
        wear_conditions = defaultdict(int)
        
        for item_name in all_items:
            if pd.isna(item_name):
                continue
                
            name = str(item_name)
            
            # Extract weapon types
            if "AK-47" in name:
                weapon_types["AK-47"] += 1
            elif "M4A4" in name:
                weapon_types["M4A4"] += 1
            elif "M4A1-S" in name:
                weapon_types["M4A1-S"] += 1
            elif "AWP" in name:
                weapon_types["AWP"] += 1
            elif "Glock-18" in name:
                weapon_types["Glock-18"] += 1
            elif "★" in name and "Knife" in name:
                weapon_types["Knives"] += 1
            elif "★" in name and "Gloves" in name:
                weapon_types["Gloves"] += 1
            elif "Sticker" in name:
                weapon_types["Stickers"] += 1
            elif "Case" in name:
                weapon_types["Cases"] += 1
            else:
                weapon_types["Other"] += 1
            
            # Extract wear conditions
            if "(Factory New)" in name:
                wear_conditions["Factory New"] += 1
            elif "(Minimal Wear)" in name:
                wear_conditions["Minimal Wear"] += 1
            elif "(Field-Tested)" in name:
                wear_conditions["Field-Tested"] += 1
            elif "(Well-Worn)" in name:
                wear_conditions["Well-Worn"] += 1
            elif "(Battle-Scarred)" in name:
                wear_conditions["Battle-Scarred"] += 1
            else:
                wear_conditions["Unknown/NA"] += 1
        
        # Top weapon types
        print("🔫 Top Weapon Categories:")
        for weapon, count in sorted(weapon_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = count / len(all_items) * 100
            print(f"   {weapon}: {count:,} items ({percentage:.1f}%)")
        
        print("\n🎨 Wear Condition Distribution:")
        for condition, count in sorted(wear_conditions.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(all_items) * 100
            print(f"   {condition}: {count:,} items ({percentage:.1f}%)")
        print()
        
        return weapon_types, wear_conditions
    
    def analyze_temporal_patterns(self):
        """Analyze time-based patterns"""
        print("⏰ TEMPORAL PATTERN ANALYSIS")
        print("-" * 40)
        
        all_timestamps = []
        
        # Collect timestamps from all collections
        for df, name in [(self.df_listed, 'listed'), (self.df_price_changes, 'price_changes'), (self.df_delisted, 'delisted')]:
            if len(df) > 0 and 'timestamp' in df.columns:
                for ts in df['timestamp']:
                    if pd.notna(ts):
                        try:
                            if isinstance(ts, str):
                                dt = pd.to_datetime(ts)
                            else:
                                dt = ts
                            all_timestamps.append((dt, name))
                        except:
                            continue
        
        if not all_timestamps:
            print("❌ No timestamp data available")
            return
        
        # Convert to DataFrame
        df_time = pd.DataFrame(all_timestamps, columns=['timestamp', 'event_type'])
        df_time['hour'] = df_time['timestamp'].dt.hour
        df_time['day_of_week'] = df_time['timestamp'].dt.day_name()
        
        # Activity by hour
        hourly_activity = df_time['hour'].value_counts().sort_index()
        print("📅 Activity by Hour (UTC):")
        peak_hour = hourly_activity.idxmax()
        print(f"   Peak Hour: {peak_hour}:00 UTC ({hourly_activity[peak_hour]} events)")
        print(f"   Quietest Hour: {hourly_activity.idxmin()}:00 UTC ({hourly_activity.min()} events)")
        
        # Activity by day of week
        daily_activity = df_time['day_of_week'].value_counts()
        print(f"\n📊 Most Active Day: {daily_activity.idxmax()} ({daily_activity.max()} events)")
        print(f"   Least Active Day: {daily_activity.idxmin()} ({daily_activity.min()} events)")
        print()
        
        return df_time
    
    def analyze_seller_behavior(self):
        """Analyze seller behavior patterns"""
        print("👤 SELLER BEHAVIOR ANALYSIS")
        print("-" * 40)
        
        # Analyze bot_steam_ids (sellers) from price changes
        if len(self.df_price_changes) > 0 and 'bot_steam_id' in self.df_price_changes.columns:
            seller_activity = self.df_price_changes['bot_steam_id'].value_counts()
            
            print(f"🤖 Active Sellers: {len(seller_activity):,}")
            print(f"📊 Most Active Seller: {seller_activity.iloc[0]:,} price changes")
            print(f"📈 Average Activity: {seller_activity.mean():.1f} price changes per seller")
            
            # Analyze pricing strategies
            seller_strategies = {}
            for seller_id in seller_activity.head(10).index:
                seller_data = self.df_price_changes[self.df_price_changes['bot_steam_id'] == seller_id]
                increases = len(seller_data[seller_data['price_change_usd'] > 0])
                decreases = len(seller_data[seller_data['price_change_usd'] < 0])
                
                if increases + decreases > 0:
                    increase_ratio = increases / (increases + decreases)
                    seller_strategies[seller_id] = {
                        'total_changes': len(seller_data),
                        'increase_ratio': increase_ratio,
                        'avg_change': seller_data['price_change_usd'].mean()
                    }
            
            print(f"\n💡 Top Seller Strategies (Top 10 by activity):")
            for i, (seller_id, stats) in enumerate(list(seller_strategies.items())[:5]):
                strategy = "Aggressive Pricer" if stats['increase_ratio'] > 0.6 else "Price Cutter" if stats['increase_ratio'] < 0.4 else "Balanced"
                print(f"   Seller #{i+1}: {strategy} ({stats['increase_ratio']*100:.1f}% increases, {stats['total_changes']} changes)")
        else:
            print("❌ No seller data available")
        print()
    
    def create_visualizations(self, weapon_types=None, wear_conditions=None, df_time=None):
        """Create comprehensive visualizations"""
        print("📊 CREATING VISUALIZATIONS")
        print("-" * 40)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Collection Overview
        plt.subplot(3, 4, 1)
        collections = ['Listed', 'Price Changes', 'Delisted/Sold']
        counts = [len(self.df_listed), len(self.df_price_changes), len(self.df_delisted)]
        colors = ['#2ecc71', '#f39c12', '#e74c3c']
        plt.pie(counts, labels=collections, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('📊 Data Distribution by Collection', fontsize=12, fontweight='bold')
        
        # 2. Price Change Distribution
        if len(self.df_price_changes) > 0:
            plt.subplot(3, 4, 2)
            price_changes = self.df_price_changes['price_change_usd'].dropna()
            plt.hist(price_changes, bins=50, alpha=0.7, color='#3498db', edgecolor='black')
            plt.axvline(price_changes.mean(), color='red', linestyle='--', label=f'Mean: ${price_changes.mean():.3f}')
            plt.xlabel('Price Change (USD)')
            plt.ylabel('Frequency')
            plt.title('💰 Price Change Distribution', fontsize=12, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        # 3. Top Weapon Categories
        if weapon_types:
            plt.subplot(3, 4, 3)
            top_weapons = dict(sorted(weapon_types.items(), key=lambda x: x[1], reverse=True)[:8])
            plt.bar(range(len(top_weapons)), list(top_weapons.values()), color='#9b59b6')
            plt.xticks(range(len(top_weapons)), list(top_weapons.keys()), rotation=45, ha='right')
            plt.ylabel('Count')
            plt.title('🔫 Top Weapon Categories', fontsize=12, fontweight='bold')
            plt.grid(True, alpha=0.3)
        
        # 4. Wear Condition Distribution
        if wear_conditions:
            plt.subplot(3, 4, 4)
            wear_colors = ['#27ae60', '#f1c40f', '#e67e22', '#d35400', '#c0392b', '#95a5a6']
            plt.pie(wear_conditions.values(), labels=wear_conditions.keys(), 
                   colors=wear_colors[:len(wear_conditions)], autopct='%1.1f%%', startangle=90)
            plt.title('🎨 Wear Condition Distribution', fontsize=12, fontweight='bold')
        
        # 5. Activity Timeline
        if df_time is not None and len(df_time) > 0:
            plt.subplot(3, 4, 5)
            hourly_activity = df_time['hour'].value_counts().sort_index()
            plt.plot(hourly_activity.index, hourly_activity.values, marker='o', linewidth=2, color='#e74c3c')
            plt.xlabel('Hour (UTC)')
            plt.ylabel('Events')
            plt.title('⏰ Activity by Hour', fontsize=12, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.xticks(range(0, 24, 2))
        
        # 6. Daily Activity
        if df_time is not None and len(df_time) > 0:
            plt.subplot(3, 4, 6)
            daily_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_activity = df_time['day_of_week'].value_counts()
            daily_values = [daily_activity.get(day, 0) for day in daily_order]
            plt.bar(range(7), daily_values, color='#16a085')
            plt.xticks(range(7), [day[:3] for day in daily_order])
            plt.ylabel('Events')
            plt.title('📅 Activity by Day of Week', fontsize=12, fontweight='bold')
            plt.grid(True, alpha=0.3)
        
        # 7. Price Ranges
        if len(self.df_price_changes) > 0:
            plt.subplot(3, 4, 7)
            prices = self.df_price_changes['new_price_usd'].dropna()
            price_ranges = {
                "< $1": len(prices[prices < 1]),
                "$1-10": len(prices[(prices >= 1) & (prices < 10)]),
                "$10-50": len(prices[(prices >= 10) & (prices < 50)]),
                "$50-100": len(prices[(prices >= 50) & (prices < 100)]),
                "$100+": len(prices[prices >= 100])
            }
            plt.bar(range(len(price_ranges)), list(price_ranges.values()), color='#8e44ad')
            plt.xticks(range(len(price_ranges)), list(price_ranges.keys()), rotation=45)
            plt.ylabel('Count')
            plt.title('💵 Price Range Distribution', fontsize=12, fontweight='bold')
            plt.grid(True, alpha=0.3)
        
        # 8. Event Type Timeline
        if df_time is not None and len(df_time) > 0:
            plt.subplot(3, 4, 8)
            event_counts = df_time['event_type'].value_counts()
            colors_map = {'listed': '#2ecc71', 'price_changes': '#f39c12', 'delisted': '#e74c3c'}
            colors = [colors_map.get(event, '#95a5a6') for event in event_counts.index]
            plt.bar(range(len(event_counts)), event_counts.values, color=colors)
            plt.xticks(range(len(event_counts)), event_counts.index, rotation=45)
            plt.ylabel('Count')
            plt.title('📈 Event Type Distribution', fontsize=12, fontweight='bold')
            plt.grid(True, alpha=0.3)
        
        # 9-12. Additional analytics based on available data
        if len(self.df_price_changes) > 0:
            # Price change patterns
            plt.subplot(3, 4, 9)
            increases = len(self.df_price_changes[self.df_price_changes['price_change_usd'] > 0])
            decreases = len(self.df_price_changes[self.df_price_changes['price_change_usd'] < 0])
            no_change = len(self.df_price_changes[self.df_price_changes['price_change_usd'] == 0])
            
            plt.bar(['Increases', 'Decreases', 'No Change'], [increases, decreases, no_change], 
                   color=['#27ae60', '#e74c3c', '#95a5a6'])
            plt.ylabel('Count')
            plt.title('📊 Price Movement Patterns', fontsize=12, fontweight='bold')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('bitskins_analytics_dashboard.png', dpi=300, bbox_inches='tight')
        print("✅ Dashboard saved as 'bitskins_analytics_dashboard.png'")
        plt.show()
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\n" + "="*60)
        print("📋 BITSKINS MARKET ANALYTICS SUMMARY REPORT")
        print("="*60)
        
        total_records = len(self.df_listed) + len(self.df_price_changes) + len(self.df_delisted)
        
        print(f"📊 Data Overview:")
        print(f"   • Total Records Analyzed: {total_records:,}")
        print(f"   • Analysis Period: Live monitoring data")
        print(f"   • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n🎯 Key Insights:")
        
        # Market activity
        if len(self.df_delisted) > len(self.df_listed):
            print(f"   • 🔥 High Market Velocity: {len(self.df_delisted):,} items sold vs {len(self.df_listed):,} newly listed")
        else:
            print(f"   • 📈 Growing Inventory: {len(self.df_listed):,} new listings vs {len(self.df_delisted):,} items sold")
        
        # Price volatility
        if len(self.df_price_changes) > 0:
            volatile_items = len(self.df_price_changes[abs(self.df_price_changes['price_change_usd']) > 1])
            print(f"   • 💹 Price Volatility: {volatile_items:,} items with price changes > $1")
        
        # Most active category
        all_items = []
        if len(self.df_listed) > 0:
            all_items.extend(self.df_listed['item_name'].dropna().tolist())
        if len(self.df_price_changes) > 0:
            all_items.extend(self.df_price_changes['item_name'].dropna().tolist())
        if len(self.df_delisted) > 0:
            all_items.extend(self.df_delisted['item_name'].dropna().tolist())
        
        if all_items:
            if any("Sticker" in str(item) for item in all_items):
                sticker_count = sum(1 for item in all_items if "Sticker" in str(item))
                print(f"   • 🏷️ Stickers Popular: {sticker_count:,} sticker-related events")
            
            if any("★" in str(item) for item in all_items):
                rare_count = sum(1 for item in all_items if "★" in str(item))
                print(f"   • ⭐ Premium Items Active: {rare_count:,} rare item events (knives/gloves)")
        
        print(f"\n💡 Recommendations:")
        print(f"   • Monitor high-frequency price changers for arbitrage opportunities")
        print(f"   • Focus on categories with high listing-to-sale ratios")
        print(f"   • Track seller behavior patterns for competitive pricing")
        
        print("\n" + "="*60)
    
    def run_complete_analysis(self):
        """Run the complete analytics suite"""
        print("🚀 STARTING COMPREHENSIVE BITSKINS ANALYTICS")
        print("="*60)
        
        # Load data
        self.load_data()
        
        # Run all analyses
        self.analyze_pricing_behavior()
        weapon_types, wear_conditions = self.analyze_item_categories()
        df_time = self.analyze_temporal_patterns()
        self.analyze_seller_behavior()
        
        # Create visualizations
        self.create_visualizations(weapon_types, wear_conditions, df_time)
        
        # Generate summary
        self.generate_summary_report()

def main():
    """Main execution function"""
    try:
        analytics = BitSkinsAnalytics()
        analytics.run_complete_analysis()
        
        print("\n🎉 Analytics completed successfully!")
        print("📊 Dashboard saved as 'bitskins_analytics_dashboard.png'")
        print("🔍 Check the visual charts and insights above!")
        
    except Exception as e:
        print(f"❌ Error running analytics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
