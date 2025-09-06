#!/usr/bin/env python3
"""
BitBot Dashboard API
Flask backend for the React dashboard
"""

import os
import sys
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from pymongo import MongoClient
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import io
import base64
import threading
import subprocess

# Add the parent directory to sys.path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.bitskins_common import BitSkinsConfig, BitSkinsDatabase

app = Flask(__name__)
CORS(app)

# Global variables for caching
_cached_data = None
_cache_timestamp = None
CACHE_DURATION = 0  # Disable caching for real-time updates

class DashboardAPI:
    def __init__(self):
        self.config = BitSkinsConfig()
        self.db = BitSkinsDatabase(self.config)
        
        # Collection references
        self.listed_items = self.db.get_collection('listed_items')
        self.price_changes = self.db.get_collection('price_changed_items')
        self.delisted_sold = self.db.get_collection('delisted_sold_items')
        
    def get_collection_stats(self):
        """Get basic stats from all collections"""
        stats = {
            'listed_count': self.listed_items.count_documents({}),
            'price_changes_count': self.price_changes.count_documents({}),
            'delisted_count': self.delisted_sold.count_documents({})
        }
        stats['total_records'] = sum(stats.values())
        return stats
    
    def get_recent_activity(self, hours=24):
        """Get activity from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_stats = {
            'recent_listed': self.listed_items.count_documents({
                'timestamp': {'$gte': cutoff_time}
            }),
            'recent_price_changes': self.price_changes.count_documents({
                'timestamp': {'$gte': cutoff_time}
            }),
            'recent_delisted': self.delisted_sold.count_documents({
                'timestamp': {'$gte': cutoff_time}
            })
        }
        
        return recent_stats
    
    def get_timeline_data(self, days=7):
        """Get timeline data for charts"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Create daily buckets
        timeline_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            day_str = current_date.strftime('%Y-%m-%d')
            
            daily_stats = {
                'date': day_str,
                'listed': self.listed_items.count_documents({
                    'timestamp': {
                        '$gte': current_date,
                        '$lt': next_date
                    }
                }),
                'priceChanges': self.price_changes.count_documents({
                    'timestamp': {
                        '$gte': current_date,
                        '$lt': next_date
                    }
                }),
                'delisted': self.delisted_sold.count_documents({
                    'timestamp': {
                        '$gte': current_date,
                        '$lt': next_date
                    }
                })
            }
            
            timeline_data.append(daily_stats)
            current_date = next_date
            
        return timeline_data
    
    def get_price_distribution(self):
        """Get price range distribution"""
        price_ranges = [
            {'range': '$0-10', 'min': 0, 'max': 10},
            {'range': '$10-50', 'min': 10, 'max': 50},
            {'range': '$50-100', 'min': 50, 'max': 100},
            {'range': '$100-500', 'min': 100, 'max': 500},
            {'range': '$500+', 'min': 500, 'max': float('inf')}
        ]
        
        distribution = []
        
        for price_range in price_ranges:
            query = {}
            if price_range['max'] == float('inf'):
                query['price_usd'] = {'$gte': price_range['min']}
            else:
                query['price_usd'] = {
                    '$gte': price_range['min'],
                    '$lt': price_range['max']
                }
            
            count = self.listed_items.count_documents(query)
            distribution.append({
                'range': price_range['range'],
                'count': count
            })
        
        return distribution
    
    def get_top_collections(self, limit=10):
        """Get top weapon types by activity"""
        # Since there's no collection_name field, let's group by weapon type from item names
        pipeline = [
            {'$project': {
                'weapon_type': {
                    '$arrayElemAt': [
                        {'$split': [
                            {'$arrayElemAt': [{'$split': ['$item_name', '|']}, 0]}, 
                            ' '
                        ]}, -1
                    ]
                }
            }},
            {'$group': {
                '_id': '$weapon_type',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        
        collections = []
        try:
            for result in self.listed_items.aggregate(pipeline):
                collections.append({
                    'name': result['_id'] or 'Unknown',
                    'value': result['count']
                })
        except Exception as e:
            print(f"Error getting collections: {e}")
            # Fallback: just show total items as one group
            total_count = self.listed_items.count_documents({})
            collections = [{'name': 'All Items', 'value': total_count}]
        
        return collections
    
    def get_volume_trends(self, days=7):
        """Get volume trends over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        volume_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Calculate daily volume based on price changes and listings
            daily_volume = 0
            
            # Approximate volume from price changes (could indicate sales)
            price_changes = list(self.price_changes.find({
                'timestamp': {
                    '$gte': current_date,
                    '$lt': next_date
                }
            }))
            
            for change in price_changes:
                if 'new_price_usd' in change:
                    daily_volume += change['new_price_usd']
            
            volume_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'volume': daily_volume
            })
            
            current_date = next_date
        
        return volume_data
    
    def get_advanced_analytics(self):
        """Get advanced analytics data"""
        try:
            # Market efficiency calculation
            total_items = self.listed_items.count_documents({})
            total_changes = self.price_changes.count_documents({})
            efficiency_score = min(100, (total_changes / max(total_items, 1)) * 100)
            
            # Volatility index (simplified)
            recent_changes = list(self.price_changes.find().sort('timestamp', -1).limit(100))
            volatility_scores = []
            for i in range(7):  # Last 7 days
                date = datetime.now() - timedelta(days=i)
                day_changes = [c for c in recent_changes if c.get('timestamp', datetime.min).date() == date.date()]
                volatility = len(day_changes) / max(total_items / 7, 1) * 100
                volatility_scores.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': volatility
                })
            
            # Correlation data (mock for now)
            correlation_data = []
            for i in range(10):
                correlation_data.append({
                    'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'volume': 100 + i * 10,
                    'price': 50 + i * 5
                })
            
            # Scatter plot data for price vs volume
            scatter_data = []
            for item in self.listed_items.find().limit(50):
                if 'price' in item:
                    scatter_data.append({
                        'x': item['price'],
                        'y': hash(str(item.get('_id', ''))) % 100,  # Mock volume
                        'collection': item.get('collection_name', 'Unknown')
                    })
            
            return {
                'volatility': volatility_scores,
                'efficiency': [{'name': 'Market Efficiency', 'value': efficiency_score}],
                'correlation': correlation_data,
                'scatter': scatter_data,
                'efficiency_score': efficiency_score
            }
            
        except Exception as e:
            print(f"Error getting advanced analytics: {e}")
            return {
                'volatility': [],
                'efficiency': [],
                'correlation': [],
                'scatter': [],
                'efficiency_score': 0
            }
    
    def get_collection_by_name(self, collection_name):
        """Get collection reference by name"""
        if collection_name == 'listed_items':
            return self.listed_items
        elif collection_name == 'price_changed_items':
            return self.price_changes
        elif collection_name == 'delisted_sold_items':
            return self.delisted_sold
        else:
            return self.listed_items  # Default fallback
    
    def get_sparkline_data(self, collection_name, days=7):
        """Get sparkline data for metric cards"""
        end_date = datetime.now()
        sparkline_data = []
        
        collection = self.get_collection_by_name(collection_name)
        
        for i in range(days):
            current_date = end_date - timedelta(days=days-1-i)
            next_date = current_date + timedelta(days=1)
            
            count = collection.count_documents({
                'timestamp': {
                    '$gte': current_date,
                    '$lt': next_date
                }
            })
            
            sparkline_data.append({
                'date': current_date.strftime('%m-%d'),
                'value': count
            })
        
        return sparkline_data

    def get_enhanced_metrics(self):
        """Get enhanced metrics with additional data"""
        stats = self.get_collection_stats()
        recent_activity = self.get_recent_activity()
        
        # Calculate additional metrics
        # Count unique weapon types instead of collection_name
        try:
            weapon_pipeline = [
                {'$project': {
                    'weapon_type': {
                        '$arrayElemAt': [
                            {'$split': [
                                {'$arrayElemAt': [{'$split': ['$item_name', '|']}, 0]}, 
                                ' '
                            ]}, -1
                        ]
                    }
                }},
                {'$group': {'_id': '$weapon_type'}}
            ]
            active_collections = len(list(self.listed_items.aggregate(weapon_pipeline)))
        except Exception as e:
            print(f"Error counting weapon types: {e}")
            active_collections = 0
        
        # Average price calculation
        price_pipeline = [
            {'$match': {'price_usd': {'$exists': True, '$type': 'number'}}},
            {'$group': {
                '_id': None,
                'avg_price': {'$avg': '$price_usd'},
                'total_items': {'$sum': 1}
            }}
        ]
        
        price_result = list(self.listed_items.aggregate(price_pipeline))
        avg_price = price_result[0]['avg_price'] if price_result else 0
        
        return {
            'totalListed': stats['listed_count'],
            'totalPriceChanges': stats['price_changes_count'],
            'totalDelisted': stats['delisted_count'],
            'totalRecords': stats['total_records'],
            'activeCollections': active_collections,
            'averagePrice': avg_price,
            'listedChange': 5.2,  # Mock data - would calculate from historical
            'priceChangeChange': -2.1,
            'delistedChange': 3.8,
            'recordsChange': 4.5,
            'collectionsChange': 1.2,
            'priceChange': 2.8
        }

    def get_enhanced_charts(self):
        """Get enhanced chart data"""
        base_charts = {
            'timeline': self.get_timeline_data(),
            'priceDistribution': self.get_price_distribution(),
            'collections': self.get_top_collections(),
            'volume': self.get_volume_trends()
        }
        
        # Add sparkline data for metric cards
        base_charts['listingSparkline'] = self.get_sparkline_data('listed_items')
        base_charts['priceSparkline'] = self.get_sparkline_data('price_changed_items')
        base_charts['velocitySparkline'] = self.get_sparkline_data('delisted_sold_items')
        
        return base_charts

# Initialize API instance
dashboard_api = DashboardAPI()

def get_cached_dashboard_data():
    """Get dashboard data with caching"""
    global _cached_data, _cache_timestamp
    
    now = datetime.now()
    print(f"Cache check: cached_data is None: {_cached_data is None}")
    print(f"Cache check: cache_timestamp is None: {_cache_timestamp is None}")
    if _cache_timestamp:
        print(f"Cache check: time since last cache: {(now - _cache_timestamp).total_seconds()}")
    print(f"Cache check: CACHE_DURATION: {CACHE_DURATION}")
    
    if (_cached_data is None or 
        _cache_timestamp is None or 
        (now - _cache_timestamp).total_seconds() > CACHE_DURATION):
        
        print("Fetching fresh dashboard data...")
        
        try:
            # Get enhanced metrics and charts
            metrics = dashboard_api.get_enhanced_metrics()
            charts = dashboard_api.get_enhanced_charts()
            
            _cached_data = {
                'metrics': metrics,
                'charts': charts,
                'status': 'healthy',
                'lastDataUpdate': now.isoformat()
            }
            _cache_timestamp = now
            
        except Exception as e:
            print(f"Error fetching dashboard data: {e}")
            _cached_data = {
                'metrics': {
                    'totalListed': 0,
                    'totalPriceChanges': 0,
                    'totalDelisted': 0,
                    'totalRecords': 0,
                    'activeCollections': 0,
                    'averagePrice': 0,
                    'listedChange': 0,
                    'priceChangeChange': 0,
                    'delistedChange': 0,
                    'recordsChange': 0,
                    'collectionsChange': 0,
                    'priceChange': 0
                },
                'charts': {
                    'timeline': [],
                    'priceDistribution': [],
                    'collections': [],
                    'volume': [],
                    'listingSparkline': [],
                    'priceSparkline': [],
                    'velocitySparkline': []
                },
                'status': 'error',
                'error': str(e),
                'lastDataUpdate': now.isoformat()
            }
            _cache_timestamp = now
    
    return _cached_data

@app.route('/api/advanced-analytics')
def get_advanced_analytics():
    """Get advanced analytics data endpoint"""
    try:
        advanced_data = dashboard_api.get_advanced_analytics()
        return jsonify(advanced_data)
    except Exception as e:
        return jsonify({
            'error': f'Failed to get advanced analytics: {str(e)}',
            'volatility': [],
            'efficiency': [],
            'correlation': [],
            'scatter': [],
            'efficiency_score': 0
        }), 500

@app.route('/api/dashboard')
def get_dashboard_data():
    """Get dashboard data endpoint"""
    print(f"Dashboard endpoint called at {datetime.now()}")
    try:
        print("Fetching fresh dashboard data...")
        # Get enhanced metrics and charts  
        metrics = dashboard_api.get_enhanced_metrics()
        charts = dashboard_api.get_enhanced_charts()
        
        return jsonify({
            'metrics': metrics,
            'charts': charts,
            'status': 'healthy',
            'lastDataUpdate': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return jsonify({
            'metrics': {
                'totalListed': 0,
                'totalPriceChanges': 0,
                'totalDelisted': 0,
                'totalRecords': 0,
                'activeCollections': 0,
                'averagePrice': 0,
                'listedChange': 0,
                'priceChangeChange': 0,
                'delistedChange': 0,
                'recordsChange': 0,
                'collectionsChange': 0,
                'priceChange': 0
            },
            'charts': {
                'timeline': [],
                'priceDistribution': [],
                'collections': [],
                'volume': [],
                'listingSparkline': [],
                'priceSparkline': [],
                'velocitySparkline': []
            },
            'status': 'error',
            'lastDataUpdate': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate analytics report endpoint"""
    try:
        # Run the market report script
        result = subprocess.run([
            'python', 
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analytics', 'market_report.py')
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Report generated successfully',
                'reportUrl': '/api/download-report'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Report generation failed: {result.stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate report: {str(e)}'
        }), 500

@app.route('/api/download-report')
def download_report():
    """Download the latest report"""
    try:
        # Look for the latest report file
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
        report_files = [f for f in os.listdir(reports_dir) if f.startswith('BitSkins_Market_Analytics_Report')]
        
        if not report_files:
            return jsonify({'error': 'No report files found'}), 404
            
        latest_report = max(report_files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
        report_path = os.path.join(reports_dir, latest_report)
        
        return send_file(report_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': f'Failed to download report: {str(e)}'}), 500

@app.route('/api/export-data')
def export_data():
    """Export raw data as JSON"""
    try:
        data = get_cached_dashboard_data()
        
        # Create a more detailed export
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'dashboard_data': data,
            'collections_summary': {
                'listed_items': dashboard_api.get_collection_stats()['listed_count'],
                'price_changes': dashboard_api.get_collection_stats()['price_changes_count'],
                'delisted_sold': dashboard_api.get_collection_stats()['delisted_count']
            }
        }
        
        # Convert to JSON and create file-like object
        json_data = json.dumps(export_data, indent=2, default=str)
        json_file = io.StringIO(json_data)
        
        return send_file(
            io.BytesIO(json_data.encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'bitbot_data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to export data: {str(e)}'}), 500

@app.route('/api/debug')
def debug_endpoint():
    """Debug endpoint to isolate issues"""
    results = {}
    
    try:
        results['collection_stats'] = dashboard_api.get_collection_stats()
    except Exception as e:
        results['collection_stats_error'] = str(e)
    
    try:
        results['enhanced_metrics'] = dashboard_api.get_enhanced_metrics()
    except Exception as e:
        results['enhanced_metrics_error'] = str(e)
        
    try:
        results['enhanced_charts'] = dashboard_api.get_enhanced_charts()
    except Exception as e:
        results['enhanced_charts_error'] = str(e)
    
    return jsonify(results)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        stats = dashboard_api.get_collection_stats()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'total_records': stats['total_records'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Starting BitBot Dashboard API...")
    print("📊 Dashboard will be available at: http://localhost:3001")
    print("🔧 API endpoints available at: http://localhost:5000/api/*")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
