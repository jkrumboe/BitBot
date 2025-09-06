# BitBot Analytics Dashboard

A real-time React-based dashboard for visualizing BitSkins market data and generating analytics reports.

## Features

🚀 **Real-time Data Visualization**
- Live market activity metrics
- Interactive charts and graphs
- Price distribution analysis
- Collection activity breakdown

📊 **Analytics & Reporting**
- One-click analytics report generation
- Data export functionality
- Historical trend analysis
- Market volume tracking

🔄 **Real-time Updates**
- Auto-refresh every 30 seconds
- Live connection status indicators
- Data freshness timestamps

## Quick Start

### Method 1: Development Mode (Recommended for local testing)

1. **Start the dashboard:**
   ```bash
   # Windows
   .\scripts\start_dashboard.bat
   
   # Linux/Mac
   ./scripts/start_dashboard.sh
   ```

2. **Access the dashboard:**
   - Frontend: http://localhost:3000
   - API: http://localhost:5000/api/dashboard

### Method 2: Docker (Recommended for production)

1. **Start all services including dashboard:**
   ```bash
   docker-compose up -d
   ```

2. **Access the dashboard:**
   - Frontend: http://localhost:3000
   - API: http://localhost:5000/api/dashboard

## Dashboard Components

### Key Metrics Cards
- **Total Listed Items**: Current number of items listed
- **Price Changes**: Total price change events
- **Delisted/Sold Items**: Items removed from listings
- **Database Records**: Total records across all collections

### Interactive Charts
- **Market Activity Over Time**: Line chart showing listing, price change, and delisting trends
- **Price Range Distribution**: Bar chart of items by price ranges
- **Top Collections by Activity**: Pie chart of most active collections
- **Trading Volume Trends**: Area chart of trading volume over time

### Actions
- **Refresh Data**: Manually refresh dashboard data
- **Generate Report**: Create and download a comprehensive analytics report
- **Export Data**: Download raw data as JSON

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard` | GET | Get dashboard data and metrics |
| `/api/generate-report` | POST | Generate analytics report |
| `/api/download-report` | GET | Download latest report |
| `/api/export-data` | GET | Export data as JSON |
| `/api/health` | GET | Health check |

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   Flask API     │    │   MongoDB       │
│   (Port 3000)   │◄──►│   (Port 5000)   │◄──►│   (Port 27018)  │
│                 │    │                 │    │                 │
│ - Dashboard UI  │    │ - Data API      │    │ - Collections:  │
│ - Charts        │    │ - Report Gen    │    │   • listed_items│
│ - Actions       │    │ - Data Export   │    │   • price_changes│
└─────────────────┘    └─────────────────┘    │   • delisted_sold│
                                               └─────────────────┘
```

## Data Flow

1. **Bots** collect data and store in MongoDB collections
2. **Flask API** aggregates data from MongoDB and provides REST endpoints
3. **React Dashboard** fetches data from API and displays interactive visualizations
4. **Report Generator** creates detailed analytics reports on demand

## Development

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB (via Docker or local installation)

### Local Development Setup

1. **Install Python dependencies:**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. **Install React dependencies:**
   ```bash
   cd web-dashboard
   npm install
   ```

3. **Start the API server:**
   ```bash
   cd api
   python dashboard_api.py
   ```

4. **Start the React development server:**
   ```bash
   cd web-dashboard
   npm start
   ```

### Environment Variables

The dashboard uses the following environment variables:

- `MONGODB_URI`: MongoDB connection string (default: `mongodb://admin:password123@localhost:27018/bitskins_bot?authSource=admin`)
- `BITSKINS_API_KEY`: BitSkins API key (optional, for demo mode warning)

## Customization

### Adding New Metrics
1. Update `DashboardAPI.get_collection_stats()` in `api/dashboard_api.py`
2. Add new metric cards in `src/App.js`
3. Update the metrics grid CSS if needed

### Adding New Charts
1. Add data aggregation method in `api/dashboard_api.py`
2. Add chart component to `src/App.js` using Recharts
3. Include in the charts grid

### Styling
- Main styles: `src/index.css`
- Component-specific styles: Inline or additional CSS files
- Color scheme: Update CSS variables for theme changes

## Troubleshooting

### Common Issues

1. **Dashboard shows "Offline" status:**
   - Check if MongoDB is running
   - Verify API server is running on port 5000
   - Check network connectivity between services

2. **No data in charts:**
   - Ensure bots are running and collecting data
   - Check MongoDB collections have data
   - Verify database connection in API logs

3. **Report generation fails:**
   - Check if analytics scripts are accessible
   - Verify Python dependencies are installed
   - Check file permissions for report output

### Logs
- API logs: Console output from `dashboard_api.py`
- React logs: Browser console and terminal output
- Docker logs: `docker-compose logs dashboard_api` or `docker-compose logs dashboard_frontend`

## Production Considerations

- Use environment-specific MongoDB URIs
- Enable HTTPS with proper SSL certificates
- Set up proper logging and monitoring
- Configure backup strategies for data
- Use production-grade web server (nginx) instead of development servers
- Implement authentication and authorization if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the BitBot suite. Please refer to the main project license.
