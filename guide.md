# AQI Prediction Project - Complete Step-by-Step Breakdown

## **Project Overview**
This is an Air Quality Index (AQI) prediction system for Karachi that:
- Fetches real-time weather and pollution data
- Engineers features from raw data
- Trains ML models to predict AQI for the next 3 days
- Automates data collection and model retraining
- Serves predictions via a Streamlit web app

---

## **Step-by-Step Flow**

### **PHASE 1: Initial Data Collection & Model Development** 
*(One-time setup - in base_code.ipynb)*

#### **Step 1: Historical Data Backfill**
- **Cell 2**: Fetches 1 year of historical AQI and weather data for Karachi
- APIs used:
  - OpenWeatherMap API (AQI & coordinates)
  - WeatherAPI (weather details)
- Collects hourly data: temperature, humidity, wind speed, precipitation, PM2.5, PM10, CO, NO2, O3, etc.
- Saves to `historical_aqi_and_weather_data.json`

#### **Step 2: Feature Engineering**
- **Cell 4**: Processes raw JSON data into structured features
- Creates time-based features: hour, day, month, year, weekday, season, time_of_day
- Lag features: previous hour's AQI and pollutants
- Rolling statistics: 24-hour rolling averages, std, min, max
- Change rates: pollution and weather variable deltas
- Interaction features: temp×humidity, wind×PM2.5
- Cumulative features: 24-hour cumulative precipitation and pollutants
- Binary alerts: high pollution flag, rain alert
- Polynomial features: temperature², humidity²
- Saves to `preprocessed_data.csv`

#### **Step 3: EDA & Feature Importance**
- **Cell 6**: Exploratory Data Analysis
- Visualizes AQI distribution, correlations, scatter plots
- Label encodes categorical variables (season, time_of_day)
- Fills missing values (mean for numeric, "Unknown" for categorical)
- Trains initial Random Forest to identify important features
- Top features: **PM10** (84.8%), **PM2.5** (11.9%), **O3** (3.3%)
- Saves to `processed_data.csv` and `feature_importances.csv`

#### **Step 4: Model Training & Selection**
- **Cell 8**: Trains multiple ML models:
  - Random Forest
  - Ridge Regression
  - XGBoost
  - LightGBM
  - TensorFlow Neural Network
- Compares performance (RMSE, MAE, R²)
- Selects best model (likely Random Forest based on feature importance)
- Retrains best model on entire dataset
- Saves to `model_registry/random_forest_retrained.pkl`

---

### **PHASE 2: Automated Production Pipeline**

#### **A. Hourly Feature Pipeline** 
*(.github/workflows/feature_pipeline.yml)* - Runs every hour

##### **Step 5: Fetch Current Data** (fetch_data.py)
- Gets Karachi's lat/lon coordinates
- Fetches current hour's AQI and weather data
- Saves to `current_hour_data.json`
- Handles API rate limits with retry logic

##### **Step 6: Compute Features** (compute_features.py)
- Extracts features from fetched JSON
- Creates same structure as training data:
  - timestamp, AQI, pollutants (CO, NO2, O3, PM2.5, PM10)
  - weather (temperature, humidity, wind_speed, precipitation)
- Saves to `computed_features.csv`

##### **Step 7: Update Feature Store** (feature_store.py)
- Reads `computed_features.csv`
- Appends new row to `processed_features.csv` (feature store)
- Creates file if doesn't exist
- Accumulates data over time for continuous learning

---

#### **B. Daily Training Pipeline** 
*(.github/workflows/model_train.yml)* - Runs at midnight

##### **Step 8: Retrain Model** (train_model.py)
- Loads entire feature store (`processed_data.csv`)
- Loads existing model from `model_registry/`
- Retrains model on all accumulated data (incremental learning)
- Overwrites model in registry with updated version
- Ensures model stays current with latest patterns

---

### **PHASE 3: Production Inference & User Interface**

#### **The Streamlit App** (app/main.py)

##### **Step 9: Load Model**
- Loads trained model from `model_registry/random_forest_retrained.pkl`

##### **Step 10: Fetch Forecast Features** (app/feature_engineering.py)
- `get_forecast_dataframe()` function:
  - Gets coordinates for Karachi
  - Fetches 3-day forecast from APIs
  - Preprocesses forecast data (same transformations as training)
  - Engineers all features (lag, rolling, interaction, etc.)
  - Returns DataFrame ready for prediction

