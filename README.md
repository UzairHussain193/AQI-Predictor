# AQI Predictor Project

Air Quality Index (AQI) prediction system for Hyderabad, Sindh using machine learning and automated hourly data collection.

## 📁 Project Structure

```
AQI Predictor/
├── .env                        # Environment variables (not tracked)
├── .env.example                # Template for environment variables
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
│
├── .github/
│   └── workflows/
│       └── fetch_hourly_data.yml  # GitHub Actions for automation
│
├── notebooks/                  # Jupyter notebooks for analysis
│   ├── Model_Training.ipynb   # Model training & evaluation
│   └── Visualization.ipynb    # Data analysis & visualization
│
├── src/                        # Source code
│   ├── config.py              # Configuration management
│   ├── data/
│   │   ├── fetch_current.py   # Fetch current weather/pollution
│   │   ├── fetch_historical.py  # Fetch historical data
│   │   └── mongodb_handler.py   # MongoDB operations
│   ├── features/
│   │   └── engineering.py     # Feature engineering functions
│   ├── models/
│   │   ├── train.py           # Model training functions
│   │   ├── predict.py         # 3-day AQI prediction
│   │   └── model_registry.py  # MongoDB model storage
│   ├── pipelines/
│   │   ├── setup_historical.py  # One-time historical setup
│   │   ├── update_hourly.py     # Hourly automation script
│   │   └── retrain_model.py     # Automated daily retraining
│   └── utils/
│       └── retry.py           # Retry logic with exponential backoff
│
├── models/                     # Trained models storage
│   ├── xgboost_aqi_v1.pkl     # Best model
│   ├── scaler.pkl             # Feature scaler
│   ├── feature_names.pkl      # Selected features
│   └── model_metadata.pkl     # Training metadata
│
├── data/                       # Data storage (not tracked)
│   ├── raw/                   # Raw CSV files
│   └── processed/             # Processed features
│
├── logs/                       # Application logs (not tracked)
└── venv/                       # Virtual environment (not tracked)
```

## 🚀 Setup Instructions

### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd AQI-Predictor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   OPENWEATHER_API_KEY=your_openweather_api_key
   MONGODB_USERNAME=your_mongodb_username
   MONGODB_PASSWORD=your_mongodb_password
   MONGODB_CLUSTER=your_cluster.mongodb.net
   ```

### 3. Setup APIs

#### OpenWeather API
1. Visit: https://openweathermap.org/api
2. Sign up for free account
3. Get API key from dashboard
4. Free tier: 1,000 calls/day

#### MongoDB Atlas
1. Visit: https://www.mongodb.com/cloud/atlas
2. Create free cluster (M0)
3. Create database user
4. Whitelist IP (0.0.0.0/0 for testing)
5. Get connection string

## 📊 Data Sources

- **Current Weather**: OpenWeather API (real-time)
- **Air Pollution**: OpenWeather API (current + historical)
- **Historical Weather**: Open-Meteo Archive API (2024-2026)
- **Feature Store**: MongoDB Atlas

## 🔄 Usage

### One-Time Historical Setup

```bash
python src/pipelines/setup_historical.py
```

This will:
1. Fetch historical weather data (2024-2026)
2. Fetch historical pollution data
3. Merge datasets
4. Apply feature engineering
5. Upload to MongoDB Atlas

### Manual Hourly Update

```bash
python src/pipelines/update_hourly.py
```

This will:
1. Fetch current hour weather + pollution
2. Check for duplicates
3. Get last 24h for lag features
4. Apply feature engineering
5. Append to MongoDB

### Automated Updates

GitHub Actions runs `update_hourly.py` every hour automatically.

## 🎯 Features Engineered

- **Temporal**: year, month, day, hour, weekday, is_weekend, season, time_of_day
- **Lag Features**: 1h, 6h, 12h, 24h lags for AQI, PM2.5, PM10, CO, NO2
- **Rolling Statistics**: 6h, 12h, 24h windows (mean, std, min, max)
- **Change Rates**: Percentage change for pollutants and weather
- **Interactions**: temp×humidity, wind×PM2.5, wind×temp, humidity×PM2.5
- **Alerts**: High pollution, rain, high PM2.5, high temperature

**Total**: 100+ features per record

## 🔧 GitHub Actions Setup

### Repository Secrets

Add these secrets in GitHub repository settings:
- `OPENWEATHER_API_KEY`
- `MONGODB_USERNAME`
- `MONGODB_PASSWORD`
- `MONGODB_CLUSTER`

### Workflow Trigger

- **Automatic**: Every hour at minute 0
- **Manual**: Workflow dispatch button in Actions tab

## 📦 What to Upload to GitHub

✅ **Include:**
- All source code (`src/`)
- Notebooks (`notebooks/`)
- Workflows (`.github/workflows/`)
- Configuration files (`.env.example`, `requirements.txt`, `.gitignore`)
- Documentation (`README.md`)

❌ **Exclude (in .gitignore):**
- `.env` (real credentials)
- `data/` (CSV files)
- `venv/` (virtual environment)
- `logs/` (log files)
- `__pycache__/` (Python cache)

## 🛠️ Technologies

- **Python 3.9+**
- **pandas** - Data manipulation
- **requests** - API calls
- **pymongo** - MongoDB operations
- **openmeteo-requests** - Historical weather data
- **GitHub Actions** - Automation

## 📈 Next Steps

1. ✅ Data collection automation
2. ✅ Feature engineering
3. ✅ Feature store (MongoDB Atlas)
4. ✅ Model training (XGBoost, LightGBM, Random Forest, Linear Regression)
5. ✅ 3-Day AQI prediction system
6. ✅ Automated daily model retraining
7. ✅ SHAP analysis for model interpretability
8. ✅ Hazardous AQI alert system
9. 🔄 Streamlit dashboard (optional)

## 🤖 Model Training & Prediction

### Train Models

Run the Jupyter notebook:
```bash
jupyter notebook notebooks/Model_Training.ipynb
```

The notebook will:
- Load data from MongoDB feature store
- Select top 40 features by correlation
- Train 4 regression models (XGBoost, LightGBM, Random Forest, Linear Regression)
- Perform SHAP analysis for interpretability
- Evaluate models (RMSE, MAE, R²)
- Save best model locally and to MongoDB

### Make 3-Day Predictions

```bash
# Using MongoDB model (recommended)
python predict_aqi.py

