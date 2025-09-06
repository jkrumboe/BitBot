#!/usr/bin/env python3
"""
BitSkins Market Analytics Report Generator
Professional market analysis with comprehensive insights and visualizations
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

# Set up matplotlib for professional styling
plt.style.use('default')
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

class BitSkinsMarketReport:
    def __init__(self):
        # Connect to MongoDB
        self.mongodb_uri = "mongodb://admin:password123@localhost:27019/bitskins_bot?authSource=admin"
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client['bitskins_bot']
        
        # Collection references
        self.listed_items = self.db['listed_items']
        self.price_changes = self.db['price_changed_items']
        self.delisted_sold = self.db['delisted_sold_items']
        
        # Report metadata
        self.report_timestamp = datetime.now()
        self.analysis_period = "Live Market Data"
        
        print("📊 BitSkins Market Analytics Report")
        print("=" * 55)
        print(f"Generated: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data Source: MongoDB Collections")
        print("=" * 55)
    
    def load_and_prepare_data(self):
        """Load and prepare data with data quality metrics"""
        print("\n🔄 LOADING & PREPARING DATA")
        print("-" * 35)
        
        # Load data
        listed_cursor = self.listed_items.find()
        self.df_listed = pd.DataFrame(list(listed_cursor))
        
        price_cursor = self.price_changes.find()
        self.df_price_changes = pd.DataFrame(list(price_cursor))
        
        delisted_cursor = self.delisted_sold.find()
        self.df_delisted = pd.DataFrame(list(delisted_cursor))
        
        # Calculate data quality metrics
        total_records = len(self.df_listed) + len(self.df_price_changes) + len(self.df_delisted)
        
        print(f"📦 Listed Items:      {len(self.df_listed):>6,} records")
        print(f"💲 Price Changes:     {len(self.df_price_changes):>6,} records")
        print(f"🗑️  Delisted/Sold:     {len(self.df_delisted):>6,} records")
        print(f"📊 Total Dataset:     {total_records:>6,} records")
        
        # Data freshness
        if total_records > 0:
            latest_timestamps = []
            for df in [self.df_listed, self.df_price_changes, self.df_delisted]:
                if len(df) > 0 and 'timestamp' in df.columns:
                    latest_timestamps.append(df['timestamp'].max())
            
            if latest_timestamps:
                latest_data = max(latest_timestamps)
                data_age = self.report_timestamp - latest_data
                print(f"⏱️  Data Freshness:    {data_age.total_seconds()/60:.1f} minutes ago")
        
        print("✅ Data loading completed")
        return total_records
    
    def generate_executive_summary(self):
        """Generate executive summary with key metrics"""
        print("\n📋 EXECUTIVE SUMMARY")
        print("-" * 35)
        
        # Market activity metrics
        listing_rate = len(self.df_listed)
        sales_rate = len(self.df_delisted)
        price_volatility = len(self.df_price_changes)
        
        # Market velocity
        if listing_rate > 0:
            market_velocity = sales_rate / listing_rate
            velocity_status = "High" if market_velocity > 1.5 else "Moderate" if market_velocity > 0.5 else "Low"
        else:
            market_velocity = 0
            velocity_status = "No Data"
        
        print(f"🏪 Market Velocity:     {velocity_status} ({market_velocity:.2f})")
        print(f"📈 New Listings:       {listing_rate:,} items")
        print(f"💰 Items Sold:         {sales_rate:,} items")
        print(f"🔄 Price Adjustments:  {price_volatility:,} changes")
        
        # Price movement analysis
        if len(self.df_price_changes) > 0:
            increases = len(self.df_price_changes[self.df_price_changes['price_change_usd'] > 0])
            decreases = len(self.df_price_changes[self.df_price_changes['price_change_usd'] < 0])
            
            if increases > decreases:
                market_trend = "🔥 Bullish (Price Increases)"
            elif decreases > increases:
                market_trend = "❄️  Bearish (Price Decreases)"
            else:
                market_trend = "⚖️  Stable (Balanced Movement)"
                
            print(f"📊 Market Sentiment:   {market_trend}")
            
            avg_change = self.df_price_changes['price_change_usd'].mean()
            print(f"💵 Avg Price Change:   ${avg_change:.3f}")
        
        # Activity concentration
        total_events = listing_rate + sales_rate + price_volatility
        if total_events > 100:
            activity_level = "🚀 Very High"
        elif total_events > 50:
            activity_level = "📈 High"
        elif total_events > 20:
            activity_level = "📊 Moderate"
        else:
            activity_level = "📉 Low"
            
        print(f"⚡ Activity Level:     {activity_level}")
        
        return {
            'market_velocity': market_velocity,
            'velocity_status': velocity_status,
            'market_trend': market_trend,
            'activity_level': activity_level,
            'total_events': total_events
        }
    
    def analyze_market_segments(self):
        """Analyze different market segments and price tiers"""
        print("\n🎯 MARKET SEGMENT ANALYSIS")
        print("-" * 35)
        
        segments = {
            'Budget Items (< $5)': 0,
            'Mid-Tier ($5-$50)': 0,
            'Premium ($50-$200)': 0,
            'Luxury ($200+)': 0
        }
        
        all_prices = []
        
        # Collect prices from all sources
        if len(self.df_listed) > 0:
            all_prices.extend(self.df_listed['price_usd'].dropna().tolist())
        if len(self.df_price_changes) > 0:
            all_prices.extend(self.df_price_changes['new_price_usd'].dropna().tolist())
        if len(self.df_delisted) > 0:
            all_prices.extend(self.df_delisted['price_usd'].dropna().tolist())
        
        if all_prices:
            for price in all_prices:
                if price < 5:
                    segments['Budget Items (< $5)'] += 1
                elif price < 50:
                    segments['Mid-Tier ($5-$50)'] += 1
                elif price < 200:
                    segments['Premium ($50-$200)'] += 1
                else:
                    segments['Luxury ($200+)'] += 1
            
            total_items = sum(segments.values())
            
            print("💰 Price Tier Distribution:")
            for segment, count in segments.items():
                percentage = (count / total_items * 100) if total_items > 0 else 0
                print(f"   {segment:<20} {count:>4,} items ({percentage:>5.1f}%)")
            
            # Market statistics
            avg_price = np.mean(all_prices)
            median_price = np.median(all_prices)
            max_price = max(all_prices)
            min_price = min(all_prices)
            
            print(f"\n📊 Price Statistics:")
            print(f"   Average Price:      ${avg_price:>8.2f}")
            print(f"   Median Price:       ${median_price:>8.2f}")
            print(f"   Price Range:        ${min_price:.2f} - ${max_price:,.2f}")
        
        return segments
    
    def analyze_item_categories(self):
        """Enhanced item category analysis"""
        print("\n🎮 ITEM CATEGORY BREAKDOWN")
        print("-" * 35)
        
        all_items = []
        
        # Combine all item names
        if len(self.df_listed) > 0:
            all_items.extend(self.df_listed['item_name'].dropna().tolist())
        if len(self.df_price_changes) > 0:
            all_items.extend(self.df_price_changes['item_name'].dropna().tolist())
        if len(self.df_delisted) > 0:
            all_items.extend(self.df_delisted['item_name'].dropna().tolist())
        
        if not all_items:
            print("❌ No item data available")
            return {}, {}
        
        categories = {
            'Rifles': ['AK-47', 'M4A4', 'M4A1-S', 'AWP', 'Galil', 'FAMAS', 'AUG', 'SG 553'],
            'Pistols': ['Glock-18', 'USP-S', 'P2000', 'Tec-9', 'Five-SeveN', 'CZ75', 'Desert Eagle', 'Dual Berettas', 'P250'],
            'SMGs': ['P90', 'Bizon', 'UMP-45', 'MAC-10', 'MP9', 'MP7', 'MP5-SD'],
            'Shotguns': ['Nova', 'XM1014', 'Sawed-Off', 'MAG-7'],
            'Snipers': ['AWP', 'SSG 08', 'G3SG1', 'SCAR-20'],
            'Machine Guns': ['M249', 'Negev'],
            'Knives': ['★'],
            'Gloves': ['★.*Gloves'],
            'Stickers': ['Sticker'],
            'Cases': ['Case'],
            'Agents': ['Agent', 'FBI', 'SAS', 'SWAT']
        }
        
        category_counts = defaultdict(int)
        
        for item_name in all_items:
            if pd.isna(item_name):
                continue
                
            name = str(item_name)
            categorized = False
            
            for category, keywords in categories.items():
                if any(keyword in name for keyword in keywords):
                    category_counts[category] += 1
                    categorized = True
                    break
            
            if not categorized:
                category_counts['Other'] += 1
        
        # Sort by count and display
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        total_items = sum(category_counts.values())
        
        print("🏷️ Category Distribution:")
        for category, count in sorted_categories[:10]:  # Top 10
            percentage = (count / total_items * 100) if total_items > 0 else 0
            print(f"   {category:<12} {count:>4,} items ({percentage:>5.1f}%)")
        
        # Wear condition analysis
        wear_conditions = defaultdict(int)
        for item_name in all_items:
            if pd.isna(item_name):
                continue
            name = str(item_name)
            
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
                wear_conditions["Unknown/N/A"] += 1
        
        print(f"\n🎨 Condition Distribution:")
        for condition, count in sorted(wear_conditions.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_items * 100) if total_items > 0 else 0
            print(f"   {condition:<15} {count:>4,} items ({percentage:>5.1f}%)")
        
        return dict(category_counts), dict(wear_conditions)
    
    def create_professional_report(self, segments, categories, wear_conditions, summary_stats):
        """Create a professional-looking analytics report"""
        print("\n📊 GENERATING VISUAL REPORT")
        print("-" * 35)
        
        # Create figure with custom layout
        fig = plt.figure(figsize=(20, 24))
        fig.suptitle('BitSkins Market Analytics Report', fontsize=20, fontweight='bold', y=0.98)
        
        # Add report metadata
        fig.text(0.02, 0.96, f"Generated: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}", 
                fontsize=10, style='italic')
        fig.text(0.02, 0.94, f"Analysis Period: {self.analysis_period}", 
                fontsize=10, style='italic')
        
        # Color palette
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592941', '#6A994E', '#BC4749']
        
        # 1. Market Overview Dashboard (Top Row)
        gs = fig.add_gridspec(6, 4, hspace=0.4, wspace=0.3)
        
        # Market Summary Stats
        ax_summary = fig.add_subplot(gs[0, :])
        ax_summary.axis('off')
        
        # Create summary table
        summary_text = f"""
        MARKET OVERVIEW
        Market Velocity: {summary_stats['velocity_status']} ({summary_stats['market_velocity']:.2f})
        Activity Level: {summary_stats['activity_level']}
        Total Events: {summary_stats['total_events']:,}
        Market Trend: {summary_stats['market_trend']}
        """
        
        ax_summary.text(0.05, 0.5, summary_text, fontsize=14, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.7),
                       verticalalignment='center')
        
        # 2. Collection Distribution (Pie Chart)
        ax1 = fig.add_subplot(gs[1, 0])
        collections = ['Listed Items', 'Price Changes', 'Delisted/Sold']
        counts = [len(self.df_listed), len(self.df_price_changes), len(self.df_delisted)]
        wedges, texts, autotexts = ax1.pie(counts, labels=collections, colors=colors[:3], 
                                          autopct='%1.1f%%', startangle=90)
        ax1.set_title('📊 Data Distribution', fontweight='bold', pad=20)
        
        # 3. Price Movement Analysis
        if len(self.df_price_changes) > 0:
            ax2 = fig.add_subplot(gs[1, 1])
            increases = len(self.df_price_changes[self.df_price_changes['price_change_usd'] > 0])
            decreases = len(self.df_price_changes[self.df_price_changes['price_change_usd'] < 0])
            no_change = len(self.df_price_changes[self.df_price_changes['price_change_usd'] == 0])
            
            bars = ax2.bar(['Price Up', 'Price Down', 'No Change'], 
                          [increases, decreases, no_change], 
                          color=['#27ae60', '#e74c3c', '#95a5a6'])
            ax2.set_title('💰 Price Movement Patterns', fontweight='bold')
            ax2.set_ylabel('Count')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Market Segments
        if segments:
            ax3 = fig.add_subplot(gs[1, 2])
            seg_names = list(segments.keys())
            seg_values = list(segments.values())
            ax3.pie(seg_values, labels=seg_names, colors=colors[:len(seg_names)], 
                   autopct='%1.1f%%', startangle=90)
            ax3.set_title('💵 Price Segments', fontweight='bold')
        
        # 5. Top Categories
        if categories:
            ax4 = fig.add_subplot(gs[1, 3])
            top_categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:6])
            bars = ax4.bar(range(len(top_categories)), list(top_categories.values()), color=colors[0])
            ax4.set_xticks(range(len(top_categories)))
            ax4.set_xticklabels(list(top_categories.keys()), rotation=45, ha='right')
            ax4.set_title('🎮 Top Item Categories', fontweight='bold')
            ax4.set_ylabel('Count')
        
        # 6. Wear Condition Distribution
        if wear_conditions:
            ax5 = fig.add_subplot(gs[2, 0])
            wear_colors = ['#27ae60', '#f1c40f', '#e67e22', '#d35400', '#c0392b', '#95a5a6']
            wedges = ax5.pie(wear_conditions.values(), labels=wear_conditions.keys(), 
                            colors=wear_colors[:len(wear_conditions)], autopct='%1.1f%%', startangle=90)
            ax5.set_title('🎨 Item Conditions', fontweight='bold')
        
        # 7. Price Distribution Histogram
        if len(self.df_price_changes) > 0:
            ax6 = fig.add_subplot(gs[2, 1])
            prices = self.df_price_changes['new_price_usd'].dropna()
            n, bins, patches = ax6.hist(prices, bins=30, alpha=0.7, color=colors[1], edgecolor='black')
            ax6.axvline(prices.mean(), color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: ${prices.mean():.2f}')
            ax6.set_xlabel('Price (USD)')
            ax6.set_ylabel('Frequency')
            ax6.set_title('💲 Price Distribution', fontweight='bold')
            ax6.legend()
            ax6.grid(True, alpha=0.3)
        
        # 8. Activity Timeline (if temporal data available)
        all_timestamps = []
        for df in [self.df_listed, self.df_price_changes, self.df_delisted]:
            if len(df) > 0 and 'timestamp' in df.columns:
                for ts in df['timestamp'].dropna():
                    try:
                        if isinstance(ts, str):
                            dt = pd.to_datetime(ts)
                        else:
                            dt = ts
                        all_timestamps.append(dt)
                    except:
                        continue
        
        if all_timestamps:
            ax7 = fig.add_subplot(gs[2, 2])
            df_time = pd.DataFrame({'timestamp': all_timestamps})
            df_time['hour'] = df_time['timestamp'].dt.hour
            hourly_activity = df_time['hour'].value_counts().sort_index()
            
            ax7.plot(hourly_activity.index, hourly_activity.values, marker='o', 
                    linewidth=2, color=colors[3], markersize=6)
            ax7.set_xlabel('Hour (UTC)')
            ax7.set_ylabel('Events')
            ax7.set_title('⏰ Activity by Hour', fontweight='bold')
            ax7.grid(True, alpha=0.3)
            ax7.set_xticks(range(0, 24, 4))
        
        # 9. Key Metrics Table
        ax8 = fig.add_subplot(gs[2, 3])
        ax8.axis('off')
        
        # Calculate additional metrics
        total_items = len(self.df_listed) + len(self.df_price_changes) + len(self.df_delisted)
        
        if len(self.df_price_changes) > 0:
            avg_price_change = self.df_price_changes['price_change_usd'].mean()
            max_price_change = self.df_price_changes['price_change_usd'].max()
            min_price_change = self.df_price_changes['price_change_usd'].min()
        else:
            avg_price_change = max_price_change = min_price_change = 0
        
        metrics_text = f"""