##### **Step 11: Make Predictions** (app/model.py)
- `predict_aqi()` function:
  - Drops timestamp column
  - Ensures feature alignment with training
  - Runs model inference
  - Returns predictions with original features

##### **Step 12: Display Results**
- Shows predicted AQI for next 3 days
- Displays date, predicted_aqi, temperature, humidity, wind_speed
- Loads historical data (`processed_data.csv`)
- Shows AQI fluctuation chart for past 30 days
- Interactive Streamlit line chart

---

## **Key Components Explained**

### **Utility Files**

#### **app/utils.py**
- `fetch_coordinates()`: Gets Karachi's lat/lon
- `fetch_weather_forecast()`: 3-day weather forecast
- `extract_features_from_forecast()`: Parses forecast JSON
- `add_time_features()`: Adds hour/day/month features

#### **app/__init__.py**
- Empty init file (makes `app/` a Python package)

---

### **Deployment**

#### **Dockerfile**
- Base image: Python 3.9
- Installs requirements
- Sets PYTHONPATH to `/app`
- Exposes port 8501 (Streamlit default)
- Runs: `streamlit run app/main.py`

**To run locally:**
```bash
docker build -t aqi-predictor .
docker run -p 8501:8501 aqi-predictor
```

**To run without Docker:**
```bash
pip install -r requirements.txt
streamlit run app/main.py
```

---

## **Data Flow Summary**

```
[APIs] → fetch_data.py → current_hour_data.json
         ↓
     compute_features.py → computed_features.csv
         ↓
     feature_store.py → processed_features.csv (Feature Store)
         ↓
     train_model.py → model_registry/*.pkl (Updated Model)
         ↓
     [Streamlit App] → Predictions for Users
```

---

## **Automation Summary**

1. **Hourly** (GitHub Actions): Fetches data → Computes features → Updates feature store
2. **Daily** (GitHub Actions): Retrains model on accumulated data
3. **On-Demand** (Streamlit): User visits app → Fetches 3-day forecast → Predicts AQI

---

## **Feature Engineering Details**

### **Time-Based Features**
- `year`, `month`, `day`, `hour`, `weekday`
- `season` (winter/spring/summer/fall)
- `is_weekend` (binary: 0/1)
- `time_of_day` (morning/afternoon/evening/night)

### **Lag Features**
- `aqi_lag_1`: Previous hour's AQI
- `co_lag_1`, `no2_lag_1`, `pm2_5_lag_1`, `pm10_lag_1`: Previous hour's pollutants

### **Rolling Statistics (24-hour window)**
- AQI: rolling std, min, max
- Pollutants: rolling avg, std

### **Change Rates (Delta)**
- Pollutants: CO, NO2, PM2.5, PM10
- Weather: temperature, humidity, wind_speed

### **Interaction Features**
- `temp_humidity_interaction`: temperature × humidity
- `wind_pm2_5_interaction`: wind_speed × PM2.5

### **Cumulative Features (24-hour window)**
- `cumulative_precipitation`
- `cumulative_co`, `cumulative_no2`, `cumulative_pm2_5`, `cumulative_pm10`

### **Binary Alerts**
- `high_pollution_alert`: 1 if AQI > 150, else 0
- `rain_alert`: 1 if precipitation > 0, else 0

### **Polynomial Features**
- `temperature_squared`: temperature²
- `humidity_squared`: humidity²

---

## **API Configuration**

### **OpenWeatherMap API**
- **Purpose**: AQI data and geocoding
- **Endpoints**:
  - Geocoding: `http://api.openweathermap.org/geo/1.0/direct`
  - Historical AQI: `http://api.openweathermap.org/data/2.5/air_pollution/history`
  - Forecast AQI: `http://api.openweathermap.org/data/2.5/air_pollution/forecast`
- **API Key**: `6f5bd489ac2182623da65e8c0210a0d3`

### **WeatherAPI**
- **Purpose**: Weather data and forecasts
- **Endpoints**:
  - Historical: `http://api.weatherapi.com/v1/history.json`
  - Forecast: `http://api.weatherapi.com/v1/forecast.json`
- **API Key**: `a8b5181c2df94da6943114229252201`

---

## **Tech Stack**