# Using local model
python predict_aqi.py --local --model-dir models
```

**Output Example:**
```
======================================================================
📊 AQI 3-DAY FORECAST
======================================================================

Day 1 - 2026-02-07 (Friday)
  AQI:      87.34
  Category: Moderate
  Status:   🟡 Moderate

Day 2 - 2026-02-08 (Saturday)
  AQI:      92.18
  Category: Moderate
  Status:   🟡 Moderate

Day 3 - 2026-02-09 (Sunday)
  AQI:      156.45
  Category: Unhealthy for Sensitive Groups
  Status:   🟠 Unhealthy for Sensitive Groups

======================================================================
⚠️ ALERT: Unhealthy AQI levels predicted!
======================================================================
```

### Automated Daily Retraining

GitHub Actions workflow runs daily at 1:05 AM UTC:
- Fetches latest features from MongoDB
- Retrains all 4 models
- Selects best model
- Updates MongoDB model registry
- Sets new model as active

**Manual trigger**:
```bash
python src/pipelines/retrain_model.py
```

For more details, see [MODEL_TRAINING_GUIDE.md](MODEL_TRAINING_GUIDE.md)

## 📊 Model Performance

| Model | Test RMSE | Test MAE | Test R² |
|-------|-----------|----------|---------|
| XGBoost | ~12 | ~8 | ~0.92 |
| LightGBM | ~12 | ~8 | ~0.92 |
| Random Forest | ~14 | ~9 | ~0.90 |
| Linear Regression | ~17 | ~11 | ~0.87 |

**Key Features** (by SHAP importance):
1. PM2.5 lag features
2. PM10 lag features
3. PM2.5 rolling averages
4. Temperature
5. Humidity

## 👤 Author

**10 Pearls Shine Internship Project**
- Location: Hyderabad, Sindh, Pakistan
- Coordinates: 25.3960°N, 68.3578°E

## 📄 License

This project is for educational purposes.
- [ ] Automate feature pipeline (hourly)
- [ ] Automate training pipeline (daily)
- [ ] GitHub Actions setup

### Phase 6: Dashboard
- [ ] Streamlit/Gradio interface
- [ ] Real-time predictions
- [ ] Visualization

## 📦 Dependencies

Core libraries:
- `requests` - API calls
- `pandas` - Data manipulation
- `python-dotenv` - Environment management
- `numpy` - Numerical operations

## 🔥 Quick Start

```python
# Test API connection
from src.config import Config
import requests

response = requests.get(
    Config.AIR_POLLUTION_URL,
    params={
        'lat': Config.LATITUDE,
        'lon': Config.LONGITUDE,
        'appid': Config.OPENWEATHER_API_KEY
    }
)
print(response.json())
```

## 📝 Notes

- CSV files in `data/` are gitignored for privacy
- Always use `.env` for sensitive credentials
- API rate limit: 60 calls/minute (free tier)

## 🤝 Contributing

This is an internship project for 10 Pearls Shine Internship Program.
