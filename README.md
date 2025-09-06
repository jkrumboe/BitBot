# BitBot - BitSkins Market Analytics Suite

A comprehensive suite of bots and analytics tools for monitoring BitSkins marketplace activity with real-time data visualization.

## Features

### 🤖 Automated Market Monitoring
- **Listed Items Bot**: Tracks newly listed items across all collections
- **Price Changes Bot**: Monitors price modifications on existing listings  
- **Delisted/Sold Bot**: Records when items are removed or sold
- **Real-time Data Collection**: Continuous monitoring via WebSocket connections

### 📊 Analytics Dashboard
- **Real-time Visualization**: Interactive web dashboard with live market data
- **Market Insights**: Price distribution, trading volume, and activity trends
- **One-click Reports**: Generate comprehensive analytics reports
- **Data Export**: Export collected data in multiple formats

### 🔧 Infrastructure
- **MongoDB Storage**: Scalable database for market data
- **Docker Support**: Easy deployment with Docker Compose
- **Modular Architecture**: Shared utilities and configuration management

## Quick Start

### Option 1: Dashboard Only (Recommended for first-time users)

1. **Test setup:**
   ```bash
   .\scripts\test_dashboard_setup.bat
   ```

2. **Start dashboard:**
   ```bash
   .\scripts\start_dashboard.bat
   ```

3. **Access dashboard:**
   - Open: http://localhost:3001
   - API: http://localhost:5001

### Option 2: Complete Suite with Docker

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access services:**
   - Dashboard: http://localhost:3001
   - MongoDB Admin: http://localhost:8081
   - API: http://localhost:5001

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   Analytics     │    │   Data Bots     │
│   (React)       │    │   API (Flask)   │    │                 │
│                 │    │                 │    │ • Listed Bot    │
│ • Real-time UI  │◄──►│ • Data API      │◄──►│ • Price Bot     │
│ • Charts        │    │ • Report Gen    │    │ • Delisted Bot  │
│ • Actions       │    │ • Export        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │   MongoDB       │
                       │                 │
                       │ • listed_items  │
                       │ • price_changes │
                       │ • delisted_sold │
                       └─────────────────┘
```

## Components

### Bots (`/bots/`)
- `listed/listed_bot.py` - Monitors new item listings
- `price_changed/price_changed_bot.py` - Tracks price modifications
- `delisted_sold/delisted_sold_bot.py` - Records item removals/sales

### Analytics (`/analytics/`)
- `analytics_dashboard.py` - Dashboard data processing
- `market_report.py` - Comprehensive report generation

### Dashboard (`/web-dashboard/`)
- React-based real-time dashboard
- Interactive charts and visualizations
- Report generation interface
- Data export functionality

### API (`/api/`)
- Flask REST API for dashboard data
- Report generation endpoints
- Data export functionality
- Health monitoring

### Shared Utilities (`/shared/`)
- `bitskins_common.py` - Common functions and database utilities
- Configuration management
- Database connection handling

## Data Collections

The system stores data in MongoDB collections:

| Collection | Description | Key Fields |
|------------|-------------|------------|
| `listed_items` | Newly listed items | `item_id`, `price`, `collection_name`, `timestamp` |
| `price_changed_items` | Price modifications | `item_id`, `old_price`, `new_price`, `timestamp` |
| `delisted_sold_items` | Removed/sold items | `item_id`, `reason`, `timestamp` |

## Configuration

### Environment Variables
- `BITSKINS_API_KEY` - Your BitSkins API key
- `MONGODB_URI` - MongoDB connection string
- `DATABASE_NAME` - Database name (default: `bitskins_bot`)

### Default Settings
- MongoDB: `localhost:27018`
- Dashboard: `localhost:3001`
- API: `localhost:5001`
- MongoDB Admin: `localhost:8081`

## Scripts

### Windows (`/scripts/`)
- `start_dashboard.bat` - Start dashboard and API
- `start_all_bots.bat` - Start all monitoring bots
- `test_dashboard_setup.bat` - Test installation and dependencies
- Individual bot scripts for granular control

### Analytics
- `run_analytics.bat` - Generate market analytics report

## Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (via Docker or local)
- BitSkins API key (optional)

### Local Development
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start MongoDB: `docker-compose up -d mongodb`
4. Run individual components as needed

### Adding New Features
1. **New Bot**: Create in `/bots/` following existing patterns
2. **Dashboard Metrics**: Add to `DashboardAPI` class in `/api/dashboard_api.py`
3. **Chart Types**: Add to React components in `/web-dashboard/src/App.js`

## Production Deployment

### Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment
1. Set up MongoDB cluster
2. Deploy API server with proper environment variables
3. Build and serve React app with nginx
4. Configure reverse proxy and SSL

## Monitoring

### Health Checks
- API: `GET /api/health`
- Dashboard: Connection status indicator
- Logs: Docker logs or console output

### Data Quality
- Real-time data freshness indicators
- Collection count monitoring
- Error tracking and reporting

## Troubleshooting

### Common Issues
1. **Dashboard shows no data**: Check MongoDB connection and bot status
2. **API errors**: Verify MongoDB URI and permissions
3. **Report generation fails**: Check Python dependencies and file permissions

### Logs Location
- Container logs: `docker-compose logs [service_name]`
- Local logs: Console output from individual scripts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow existing code patterns
4. Test thoroughly with the dashboard
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Test individual components
4. Create an issue with detailed information
