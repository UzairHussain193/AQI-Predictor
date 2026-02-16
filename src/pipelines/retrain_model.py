"""
Automated Model Retraining Pipeline

Fetches latest features from MongoDB and retrains the model daily.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from src.data.mongodb_handler import MongoDBHandler
from src.models.train import train_models, select_best_model
from src.models.model_registry import ModelRegistry
import joblib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retrain_model():
    """
    Retrain model with latest data from MongoDB feature store.
    
    This function:
    1. Fetches all features from MongoDB
    2. Prepares training data
    3. Trains 4 models
    4. Selects best model
    5. Saves to MongoDB registry and locally
    """
    logger.info("=" * 80)
    logger.info("AUTOMATED MODEL RETRAINING")
    logger.info("=" * 80)
    logger.info(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    
    try:
        # 1. Initialize MongoDB handler
        logger.info("\n1.Connecting to MongoDB...")
        db_handler = MongoDBHandler()
        
        # 2. Fetch all historical features
        logger.info("\n2. Fetching data from feature store...")
        data = db_handler.query_features(collection_name='historical_features', limit=None)
        
        if data.empty:
            raise ValueError("No data found in MongoDB! Cannot retrain model.")
        
        logger.info(f"Loaded {len(data)} records")
        logger.info(f"   Date Range: {data['timestamp'].min()} to {data['timestamp'].max()}")
        
        # 3. Prepare features and target
        logger.info("\n3. Preparing features and target...")
        
        # Drop non-feature columns
        columns_to_drop = ['timestamp', '_id']
        df_clean = data.drop(columns=[col for col in columns_to_drop if col in data.columns], errors='ignore')
        
        # Separate features and target
        target_col = 'aqi'
        if target_col not in df_clean.columns:
            raise ValueError(f"Target column '{target_col}' not found!")
        
        X = df_clean.drop(columns=[target_col])
        y = df_clean[target_col]
        
        # Feature selection: top 40 by correlation
        correlations = X.corrwith(y).abs().sort_values(ascending=False)
        top_features = correlations.head(40).index.tolist()
        X_selected = X[top_features]
        
        logger.info(f"Selected {len(top_features)} features")
        logger.info(f"   Target (AQI) range: {y.min():.2f} - {y.max():.2f}")
        
        # 4. Time-based train-test split
        logger.info("\n4. Splitting data (time-based)...")
        n = len(X_selected)
        train_size = int(0.70 * n)
        val_size = int(0.15 * n)
        
        X_train = X_selected.iloc[:train_size]
        X_val = X_selected.iloc[train_size:train_size+val_size]
        X_test = X_selected.iloc[train_size+val_size:]
        
        y_train = y.iloc[:train_size]
        y_val = y.iloc[train_size:train_size+val_size]
        y_test = y.iloc[train_size+val_size:]
        
        logger.info(f"   Train: {len(X_train):,} samples ({len(X_train)/n*100:.1f}%)")
        logger.info(f"   Val:   {len(X_val):,} samples ({len(X_val)/n*100:.1f}%)")
        logger.info(f"   Test:  {len(X_test):,} samples ({len(X_test)/n*100:.1f}%)")
        
        # 5. Train models
        logger.info("\n5. Training models...")
        models, results, scaler = train_models(
            X_train, y_train, 
            X_val, y_val, 
            X_test, y_test
        )
        
        # 6. Select best model
        logger.info("\n6. Selecting best model...")
        best_model_name, best_model = select_best_model(models, results)
        
        # 7. Save to local storage
        logger.info("\n7. Saving to local storage...")
        models_dir = project_root / "models"
        models_dir.mkdir(exist_ok=True)
        
        model_filename = f"{best_model_name.lower()}_aqi_retrained.pkl"
        model_path = models_dir / model_filename
        joblib.dump(best_model, model_path)
        
        scaler_path = models_dir / "scaler.pkl"
        joblib.dump(scaler, scaler_path)
        
        feature_names_path = models_dir / "feature_names.pkl"
        joblib.dump(top_features, feature_names_path)
        
        metadata = {
            'model_name': best_model_name,
            'model_filename': model_filename,
            'trained_at': datetime.now(timezone.utc).isoformat(),
            'features': top_features,
            'n_features': len(top_features),
            'performance': results[best_model_name]['test'],
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        metadata_path = models_dir / "model_metadata.pkl"
        joblib.dump(metadata, metadata_path)
        
        logger.info(f"Model saved to: {model_path}")
        
        # 8. Save to MongoDB registry
        logger.info("\n8. Saving to MongoDB model registry...")
        registry = ModelRegistry(db_handler)
        
        # Increment version number
        existing_models = registry.list_models(limit=1)
        if existing_models:
            last_version = existing_models[0].get('version', 'v0')
            version_num = int(last_version.replace('v', '')) + 1
            new_version = f'v{version_num}'
        else:
            new_version = 'v1'
        
        performance = {
            'test_rmse': float(results[best_model_name]['test']['RMSE']),
            'test_mae': float(results[best_model_name]['test']['MAE']),
            'test_r2': float(results[best_model_name]['test']['R²'])
        }
        
        training_info = {
            'trained_at': datetime.now(timezone.utc),
            'training_samples': int(len(X_train)),
            'test_samples': int(len(X_test)),
            'aqi_range': {'min': float(y.min()), 'max': float(y.max())},
            'retrained': True
        }
        
        model_id = registry.save_model(
            model=best_model,
            scaler=scaler,
            model_name=best_model_name,
            version=new_version,
            feature_names=top_features,
            performance=performance,
            training_info=training_info
        )
        
        logger.info(f"Model saved to MongoDB! ID: {model_id}")
        
        # 9. Summary
        logger.info("\n" + "=" * 80)
        logger.info("MODEL RETRAINING COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"Model: {best_model_name} {new_version}")
        logger.info(f"Test RMSE: {results[best_model_name]['test']['RMSE']:.4f}")
        logger.info(f"Test MAE:  {results[best_model_name]['test']['MAE']:.4f}")
        logger.info(f"Test R²:   {results[best_model_name]['test']['R²']:.4f}")
        logger.info(f"Completed at: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"\nRETRAINING FAILED: {str(e)}")
        logger.exception("Full traceback:")
        return False


if __name__ == "__main__":
    success = retrain_model()
    sys.exit(0 if success else 1)
