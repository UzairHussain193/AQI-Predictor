# AQI Predictor - Hyderabad, Sindh

A production-ready Air Quality Index (AQI) prediction system using machine learning, automated data pipelines, and real-time forecasting for Hyderabad, Pakistan.

## 🌐 Live Application

<p><strong>Dashboard:</strong> 
<a href="https://hyd-aqi-predictor.streamlit.app/" target="_blank">
https://hyd-aqi-predictor.streamlit.app/
</a>
</p>


Features:
- Real-time AQI monitoring
- 3-day AQI forecasts with confidence intervals
- Model performance metrics
- Automated hourly updates

## 📊 Project Overview

**Duration**: February 2024 - February 2026 (24 months)  
**Data Collected**: 4,215+ hourly records  
**Model Accuracy**: 97.2% (R² score)  
**Best Model**: XGBoost (RMSE: 5.342)

This system automatically fetches air quality and weather data every hour, engineers 120+ features, trains ML models daily, and provides accurate 3-day AQI predictions through a web dashboard.

## 🏗️ System Architecture

**Data Pipeline**: API Fetch → Feature Engineering → MongoDB Storage  
**ML Pipeline**: Model Training → Registry → Deployment  
**Automation**: GitHub Actions (Hourly data fetch + Daily model retraining)  
**Frontend**: Streamlit dashboard with real-time predictions

**Key Components**:
- `src/data/` - Data fetching and MongoDB operations
- `src/features/` - Feature engineering (120+ features)
- `src/models/` - Model training, prediction, and registry
- `src/pipelines/` - Automation scripts
- `streamlit/` - Web dashboard
- `.github/workflows/` - CI/CD automation

## 📄 Technology Stack

**Data & Storage**:
- OpenWeather Air Pollution API (8 pollutants, hourly updates)
- Open-Meteo Weather API (15+ weather parameters)
- MongoDB Atlas (Feature store + Model registry)

**Machine Learning**:
- XGBoost (Active model, RMSE: 5.342, R²: 0.972)
- LightGBM, Random Forest (Alternative models)
- SHAP (Model interpretability)
- 120+ engineered features (lags, rolling stats, interactions)

**Deployment**:
- Streamlit Cloud (Dashboard hosting)
- GitHub Actions (Automation)
- Python 3.9+, pandas, pymongo, scikit-learn

## � Quick Start

### Local Setup

```bash
# 1. Clone and install
git clone <repository-url>
cd AQI-Predictor
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys and MongoDB credentials

# 3. Run dashboard locally
cd streamlit
streamlit run app.py
```

### Key Scripts

```bash
# Fetch current data and update MongoDB
python src/pipelines/update_hourly.py

# Retrain models with latest data
python src/pipelines/retrain_model.py

# Make 3-day AQI predictions
python predict_aqi.py
```

### Automation

**GitHub Actions** automatically runs:
- **Hourly**: Data fetch and feature engineering
- **Daily (2 AM UTC)**: Model retraining and registry update

## 🎯 Key Features

**Feature Engineering** (120+ features):
- Temporal: hour, weekday, season, time_of_day
- Lag features: 1h, 6h, 12h, 24h for all pollutants
- Rolling statistics: 6h, 12h, 24h windows (mean, std, min, max)
- Interactions: temp×humidity, wind×PM2.5, humidity×pollutants
- Change rates: Percentage changes for all parameters

**Model Performance**:
| Model | RMSE | MAE | R² |
|-------|------|-----|-----|
| XGBoost | 5.342 | 3.421 | 0.972 |
| LightGBM | 5.498 | 3.556 | 0.969 |
| Random Forest | 6.123 | 4.012 | 0.961 |

## 📄 Documentation

- **Technical Report**: [`report/HYD-AQI-Predictor-Report.pdf`](report/draft.txt) - Comprehensive project documentation
- **Notebooks**: 
  - `notebooks/Model_Training.ipynb` - Model development and evaluation
  - `notebooks/Visualization.ipynb` - EDA and SHAP analysis
- **API Documentation**: See inline docstrings in `src/` modules

## 🔑 Configuration

Required environment variables (`.env`):
```env
OPENWEATHER_API_KEY=your_key_here
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_CLUSTER=your_cluster.mongodb.net
```

GitHub repository secrets (for automation):
- `OPENWEATHER_API_KEY`
- `MONGODB_USERNAME`
- `MONGODB_PASSWORD`
- `MONGODB_CLUSTER`

## 📍 Project Details

**Location**: Hyderabad, Sindh, Pakistan (25.3960°N, 68.3578°E)  
**Duration**: December 2026 - February 2026  
**Context**: 10 Pearls Shine Internship Project

## 📄 License

This project is developed for educational purposes as part of the 10 Pearls Shine Internship Program.

## 📞 Contact

Uzair Hussain Shaikh | 
[GitHub](https://github.com/uzairhussain193) | 
[LinkedIn](https://linkedin.com/in/uzairhussain1)