KEY METRICS

Total Items: {total_items:,}
Active Listings: {len(self.df_listed):,}
Items Sold: {len(self.df_delisted):,}
Price Changes: {len(self.df_price_changes):,}

Avg Price Change: ${avg_price_change:.3f}
Max Price Change: ${max_price_change:.2f}
Min Price Change: ${min_price_change:.2f}
        """
        
        ax8.text(0.05, 0.95, metrics_text, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen', alpha=0.7))
        
        # Add detailed analysis sections
        
        # 10. Market Insights Section
        ax9 = fig.add_subplot(gs[3, :])
        ax9.axis('off')
        
        insights_text = "📈 MARKET INSIGHTS\n\n"
        
        if summary_stats['market_velocity'] > 1.0:
            insights_text += "• High market turnover indicates strong buyer demand\n"
        elif summary_stats['market_velocity'] < 0.5:
            insights_text += "• Low market turnover suggests buyer hesitation or overpricing\n"
        else:
            insights_text += "• Balanced market turnover indicates healthy supply-demand equilibrium\n"
        
        if len(self.df_price_changes) > 0:
            volatility = self.df_price_changes['price_change_usd'].std()
            if volatility > 5:
                insights_text += "• High price volatility suggests an active, speculative market\n"
            else:
                insights_text += "• Low price volatility indicates stable pricing conditions\n"
        
        # Category insights
        if categories:
            top_category = max(categories.items(), key=lambda x: x[1])
            insights_text += f"• {top_category[0]} items dominate the market with {top_category[1]:,} listings\n"
        
        ax9.text(0.02, 0.8, insights_text, fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.8", facecolor='lightyellow', alpha=0.8))
        
        # 11. Recommendations Section
        ax10 = fig.add_subplot(gs[4, :])
        ax10.axis('off')
        
        recommendations_text = "💡 TRADING RECOMMENDATIONS\n\n"
        
        if summary_stats['market_velocity'] > 1.2:
            recommendations_text += "• Consider quick flips on popular items due to high turnover\n"
        elif summary_stats['market_velocity'] < 0.7:
            recommendations_text += "• Focus on underpriced items that may take time to sell\n"
        
        if len(self.df_price_changes) > 0:
            avg_change = self.df_price_changes['price_change_usd'].mean()
            if avg_change > 0:
                recommendations_text += "• Market trend is upward - consider buying before further increases\n"
            else:
                recommendations_text += "• Market trend is downward - wait for better buying opportunities\n"
        
        recommendations_text += "• Monitor high-activity categories for arbitrage opportunities\n"
        recommendations_text += "• Track seller behavior patterns for competitive pricing strategies"
        
        ax10.text(0.02, 0.8, recommendations_text, fontsize=12, verticalalignment='top',
                 bbox=dict(boxstyle="round,pad=0.8", facecolor='lightcoral', alpha=0.8))
        
        # 12. Footer with data source info
        ax11 = fig.add_subplot(gs[5, :])
        ax11.axis('off')
        
        footer_text = f"""
        DATA SOURCE: BitSkins API WebSocket Live Feed | REPORT GENERATED: {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        Total Records Analyzed: {total_items:,} | Data Freshness: Live Stream | Analysis Period: Real-time Monitoring
        """
        
        ax11.text(0.5, 0.5, footer_text, fontsize=10, ha='center', va='center',
                 style='italic', bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('BitSkins_Market_Analytics_Report.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        print("✅ Professional report saved as 'BitSkins_Market_Analytics_Report.png'")
        plt.show()
    
    def generate_complete_report(self):
        """Generate the complete professional market report"""
        print("🚀 BITSKINS MARKET ANALYTICS REPORT")
        print("=" * 55)
        
        # Load data
        total_records = self.load_and_prepare_data()
        
        if total_records == 0:
            print("❌ No data available for analysis")
            return
        
        # Generate analysis sections
        summary_stats = self.generate_executive_summary()
        segments = self.analyze_market_segments()
        categories, wear_conditions = self.analyze_item_categories()
        
        # Create visual report
        self.create_professional_report(segments, categories, wear_conditions, summary_stats)
        
        print("\n" + "="*55)
        print("📊 REPORT GENERATION COMPLETED")
        print("="*55)
        print("✅ Professional analytics report generated successfully!")
        print("📁 Report saved as: BitSkins_Market_Analytics_Report.png")
        print("🔍 Review the comprehensive market insights above!")

def main():
    """Main execution function"""
    try:
        report = BitSkinsMarketReport()
        report.generate_complete_report()
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
