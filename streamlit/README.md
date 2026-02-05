# AQI Predictor - Streamlit Dashboard

Interactive web dashboard for Air Quality Index prediction and monitoring in Hyderabad, Sindh.

## Features

### 📊 Real-Time Monitoring
- **Current AQI Display**: Large gauge chart showing current air quality
- **Color-Coded Categories**: 6 AQI categories (Good to Hazardous)
- **Health Recommendations**: Personalized advice based on current AQI
- **Last Updated Timestamp**: Know when data was last refreshed

### 🔮 3-Day Forecast
- **Prediction Cards**: Visual cards for each day's forecast
- **Forecast Chart**: Interactive bar chart showing AQI trends
- **Category Indicators**: Emoji and color-coded predictions
- **Date Display**: Clear date labels for each forecast day

### ⚠️ Alert System
- **Hazardous Level Alerts**: Prominent warnings when AQI ≥ 200
- **Alert Details**: Expandable section with specific alert days
- **Health Impact**: Clear messaging about health risks

### 📈 Historical Analysis
- **Trend Charts**: Interactive line charts showing AQI history
- **Customizable Range**: Select 1-30 days of historical data
- **Threshold Lines**: Visual indicators for AQI category boundaries
- **Statistics**: Average, max, min, and 24-hour trend metrics

### 🧪 Pollutant Breakdown
- **Current Levels**: Horizontal bar chart of all pollutants
- **5 Pollutants Tracked**: PM2.5, PM10, O3, NO2, CO
- **Concentration Values**: Detailed measurements in µg/m³
- **Color-Coded Display**: Different colors for each pollutant

### 📊 Statistical Analysis
- **Descriptive Statistics**: Mean, std, min, max, quartiles
- **Distribution Charts**: Histogram showing AQI frequency
- **Data Tables**: Comprehensive statistical summaries

### 📥 Data Export
- **CSV Download**: Export historical data to CSV format
- **Timestamp Preservation**: All data with accurate timestamps
- **Complete Dataset**: All pollutants and AQI values included

### ⚙️ Settings & Info
- **Refresh Button**: Manual data refresh on demand
- **Date Range Selector**: Choose historical data range (1-30 days)
- **Active Model Info**: Current model name, version, and performance
- **About Section**: Data sources and update frequency information

## Installation

### Prerequisites
```bash
# Python 3.9+
# MongoDB connection configured
# Environment variables set (MONGODB_URI, etc.)
```

### Install Dependencies
```bash
pip install streamlit plotly pandas numpy
```

Or use the project requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Run Locally
```bash
cd "d:/Internships and Jobs Data/10 Pearls Shine Internship/Project/AQI Predictor"
streamlit run streamlit/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Run with Custom Port
```bash
streamlit run streamlit/app.py --server.port 8080
```

### Run in Headless Mode (Server)
```bash
streamlit run streamlit/app.py --server.headless true
```

## Configuration

### Environment Variables
Ensure these are set before running:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=aqi_feature_store
OPENWEATHER_API_KEY=your_api_key_here
```

### Streamlit Configuration
Create `.streamlit/config.toml` for custom settings:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200
```

## Dashboard Layout

### Sidebar
- **Refresh Data**: Clear cache and reload all data
- **Date Range Selector**: Choose 1-30 days of historical data
- **Active Model Info**: 
  - Model name (XGBoost/LightGBM/RandomForest/LinearRegression)
  - Version (v1, v2, v3...)
  - Performance metrics (RMSE, R²)
  - Last update timestamp
- **About Section**: Data sources and update information

### Main Content

#### 1. Current Air Quality
- **Left Column**: 
  - Large AQI number with emoji indicator
  - Category name (Good/Moderate/etc.)
  - Timestamp of measurement
  - Health recommendation message
- **Right Column**: 
  - Gauge chart (0-500 range)
  - Color-coded segments for each AQI category
  - Threshold indicator at 200 (unhealthy level)

#### 2. Alert Banner
- Appears only when AQI ≥ 200 detected in forecasts
- Red error banner with warning icon
- Expandable details showing which days have alerts
- Specific AQI values and categories for alert days

#### 3. 3-Day Forecast
- **Forecast Cards**: 
  - Day label (Day 1, Day 2, Day 3)
  - Date (YYYY-MM-DD format)
  - AQI value with emoji
  - Category name
  - Color-coded background matching AQI category
- **Forecast Chart**: 
  - Bar chart with date on x-axis
  - AQI value on y-axis
  - Color-coded bars
  - Value labels on top of bars
  - Hover tooltips with details

#### 4. Tabbed Views

**Tab 1: Historical Trends**
- Line chart showing AQI over selected time period
- Dashed horizontal lines for category thresholds
- Annotations for threshold names (Good, Moderate, etc.)
- Hover tooltips showing exact timestamp and AQI
- 4 metric cards: Average, Max, Min, 24h Trend

**Tab 2: Pollutant Breakdown**
- Horizontal bar chart of current pollutant levels
- 5 pollutants with different colors
- Value labels outside bars
- Data table below with exact concentrations in µg/m³

**Tab 3: Statistics**
- Descriptive statistics table (describe())
- Histogram showing AQI distribution
- Frequency analysis across AQI ranges

**Tab 4: Download Data**
- Download button for CSV export
- Dataset information (number of records)
- Filename includes current date

#### 5. Footer
- Copyright notice
- Data update frequency information

## Features Explained

### Caching Strategy
```python
@st.cache_resource  # For database connections and predictors
@st.cache_data(ttl=3600)  # For data queries (1 hour cache)
```
- Database connections cached indefinitely
- Data queries cached for 1 hour (3600 seconds)
- Manual refresh clears all caches

### Color Coding
- **Green (#00e400)**: Good (0-50)
- **Yellow (#ffff00)**: Moderate (51-100)
- **Orange (#ff7e00)**: Unhealthy for Sensitive (101-150)
- **Red (#ff0000)**: Unhealthy (151-200)
- **Purple (#8f3f97)**: Very Unhealthy (201-300)
- **Maroon (#7e0023)**: Hazardous (301+)

### Responsive Design
- Wide layout for desktop viewing
- Columns adjust automatically
- Charts scale to container width
- Mobile-friendly with proper spacing

## Troubleshooting

### Dashboard Won't Start
```bash
# Check Streamlit installation
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

