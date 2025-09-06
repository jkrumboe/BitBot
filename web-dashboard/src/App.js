import React, { useState, useEffect, useCallback } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Database, 
  RefreshCw, 
  FileText, 
  Download,
  Clock,
  AlertCircle,
  CheckCircle,
  Settings,
  Filter,
  Calendar,
  Eye,
  BarChart3,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon,
  DollarSign,
  Users,
  ShoppingCart,
  Target,
  Zap,
  Bell,
  Search,
  Info,
  ArrowUpDown
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ComposedChart,
  Legend,
  ReferenceLine,
  Scatter,
  ScatterChart,
  RadialBarChart,
  RadialBar
} from 'recharts';
import axios from 'axios';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'];
const CHART_THEMES = {
  purple: ['#667eea', '#764ba2', '#9f7aea'],
  blue: ['#4facfe', '#00f2fe', '#00d4ff'],
  green: ['#43e97b', '#38f9d7', '#2dd4bf'],
  pink: ['#f093fb', '#f5576c', '#ec4899']
};

function App() {
  const [data, setData] = useState({
    metrics: null,
    charts: null,
    advanced: null,
    loading: true,
    error: null,
    lastUpdated: null
  });
  const [reportLoading, setReportLoading] = useState(false);
  const [reportStatus, setReportStatus] = useState('');
  const [settings, setSettings] = useState({
    autoRefresh: true,
    refreshInterval: 5,  // Changed from 30 to 5 seconds
    theme: 'purple',
    chartType: 'line',
    timeRange: '7d',
    showAlerts: true
  });
  const [activeTab, setActiveTab] = useState('overview');
  const [alerts, setAlerts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    priceRange: 'all',
    collection: 'all',
    timeframe: '24h'
  });
  const [apiRequest, setApiRequest] = useState({
    method: 'GET',
    endpoint: '/api/dashboard',
    body: '',
    response: '',
    loading: false,
    error: null
  });

  useEffect(() => {
    fetchDashboardData();
    // Refresh data based on settings
    const interval = setInterval(() => {
      if (settings.autoRefresh) {
        fetchDashboardData();
      }
    }, settings.refreshInterval * 1000);
    return () => clearInterval(interval);
  }, [settings.autoRefresh, settings.refreshInterval]);

  const fetchDashboardData = useCallback(async () => {
    try {
      const [dashboardResponse, advancedResponse] = await Promise.all([
        axios.get('/api/dashboard'),
        axios.get('/api/advanced-analytics').catch(() => ({ data: null })) // Fallback if endpoint doesn't exist
      ]);
      
      const newData = {
        ...dashboardResponse.data,
        advanced: advancedResponse.data,
        loading: false,
        error: null,
        lastUpdated: new Date()
      };
      
      setData(newData);
      
      // Generate alerts based on data changes
      generateAlerts(newData);
      
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setData(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to load dashboard data. Please check if the backend service is running.'
      }));
    }
  }, []);

  const generateAlerts = (newData) => {
    const newAlerts = [];
    
    if (newData.metrics) {
      // High activity alert
      if (newData.metrics.totalListed > 1000) {
        newAlerts.push({
          id: 'high-activity',
          type: 'info',
          message: `High market activity detected: ${newData.metrics.totalListed} items listed`
        });
      }
      
      // Price volatility alert
      if (Math.abs(newData.metrics.priceChangeChange) > 10) {
        newAlerts.push({
          id: 'price-volatility',
          type: 'warning',
          message: `High price volatility: ${newData.metrics.priceChangeChange}% change`
        });
      }
      
      // Low data freshness alert
      const dataAge = new Date() - new Date(newData.lastDataUpdate);
      if (dataAge > 5 * 60 * 1000) { // 5 minutes
        newAlerts.push({
          id: 'stale-data',
          type: 'warning',
          message: 'Data may be stale - last update over 5 minutes ago'
        });
      }
    }
    
    setAlerts(newAlerts);
  };

  const generateReport = async () => {
    setReportLoading(true);
    setReportStatus('Generating analytics report...');
    
    try {
      const response = await axios.post('/api/generate-report');
      setReportStatus('Report generated successfully!');
      
      // Auto-download the report
      if (response.data.reportUrl) {
        window.open(response.data.reportUrl, '_blank');
      }
      
      setTimeout(() => setReportStatus(''), 3000);
    } catch (error) {
      console.error('Failed to generate report:', error);
      setReportStatus('Failed to generate report. Please try again.');
      setTimeout(() => setReportStatus(''), 3000);
    } finally {
      setReportLoading(false);
    }
  };

  const refreshData = () => {
    setData(prev => ({ ...prev, loading: true }));
    fetchDashboardData();
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num?.toLocaleString() || '0';
  };

  const getTimeAgo = (date) => {
    if (!date) return 'Never';
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const executeApiRequest = async () => {
    setApiRequest(prev => ({ ...prev, loading: true, error: null, response: '' }));
    
    try {
      const config = {
        method: apiRequest.method,
        url: apiRequest.endpoint,
        headers: {
          'Content-Type': 'application/json',
        },
      };
      
      if ((apiRequest.method === 'POST' || apiRequest.method === 'PUT') && apiRequest.body) {
        try {
          config.data = JSON.parse(apiRequest.body);
        } catch (e) {
          throw new Error('Invalid JSON in request body');
        }
      }
      
      const response = await axios(config);
      setApiRequest(prev => ({ 
        ...prev, 
        response: JSON.stringify(response.data, null, 2),
        loading: false 
      }));
    } catch (error) {
      setApiRequest(prev => ({ 
        ...prev, 
        error: error.response?.data?.error || error.message || 'Request failed',
        response: error.response ? JSON.stringify(error.response.data, null, 2) : '',
        loading: false 
      }));
    }
  };

  const MetricCard = ({ title, value, change, icon: Icon, trend, subtitle, comparison, sparklineData }) => (
    <div className="metric-card">
      <div className="metric-header">
        <div>
          <span className="metric-title">{title}</span>
          {subtitle && <div className="metric-subtitle">{subtitle}</div>}
        </div>
        <div className="metric-icon">
          <Icon size={24} color="#667eea" />
        </div>
      </div>
      <div className="metric-value">{formatNumber(value)}</div>
      <div className="metric-details">
        {change !== undefined && (
          <div className={`metric-change ${trend}`}>
            {trend === 'positive' ? <TrendingUp size={16} /> : 
             trend === 'negative' ? <TrendingDown size={16} /> : 
             <Activity size={16} />}
            {change > 0 ? '+' : ''}{change}%
          </div>
        )}
        {comparison && (
          <div className="metric-comparison">
            vs {comparison.period}: {comparison.value > 0 ? '+' : ''}{comparison.value}%
          </div>
        )}
      </div>
      {sparklineData && sparklineData.length > 0 && (
        <div className="metric-sparkline">
          <ResponsiveContainer width="100%" height={40}>
            <LineChart data={sparklineData}>
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#667eea" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );

  const AdvancedChart = ({ title, data, type = 'line', height = 300, colors = COLORS }) => {
    const renderChart = () => {
      switch (type) {
        case 'area':
          return (
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="value" stroke={colors[0]} fill={colors[0]} fillOpacity={0.6} />
            </AreaChart>
          );
        case 'bar':
          return (
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill={colors[0]} />
            </BarChart>
          );
        case 'composed':
          return (
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="volume" fill={colors[0]} name="Volume" />
              <Line yAxisId="right" type="monotone" dataKey="price" stroke={colors[1]} name="Avg Price" />
            </ComposedChart>
          );
        case 'radial':
          return (
            <RadialBarChart cx="50%" cy="50%" innerRadius="10%" outerRadius="80%" data={data}>
              <RadialBar dataKey="value" cornerRadius={10} fill={colors[0]} />
              <Tooltip />
            </RadialBarChart>
          );
        default:
          return (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke={colors[0]} strokeWidth={2} />
            </LineChart>
          );
      }
    };

    return (
      <div className="chart-card advanced-chart">
        <div className="chart-header">
          <h3 className="chart-title">{title}</h3>
          <div className="chart-controls">
            <button className="chart-control-btn" title="View Details">
              <Eye size={16} />
            </button>
            <button className="chart-control-btn" title="Export">
              <Download size={16} />
            </button>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={height}>
          {renderChart()}
        </ResponsiveContainer>
      </div>
    );
  };

  const AlertBanner = () => {
    if (!settings.showAlerts || alerts.length === 0) return null;
    
    return (
      <div className="alerts-banner">
        {alerts.map(alert => (
          <div key={alert.id} className={`alert alert-${alert.type}`}>
            <div className="alert-content">
              <Bell size={16} />
              <span>{alert.message}</span>
            </div>
            <button 
              className="alert-close"
              onClick={() => setAlerts(alerts.filter(a => a.id !== alert.id))}
            >
              ×
            </button>
          </div>
        ))}
      </div>
    );
  };

  const TabNavigation = () => (
    <div className="tab-navigation">
      <button 
        className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
        onClick={() => setActiveTab('overview')}
      >
        <BarChart3 size={18} />
        Overview
      </button>
      <button 
        className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
        onClick={() => setActiveTab('analytics')}
      >
        <LineChartIcon size={18} />
        Analytics
      </button>
      <button 
        className={`tab-btn ${activeTab === 'collections' ? 'active' : ''}`}
        onClick={() => setActiveTab('collections')}
      >
        <PieChartIcon size={18} />
        Collections
      </button>
      <button 
        className={`tab-btn ${activeTab === 'trends' ? 'active' : ''}`}
        onClick={() => setActiveTab('trends')}
      >
        <TrendingUp size={18} />
        Trends
      </button>
      <button 
        className={`tab-btn ${activeTab === 'api' ? 'active' : ''}`}
        onClick={() => setActiveTab('api')}
      >
        <Settings size={18} />
        API
      </button>
    </div>
  );

  const ControlPanel = () => (
    <div className="control-panel">
      <div className="search-box">
        <Search size={16} />
        <input
          type="text"
          placeholder="Search collections, items..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      <div className="filters">
        <select 
          value={filters.timeframe} 
          onChange={(e) => setFilters({...filters, timeframe: e.target.value})}
        >
          <option value="1h">Last Hour</option>
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
        </select>
        
        <select 
          value={filters.priceRange} 
          onChange={(e) => setFilters({...filters, priceRange: e.target.value})}
        >
          <option value="all">All Prices</option>
          <option value="0-10">$0 - $10</option>
          <option value="10-50">$10 - $50</option>
          <option value="50-100">$50 - $100</option>
          <option value="100+">$100+</option>
        </select>
      </div>
      
      <button 
        className="settings-btn"
        onClick={() => setSettings({...settings, showAlerts: !settings.showAlerts})}
        title="Toggle Alerts"
      >
        <Bell size={16} className={settings.showAlerts ? 'active' : ''} />
      </button>
      
      <button 
        className="settings-btn"
        onClick={() => setSettings({...settings, autoRefresh: !settings.autoRefresh})}
        title="Toggle Auto Refresh"
      >
        <RefreshCw size={16} className={settings.autoRefresh ? 'active spinning' : ''} />
      </button>
    </div>
  );

  if (data.loading && !data.metrics) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1 className="dashboard-title">BitBot Analytics Dashboard</h1>
          <p className="dashboard-subtitle">Real-time BitSkins market data visualization</p>
        </div>
        <div className="loading">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="dashboard-title">BitBot Analytics Dashboard</h1>
            <p className="dashboard-subtitle">Real-time BitSkins market data visualization & analytics</p>
          </div>
          <div className="header-right">
            <div className="status-indicator">
              <div className={`status-dot ${data.error ? 'offline' : 'online'}`}></div>
              {data.error ? 'Offline' : 'Live'}
              {data.lastUpdated && (
                <span className="data-freshness">
                  Updated: {getTimeAgo(data.lastUpdated)}
                </span>
              )}
            </div>
          </div>
        </div>
        
        <TabNavigation />
        <ControlPanel />
      </div>

      <div className="dashboard-content">
        <AlertBanner />

        {data.error && (
          <div className="error">
            <AlertCircle size={16} style={{ marginRight: '0.5rem' }} />
            {data.error}
          </div>
        )}

        {reportStatus && (
          <div className={reportStatus.includes('Failed') ? 'error' : 'success'}>
            {reportStatus.includes('Failed') ? 
              <AlertCircle size={16} style={{ marginRight: '0.5rem' }} /> :
              <CheckCircle size={16} style={{ marginRight: '0.5rem' }} />
            }
            {reportStatus}
          </div>
        )}

        {/* Enhanced Key Metrics */}
        <div className="metrics-grid">
          <MetricCard
            title="Total Listed Items"
            subtitle="Active marketplace listings"
            value={data.metrics?.totalListed || 0}
            change={data.metrics?.listedChange || 0}
            trend={data.metrics?.listedChange > 0 ? 'positive' : data.metrics?.listedChange < 0 ? 'negative' : 'neutral'}
            icon={ShoppingCart}
            comparison={{ period: 'yesterday', value: data.metrics?.listedChange || 0 }}
            sparklineData={data.charts?.listingSparkline || []}
          />
          <MetricCard
            title="Price Changes"
            subtitle="Market price movements"
            value={data.metrics?.totalPriceChanges || 0}
            change={data.metrics?.priceChangeChange || 0}
            trend={data.metrics?.priceChangeChange > 0 ? 'positive' : data.metrics?.priceChangeChange < 0 ? 'negative' : 'neutral'}
            icon={DollarSign}
            comparison={{ period: 'yesterday', value: data.metrics?.priceChangeChange || 0 }}
            sparklineData={data.charts?.priceSparkline || []}
          />
          <MetricCard
            title="Market Velocity"
            subtitle="Items sold/delisted"
            value={data.metrics?.totalDelisted || 0}
            change={data.metrics?.delistedChange || 0}
            trend={data.metrics?.delistedChange > 0 ? 'positive' : data.metrics?.delistedChange < 0 ? 'negative' : 'neutral'}
            icon={Zap}
            comparison={{ period: 'yesterday', value: data.metrics?.delistedChange || 0 }}
            sparklineData={data.charts?.velocitySparkline || []}
          />
          <MetricCard
            title="Active Collections"
            subtitle="Collections with activity"
            value={data.metrics?.activeCollections || 0}
            change={data.metrics?.collectionsChange || 0}
            trend={data.metrics?.collectionsChange > 0 ? 'positive' : data.metrics?.collectionsChange < 0 ? 'negative' : 'neutral'}
            icon={Target}
            comparison={{ period: 'yesterday', value: data.metrics?.collectionsChange || 0 }}
          />
          <MetricCard
            title="Database Records"
            subtitle="Total data points collected"
            value={data.metrics?.totalRecords || 0}
            change={data.metrics?.recordsChange || 0}
            trend={data.metrics?.recordsChange > 0 ? 'positive' : data.metrics?.recordsChange < 0 ? 'negative' : 'neutral'}
            icon={Database}
            comparison={{ period: 'yesterday', value: data.metrics?.recordsChange || 0 }}
          />
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="tab-content">
            <div className="charts-grid">
              {/* Real-time Activity Feed */}
              <div className="chart-card featured">
                <h3 className="chart-title">
                  <Activity size={20} />
                  Real-time Market Activity
                </h3>
                <ResponsiveContainer width="100%" height={350}>
                  <ComposedChart data={data.charts?.timeline || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Area 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="listed" 
                      fill="#667eea" 
                      fillOpacity={0.6}
                      name="Listed Items"
                    />
                    <Bar yAxisId="left" dataKey="delisted" fill="#f093fb" name="Delisted/Sold" />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="priceChanges" 
                      stroke="#764ba2" 
                      strokeWidth={3}
                      name="Price Changes"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>

              {/* Enhanced Price Distribution */}
              <div className="chart-card">
                <h3 className="chart-title">
                  <BarChart3 size={20} />
                  Price Distribution Analysis
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.charts?.priceDistribution || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="range" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#667eea" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="tab-content">
            <div className="charts-grid">
              <AdvancedChart
                title="Market Volatility Index"
                data={data.charts?.volatility || []}
                type="area"
                colors={CHART_THEMES.purple}
              />
              
              <AdvancedChart
                title="Volume vs Price Correlation"
                data={data.charts?.correlation || []}
                type="composed"
                colors={CHART_THEMES.blue}
              />
              
              <AdvancedChart
                title="Market Efficiency Score"
                data={data.charts?.efficiency || []}
                type="radial"
                height={250}
                colors={CHART_THEMES.green}
              />
            </div>
          </div>
        )}

        {activeTab === 'collections' && (
          <div className="tab-content">
            <div className="charts-grid">
              {/* Enhanced Collections Chart */}
              <div className="chart-card featured">
                <h3 className="chart-title">
                  <Target size={20} />
                  Top Collections by Activity
                </h3>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={data.charts?.collections || []}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {(data.charts?.collections || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-card">
                <h3 className="chart-title">Collection Performance</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.charts?.collections || []} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={100} />
                    <Tooltip />
                    <Bar dataKey="value" fill="#667eea" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="tab-content">
            <div className="charts-grid">
              <AdvancedChart
                title="Trading Volume Trends"
                data={data.charts?.volume || []}
                type="area"
                colors={CHART_THEMES.pink}
              />
              
              <div className="chart-card">
                <h3 className="chart-title">
                  <TrendingUp size={20} />
                  Price Movement Heatmap
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart data={data.charts?.scatter || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="x" name="Price" />
                    <YAxis dataKey="y" name="Volume" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter dataKey="y" fill="#667eea" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'api' && (
          <div className="tab-content">
            <div className="api-testing-panel">
              <h3 className="section-title">
                <Settings size={20} />
                Custom API Requests
              </h3>
              
              <div className="api-request-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>Method</label>
                    <select 
                      value={apiRequest.method}
                      onChange={(e) => setApiRequest(prev => ({ ...prev, method: e.target.value }))}
                    >
                      <option value="GET">GET</option>
                      <option value="POST">POST</option>
                      <option value="PUT">PUT</option>
                      <option value="DELETE">DELETE</option>
                    </select>
                  </div>
                  <div className="form-group endpoint-group">
                    <label>Endpoint</label>
                    <input
                      type="text"
                      value={apiRequest.endpoint}
                      onChange={(e) => setApiRequest(prev => ({ ...prev, endpoint: e.target.value }))}
                      placeholder="/api/dashboard"
                    />
                  </div>
                </div>
                
                {(apiRequest.method === 'POST' || apiRequest.method === 'PUT') && (
                  <div className="form-group">
                    <label>Request Body (JSON)</label>
                    <textarea
                      value={apiRequest.body}
                      onChange={(e) => setApiRequest(prev => ({ ...prev, body: e.target.value }))}
                      placeholder='{"key": "value"}'
                      rows={4}
                    />
                  </div>
                )}
                
                <button 
                  className="api-submit-btn"
                  onClick={executeApiRequest}
                  disabled={apiRequest.loading}
                >
                  {apiRequest.loading ? <RefreshCw size={16} className="spinning" /> : <Settings size={16} />}
                  Execute Request
                </button>
              </div>
              
              <div className="api-response-section">
                <h4>Response</h4>
                {apiRequest.error && (
                  <div className="api-error">
                    <AlertCircle size={16} />
                    {apiRequest.error}
                  </div>
                )}
                <pre className="api-response">
                  {apiRequest.response || 'No response yet...'}
                </pre>
              </div>
              
              <div className="api-endpoints-reference">
                <h4>Available Endpoints</h4>
                <div className="endpoints-list">
                  <div className="endpoint-item">
                    <span className="method get">GET</span>
                    <code>/api/dashboard</code>
                    <span className="description">Main dashboard data</span>
                  </div>
                  <div className="endpoint-item">
                    <span className="method get">GET</span>
                    <code>/api/advanced-analytics</code>
                    <span className="description">Advanced analytics data</span>
                  </div>
                  <div className="endpoint-item">
                    <span className="method get">GET</span>
                    <code>/api/debug</code>
                    <span className="description">Debug information</span>
                  </div>
                  <div className="endpoint-item">
                    <span className="method get">GET</span>
                    <code>/api/health</code>
                    <span className="description">API health check</span>
                  </div>
                  <div className="endpoint-item">
                    <span className="method post">POST</span>
                    <code>/api/generate-report</code>
                    <span className="description">Generate analytics report</span>
                  </div>
                  <div className="endpoint-item">
                    <span className="method get">GET</span>
                    <code>/api/export-data</code>
                    <span className="description">Export raw data as JSON</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Actions Section */}
        <div className="actions-section">
          <h3 className="actions-title">
            <Settings size={20} />
            Dashboard Actions
          </h3>
          <div className="actions-grid">
            <button 
              className="action-button primary"
              onClick={refreshData}
              disabled={data.loading}
            >
              <RefreshCw size={20} className={data.loading ? 'spinning' : ''} />
              Refresh Data
            </button>
            
            <button 
              className="action-button secondary"
              onClick={generateReport}
              disabled={reportLoading}
            >
              {reportLoading ? (
                <>
                  <div className="loading-spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
                  Generating...
                </>
              ) : (
                <>
                  <FileText size={20} />
                  Generate Report
                </>
              )}
            </button>
            
            <button 
              className="action-button secondary"
              onClick={() => window.open('/api/export-data', '_blank')}
            >
              <Download size={20} />
              Export Data
            </button>

            <button 
              className="action-button tertiary"
              onClick={() => setSettings({...settings, autoRefresh: !settings.autoRefresh})}
            >
              <Bell size={20} />
              {settings.autoRefresh ? 'Disable' : 'Enable'} Auto-refresh
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
