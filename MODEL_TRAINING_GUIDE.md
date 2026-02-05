# AQI Prediction System - Model Training & Prediction Guide

## 📊 Overview

This system predicts Air Quality Index (AQI) **numbers** (regression, not classification) for the next 3 days using machine learning models trained on historical weather and pollution data.

## 🎯 Key Features

- **4 Regression Models**: XGBoost, LightGBM, Random Forest, Linear Regression
- **SHAP Analysis**: Model interpretability and feature importance
- **Automated Daily Retraining**: Updates model with latest data at 1:05 AM UTC
- **3-Day Predictions**: Forecast AQI values for next 3 days
- **Hazardous AQI Alerts**: Automatic warnings for unhealthy air quality
- **Dual Storage**: Models saved locally (.pkl) and in MongoDB registry

---

## 🔧 Setup & Installation

### Prerequisites
```bash
# Required packages (add to requirements.txt)
pandas
numpy
scikit-learn
xgboost
lightgbm
shap
joblib
pymongo
python-dotenv
```

### Environment Variables (.env)
```env
OPENWEATHER_API_KEY=your_api_key
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_CLUSTER=your_cluster_url
```

---

## 📚 Usage Guide

### 1. Train Models (Jupyter Notebook)

Open and run `notebooks/Model_Training.ipynb`:

```python
# The notebook covers:
# 1. Load data from MongoDB feature store
# 2. Feature selection (top 40 by correlation)
# 3. Train 4 regression models
# 4. SHAP analysis for interpretability
# 5. Evaluate models (RMSE, MAE, R²)
# 6. Save best model locally and to MongoDB
```

**Expected Output:**
- Trained models comparison table
- SHAP feature importance plots
- Best model saved to `models/` directory
- Model registered in MongoDB `model_registry` collection

---

### 2. Make 3-Day Predictions

#### Method A: Python Script
```python
from src.models.predict import AQIPredictor

# Initialize predictor (loads active model from MongoDB)
predictor = AQIPredictor(use_mongodb=True)

# Get 3-day forecast
predictions = predictor.predict_next_3_days()

# Check for hazardous alerts
alerts = predictor.check_hazardous_alert(predictions)

# Display results
for day, pred in predictions.items():
    print(f"{day} ({pred['date']}): AQI = {pred['aqi']} ({pred['category']})")

if alerts['has_alert']:
    print(f"\n⚠️ ALERT: {alerts['message']}")
```

#### Method B: Command Line
```bash
python src/models/predict.py
```

**Output Example:**
```
============================================================
📊 3-DAY AQI FORECAST
============================================================

Day 1 (2026-02-07):
  AQI: 87.34
  Category: Moderate

Day 2 (2026-02-08):
  AQI: 92.18
  Category: Moderate

Day 3 (2026-02-09):
  AQI: 156.45
  Category: Unhealthy for Sensitive Groups

============================================================
⚠️ ALERT: Unhealthy AQI levels predicted!
============================================================
```

---

### 3. Automated Daily Retraining

**GitHub Actions Workflow**: `.github/workflows/retrain_model.yml`

- **Schedule**: Daily at 1:05 AM UTC
- **Process**:
  1. Fetches latest features from MongoDB
  2. Trains 4 models on all available data
  3. Selects best model based on test RMSE
  4. Saves model locally and to MongoDB registry
  5. Sets new model as active

**Manual Trigger**:
```bash
# Run manually via GitHub UI: Actions > Automated Model Retraining > Run workflow
```

**Local Execution**:
```bash
python src/pipelines/retrain_model.py
```

---

## 📁 Project Structure

```
AQI Predictor/
├── notebooks/
│   └── Model_Training.ipynb          # Training notebook
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py                  # Model training functions
│   │   ├── model_registry.py         # MongoDB storage
│   │   └── predict.py                # 3-day prediction
│   └── pipelines/
│       └── retrain_model.py          # Automated retraining
├── models/                           # Local model storage
│   ├── xgboost_aqi_v1.pkl           # Trained model
│   ├── scaler.pkl                    # Feature scaler
│   ├── feature_names.pkl             # Selected features
│   └── model_metadata.pkl            # Training metadata
└── .github/
    └── workflows/
        └── retrain_model.yml         # Automated retraining workflow
```

---

## 🗄️ MongoDB Collections

### `model_registry`
Stores trained models with metadata:
```json
{
  "model_name": "XGBoost",
  "version": "v1",
  "model_binary": "<binary>",
  "scaler_binary": "<binary>",
  "feature_names": ["pm25", "pm10", ...],
  "n_features": 40,
  "performance": {
    "test_rmse": 12.34,
    "test_mae": 8.56,
    "test_r2": 0.92
  },
  "training_info": {
    "trained_at": "2026-02-06T10:00:00Z",
    "training_samples": 12000,
    "test_samples": 2500
  },
  "is_active": true
}
```