### Connection Errors
```bash
# Verify MongoDB connection
python -c "from src.data.mongodb_handler import MongoDBHandler; db = MongoDBHandler(); print('Connected!')"

# Check environment variables
echo $MONGODB_URI
```

### No Data Displayed
- Ensure `historical_features` collection has data
- Run data collection scripts first
- Check MongoDB connection in sidebar

### Cache Issues
- Click "Refresh Data" button in sidebar
- Or restart Streamlit server

### Import Errors
```bash
# Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/AQI Predictor"

# Or set in script (already included in app.py)
sys.path.insert(0, str(project_root))
```

## Performance Optimization

### Tips for Faster Loading
1. **Reduce Data Range**: Start with 7 days, increase if needed
2. **Use Caching**: Don't clear cache unnecessarily
3. **Limit Database Queries**: Cache is set to 1 hour by default
4. **Optimize Plots**: Charts are already optimized for performance

### Memory Usage
- Typical usage: 200-500 MB
- Large datasets (30 days): Up to 1 GB
- Consider limiting historical data range for production

## Deployment Options

### 1. Streamlit Cloud (Recommended)
1. Push code to GitHub repository
2. Connect Streamlit Cloud to your repo
3. Add secrets in dashboard settings
4. Deploy automatically on push

### 2. Local Server
```bash
# Run with systemd service
[Unit]
Description=AQI Predictor Dashboard
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/AQI Predictor
ExecStart=/usr/bin/streamlit run streamlit/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Docker Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "streamlit/app.py"]
```

### 4. Cloud Platforms
- **Heroku**: Use Procfile with `web: streamlit run streamlit/app.py`
- **AWS**: Deploy on EC2 or ECS
- **Azure**: Use App Service or Container Instances
- **Google Cloud**: Deploy on Cloud Run or Compute Engine

## Security Considerations

### Production Deployment
1. **Environment Variables**: Never commit secrets
2. **HTTPS**: Enable SSL/TLS for production
3. **Authentication**: Add auth layer if needed
4. **CORS**: Configure properly in config.toml
5. **Rate Limiting**: Use reverse proxy (nginx) for protection

### Data Privacy
- No personal data collected
- Air quality data is public information
- Model predictions are anonymized
- No user tracking or cookies

## Customization

### Change Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B6B"  # Your brand color
backgroundColor = "#0E1117"  # Dark mode
```

### Modify Layouts
- Edit column ratios: `st.columns([1, 2])` → `st.columns([1, 3])`
- Add/remove tabs in `st.tabs()`
- Adjust chart heights in `fig.update_layout(height=400)`

### Add New Features
- Import additional modules in header
- Create new chart functions
- Add tabs for custom views
- Extend sidebar with more controls

## Support

For issues or questions:
1. Check MongoDB connection status
2. Verify all dependencies installed
3. Review logs in terminal
4. Check environment variables
5. Test prediction module separately

## Version History

- **v1.0.0** (2026-02-06): Initial release
  - Current AQI display with gauge chart
  - 3-day forecast with cards and chart
  - Historical trends with customizable range
  - Pollutant breakdown and statistics
  - Alert system for hazardous levels
  - Data export functionality
  - Model information display
  - Responsive design

## Future Enhancements

- [ ] Multiple location support
- [ ] Model comparison view
- [ ] Prediction accuracy tracking
- [ ] Email/SMS alert notifications
- [ ] Custom date range picker
- [ ] Mobile app version
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] API endpoint documentation
- [ ] User authentication

## License

Part of AQI Predictor project for 10 Pearls Shine Internship.