### **Machine Learning**
- scikit-learn (Random Forest, Ridge Regression)
- XGBoost
- LightGBM
- TensorFlow/Keras

### **Data Processing**
- pandas
- numpy

### **Visualization**
- matplotlib
- seaborn
- plotly

### **Web Application**
- Streamlit

### **Deployment**
- Docker
- GitHub Actions (CI/CD)

### **Model Persistence**
- joblib (pickle format)

---

## **File Structure**

```
10pearls_Aqi-main/
├── .github/
│   └── workflows/
│       ├── feature_pipeline.yml    # Hourly data collection
│       └── model_train.yml         # Daily model retraining
├── app/
│   ├── __init__.py
│   ├── feature_engineering.py      # Forecast feature engineering
│   ├── main.py                     # Streamlit app
│   ├── model.py                    # Model loading & prediction
│   └── utils.py                    # Utility functions
├── model_registry/
│   ├── random_forest_retrained.pkl # Trained Random Forest model
│   └── ridge_regression_retrained.pkl
├── base_code.ipynb                 # Initial development notebook
├── compute_features.py             # Feature computation script
├── Dockerfile                      # Container configuration
├── feature_importances.csv         # Feature importance results
├── feature_store.py                # Feature store update script
├── fetch_data.py                   # Data fetching script
├── preprocessed_data.csv           # Preprocessed historical data
├── processed_data.csv              # Final processed data for training
├── README.md
├── requirements.txt                # Python dependencies
└── train_model.py                  # Model retraining script
```

---

## **Model Performance Metrics**

The project evaluates models using:
- **RMSE** (Root Mean Squared Error): Lower is better
- **MAE** (Mean Absolute Error): Average prediction error
- **R²** (R-squared): Coefficient of determination (closer to 1 is better)

Based on feature importance analysis:
- **PM10**: 84.8% importance (most critical)
- **PM2.5**: 11.9% importance
- **O3**: 3.3% importance
- Other features: < 1% each

---

## **Current State**

✅ Historical data collected (1 year)  
✅ Features engineered (50+ features)  
✅ Models trained (Random Forest selected)  
✅ Workflows configured (hourly/daily)  
✅ Streamlit app built  
✅ Docker setup complete  
✅ Model registry contains 2 trained models  

---

## **How to Run the Project**

### **1. Run Streamlit App Locally**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app/main.py
```

### **2. Run with Docker**
```bash
# Build the image
docker build -t aqi-predictor .

# Run the container
docker run -p 8501:8501 aqi-predictor

# Access at http://localhost:8501
```

### **3. Manual Data Pipeline Execution**
```bash
# Fetch current data
python fetch_data.py

# Compute features
python compute_features.py

# Update feature store
python feature_store.py

# Retrain model
python train_model.py
```

### **4. Run Initial Setup (Jupyter Notebook)**
```bash
# Open the notebook
jupyter notebook base_code.ipynb

# Execute cells in order:
# 1. Historical data collection (Cell 2)
# 2. Feature engineering (Cell 4)
# 3. EDA & feature importance (Cell 6)
# 4. Model training & selection (Cell 8)
```

---

## **Future Improvements**

### **Potential Enhancements**
1. **Model Monitoring**: Add drift detection and performance tracking
2. **A/B Testing**: Compare multiple models in production
3. **Real-time Alerts**: Notify users when AQI exceeds thresholds
4. **Multi-city Support**: Extend beyond Karachi
5. **Advanced Features**: Add satellite imagery, traffic data
6. **Model Explainability**: Integrate SHAP or LIME
7. **Cloud Deployment**: Move to AWS/GCP/Azure
8. **Database Integration**: Replace CSV with proper database
9. **API Development**: Create REST API for predictions
10. **Mobile App**: Build mobile interface

---

## **Troubleshooting**

### **Common Issues**

**API Rate Limits**
- Both scripts include retry logic with exponential backoff
- Default retry: 60 seconds

**Missing Data**
- Numeric columns: Filled with mean
- Categorical columns: Filled with "Unknown"

**Model Loading Errors**
- Ensure model exists in `model_registry/`
- Check scikit-learn version compatibility

**Feature Mismatch**
- Ensure training and inference use same feature engineering pipeline
- Timestamp column is dropped before prediction

---

## **License**
Not specified in project files.

---

## **Contributors**
10 Pearls Shine Internship Project

---

**Last Updated**: February 5, 2026