### `historical_features`
Feature store with engineered features:
- Temporal features (hour, day, month, weekday)
- Lag features (previous 1-24 hours)
- Rolling statistics (24h averages, std)
- Change rates (pollution deltas)
- Interaction features (temp×humidity, etc.)

---

## 📊 Model Performance

### Evaluation Metrics

- **RMSE** (Root Mean Squared Error): Lower is better
- **MAE** (Mean Absolute Error): Lower is better
- **R²** (R-squared): Higher is better (0-1 scale)

### Expected Performance
```
Model              Test RMSE    Test MAE    Test R²
XGBoost            10-15        7-10        0.90-0.95
LightGBM           10-15        7-10        0.90-0.95
RandomForest       12-17        8-11        0.88-0.93
LinearRegression   15-20        10-14       0.85-0.90
```

---

## 🔍 SHAP Analysis

SHAP (SHapley Additive exPlanations) provides:
- **Feature Importance**: Which features matter most
- **Feature Impact**: How features affect predictions
- **Model Interpretability**: Understand model decisions

**Top Features** (typical):
1. PM2.5 (lag features)
2. PM10 (lag features)
3. PM2.5 rolling averages
4. Temperature
5. Humidity

---

## ⚠️ AQI Categories & Alerts

| AQI Range | Category | Health Impact |
|-----------|----------|---------------|
| 0-50 | Good | ✅ Minimal impact |
| 51-100 | Moderate | 🟡 Acceptable quality |
| 101-150 | Unhealthy for Sensitive Groups | 🟠 Sensitive groups affected |
| 151-200 | Unhealthy | 🔴 Everyone affected |
| 201-300 | Very Unhealthy | 🟣 Serious health effects |
| 301+ | Hazardous | 🟤 Emergency conditions |

**Alert Thresholds**:
- **Warning**: AQI ≥ 200 (Unhealthy)
- **Severe**: AQI ≥ 300 (Very Unhealthy/Hazardous)

---

## 🔄 Prediction Workflow

```
┌─────────────────────────────────────────┐
│ 1. Fetch Latest 24h Features            │
│    (from MongoDB historical_features)    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. Create Future Feature Sets           │
│    (persistence model + temporal)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. Load Active Model from MongoDB       │
│    (model + scaler + feature names)      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 4. Scale Features                        │
│    (using fitted StandardScaler)         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 5. Make Predictions                      │
│    (Day 1, Day 2, Day 3)                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 6. Check Hazardous Alerts                │
│    (AQI ≥ 200 triggers warning)          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 7. Return Predictions + Alerts           │
└─────────────────────────────────────────┘
```

---

## 🧪 Testing

### Test Model Training
```bash
# Run notebook cells sequentially
jupyter notebook notebooks/Model_Training.ipynb
```

### Test Predictions
```bash
python src/models/predict.py
```

### Test Retraining
```bash
python src/pipelines/retrain_model.py
```

---

## 🐛 Troubleshooting

### Issue: No active model found
```
Solution: Train a model first using Model_Training.ipynb
```

### Issue: Prediction fails - no recent data
```
Solution: Ensure hourly data pipeline is running (fetch_hourly_data.yml)
```

### Issue: GitHub Actions workflow not running
```
Solution: 
1. Check repository secrets (MONGODB_*, OPENWEATHER_API_KEY)
2. Verify MongoDB Network Access (0.0.0.0/0)
3. Check workflow logs in Actions tab
```

---

## 🚀 Next Steps

1. ✅ **Model Training**: Run `Model_Training.ipynb`
2. ✅ **Test Predictions**: Run `python src/models/predict.py`
3. ✅ **Enable Automated Retraining**: Push `.github/workflows/retrain_model.yml`
4. 🔜 **Create Streamlit Dashboard**: Visualize predictions
5. 🔜 **Add Weather Forecast API**: Improve future predictions
6. 🔜 **Deploy Prediction Service**: REST API or web app

---

## 📞 Support

For issues or questions:
1. Check logs: `logs/` directory
2. Review MongoDB collections: `historical_features`, `model_registry`
3. Verify environment variables in `.env`
4. Check GitHub Actions logs for automation issues

---

## 📝 Notes

- **Persistence Model**: Current implementation uses simple persistence (last known values) for future pollutant predictions. Production systems should integrate weather forecast APIs.
- **Feature Selection**: Top 40 features selected by correlation. Can be adjusted in training code.
- **Retraining Frequency**: Daily at 1:05 AM UTC. Can be modified in workflow cron schedule.
- **Model Versioning**: Automatic version incrementation (v1, v2, v3...) on each retraining.

---

**Last Updated**: 2026-02-06
**Version**: 1.0
