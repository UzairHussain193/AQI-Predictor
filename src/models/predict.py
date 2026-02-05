"""
AQI Prediction Module

Provides 3-day AQI forecast using trained models.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple
import logging
import joblib
from pathlib import Path

from ..data.mongodb_handler import MongoDBHandler
from ..features.engineering import apply_all_features
from .model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class AQIPredictor:
    """Predicts AQI for the next 3 days."""
    
    def __init__(self, use_mongodb: bool = True, local_model_path: str = None):
        """
        Initialize AQI Predictor.
        
        Args:
            use_mongodb: If True, load model from MongoDB. If False, load from local path.
            local_model_path: Path to local model directory (if use_mongodb=False)
        """
        self.use_mongodb = use_mongodb
        self.local_model_path = local_model_path
        
        # Load model and components
        self._load_model()
        
        logger.info("✅ AQIPredictor initialized")
    
    def _load_model(self):
        """Load model, scaler, and feature names from MongoDB or local storage."""
        if self.use_mongodb:
            logger.info("Loading model from MongoDB...")
            db_handler = MongoDBHandler()
            registry = ModelRegistry(db_handler)
            
            result = registry.load_active_model()
            if result is None:
                raise ValueError("No active model found in MongoDB registry!")
            
            self.model, self.scaler, self.feature_names, self.metadata = result
        else:
            logger.info(f"Loading model from local path: {self.local_model_path}")
            if not self.local_model_path:
                raise ValueError("local_model_path must be provided when use_mongodb=False")
            
            model_dir = Path(self.local_model_path)
            
            # Load model
            model_files = list(model_dir.glob("*_aqi_v*.pkl"))
            if not model_files:
                raise FileNotFoundError(f"No model file found in {model_dir}")
            
            self.model = joblib.load(model_files[0])
            self.scaler = joblib.load(model_dir / "scaler.pkl")
            self.feature_names = joblib.load(model_dir / "feature_names.pkl")
            
            # Load metadata if available
            metadata_path = model_dir / "model_metadata.pkl"
            if metadata_path.exists():
                self.metadata = joblib.load(metadata_path)
            else:
                self.metadata = {'model_name': 'Local Model'}
        
        logger.info(f"✅ Loaded {self.metadata.get('model_name', 'Model')}")
    
    def _fetch_latest_features(self) -> pd.DataFrame:
        """
        Fetch latest 24 hours of features from MongoDB for lag calculation.
        
        Returns:
            pd.DataFrame: Latest feature data
        """
        logger.info("Fetching latest 24h features from MongoDB...")
        
        db_handler = MongoDBHandler()
        latest_data = db_handler.query_last_n_hours(
            hours=24,
            collection_name='historical_features'
        )
        
        if latest_data.empty:
            logger.warning("⚠️ No recent data found, fetching from current_features...")
            latest_data = db_handler.query_features(
                collection_name='current_features',
                limit=24
            )
        
        if latest_data.empty:
            raise ValueError("No feature data available for prediction!")
        
        logger.info(f"✅ Fetched {len(latest_data)} records")
        return latest_data
    
    def _create_future_features(self, base_data: pd.DataFrame, 
                                days_ahead: int = 3) -> List[pd.DataFrame]:
        """
        Create feature sets for future days using persistence model.
        
        Args:
            base_data: Latest feature data
            days_ahead: Number of days to predict
            
        Returns:
            list: List of DataFrames, one for each future day
        """
        logger.info(f"Creating features for next {days_ahead} days...")
        
        future_features = []
        
        # Get the most recent complete record
        latest_record = base_data.sort_values('timestamp').iloc[-1].copy()
        
        for day in range(1, days_ahead + 1):
            # Create future timestamp
            future_time = latest_record['timestamp'] + timedelta(days=day)
            
            # Use persistence model: assume pollutants remain similar
            # In production, you might want to:
            # 1. Use weather forecast API for meteorological features
            # 2. Use statistical models for pollutant trends
            # 3. Consider seasonal patterns
            
            future_record = latest_record.copy()
            future_record['timestamp'] = future_time
            
            # Update temporal features
            future_record['hour'] = future_time.hour
            future_record['day'] = future_time.day
            future_record['month'] = future_time.month
            future_record['weekday'] = future_time.weekday()
            
            # For lag features, use recent values from base_data
            # This is a simplified approach - production would be more sophisticated
            
            future_features.append(pd.DataFrame([future_record]))
        
        logger.info(f"✅ Created features for {days_ahead} days")
        return future_features
    
    def predict_next_3_days(self) -> Dict[str, Dict]:
        """
        Predict AQI for the next 3 days.
        
        Returns:
            dict: Predictions with format:
                {
                    'Day 1': {'date': ..., 'aqi': ..., 'timestamp': ...},
                    'Day 2': {...},
                    'Day 3': {...}
                }
        """
        logger.info("=" * 60)
        logger.info("🔮 PREDICTING AQI FOR NEXT 3 DAYS")
        logger.info("=" * 60)
        
        # Fetch latest features
        base_data = self._fetch_latest_features()
        
        # Create future feature sets
        future_feature_sets = self._create_future_features(base_data, days_ahead=3)
        
        # Make predictions
        predictions = {}
        
        for idx, future_df in enumerate(future_feature_sets, 1):
            # Select only the features used by the model
            X_future = future_df[self.feature_names]
            
            # Scale features
            X_future_scaled = self.scaler.transform(X_future)
            
            # Predict AQI
            aqi_pred = self.model.predict(X_future_scaled)[0]
            
            # Get timestamp
            future_timestamp = future_df['timestamp'].iloc[0]
            
            predictions[f'Day {idx}'] = {
                'date': future_timestamp.strftime('%Y-%m-%d'),
                'aqi': round(aqi_pred, 2),
                'timestamp': future_timestamp,
                'category': self._aqi_category(aqi_pred)
            }
            
            logger.info(f"Day {idx} ({future_timestamp.strftime('%Y-%m-%d')}): AQI = {aqi_pred:.2f} ({self._aqi_category(aqi_pred)})")
        
        logger.info("=" * 60)
        logger.info("✅ Prediction complete!")
        
        return predictions
    
    @staticmethod
    def _aqi_category(aqi: float) -> str:
        """
        Determine AQI category based on value.
        
        Args:
            aqi: AQI value
            
        Returns:
            str: AQI category
        """
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def check_hazardous_alert(self, predictions: Dict) -> Dict:
        """
        Check if any predictions exceed hazardous AQI levels.
        
        Args:
            predictions: Predictions dictionary from predict_next_3_days()
            
        Returns:
            dict: Alert information
        """
        hazardous_threshold = 200  # Unhealthy threshold
        very_hazardous_threshold = 300  # Very Unhealthy threshold
        
        alerts = {
            'has_alert': False,
            'alert_days': [],
            'max_aqi': 0,
            'message': ""
        }
        
        for day, pred in predictions.items():
            aqi = pred['aqi']
            alerts['max_aqi'] = max(alerts['max_aqi'], aqi)
            
            if aqi >= hazardous_threshold:
                alerts['has_alert'] = True
                alerts['alert_days'].append({
                    'day': day,
                    'date': pred['date'],
                    'aqi': aqi,
                    'category': pred['category']
                })
        
        if alerts['has_alert']:
            if alerts['max_aqi'] >= very_hazardous_threshold:
                alerts['message'] = "⚠️ SEVERE ALERT: Very Unhealthy/Hazardous AQI levels predicted!"
            else:
                alerts['message'] = "⚠️ ALERT: Unhealthy AQI levels predicted!"
        else:
            alerts['message'] = "✅ No hazardous AQI levels predicted for the next 3 days"
        
        return alerts


def predict_aqi_cli():
    """Command-line interface for AQI prediction."""
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize predictor
        predictor = AQIPredictor(use_mongodb=True)
        
        # Make predictions
        predictions = predictor.predict_next_3_days()
        
        # Check for alerts
        alerts = predictor.check_hazardous_alert(predictions)
        
        print("\n" + "=" * 60)
        print("📊 3-DAY AQI FORECAST")
        print("=" * 60)
        for day, pred in predictions.items():
            print(f"\n{day} ({pred['date']}):")
            print(f"  AQI: {pred['aqi']}")
            print(f"  Category: {pred['category']}")
        
        print("\n" + "=" * 60)
        print(alerts['message'])
        print("=" * 60)
        
        if alerts['has_alert']:
            print("\n⚠️ ALERT DETAILS:")
            for alert_day in alerts['alert_days']:
                print(f"  {alert_day['day']} ({alert_day['date']}): AQI {alert_day['aqi']} - {alert_day['category']}")
        
        print()
        
    except Exception as e:
        logger.error(f"❌ Prediction failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    predict_aqi_cli()
