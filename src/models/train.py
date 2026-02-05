"""
Model Training Module

Provides functions to train and evaluate AQI prediction models.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import xgboost as xgb
import lightgbm as lgb
import logging

logger = logging.getLogger(__name__)


def evaluate_model(y_true, y_pred):
    """
    Calculate RMSE, MAE, and R² for model evaluation.
    
    Args:
        y_true: True target values
        y_pred: Predicted target values
        
    Returns:
        dict: Dictionary containing RMSE, MAE, and R² scores
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    return {
        'RMSE': rmse,
        'MAE': mae,
        'R²': r2
    }


def train_models(X_train, y_train, X_val, y_val, X_test, y_test):
    """
    Train 4 regression models: XGBoost, LightGBM, Random Forest, Linear Regression.
    
    Args:
        X_train: Training features
        y_train: Training target
        X_val: Validation features
        y_val: Validation target
        X_test: Test features
        y_test: Test target
        
    Returns:
        tuple: (models_dict, results_dict, scaler)
    """
    logger.info("Starting model training...")
    
    # Feature scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    models = {}
    results = {}
    
    # 1. XGBoost
    logger.info("Training XGBoost...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )
    xgb_model.fit(X_train_scaled, y_train,
                  eval_set=[(X_val_scaled, y_val)],
                  verbose=False)
    
    models['XGBoost'] = xgb_model
    results['XGBoost'] = {
        'train': evaluate_model(y_train, xgb_model.predict(X_train_scaled)),
        'val': evaluate_model(y_val, xgb_model.predict(X_val_scaled)),
        'test': evaluate_model(y_test, xgb_model.predict(X_test_scaled))
    }
    logger.info(f"XGBoost - Test RMSE: {results['XGBoost']['test']['RMSE']:.4f}")
    
    # 2. LightGBM
    logger.info("Training LightGBM...")
    lgb_model = lgb.LGBMRegressor(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgb_model.fit(X_train_scaled, y_train,
                  eval_set=[(X_val_scaled, y_val)])
    
    models['LightGBM'] = lgb_model
    results['LightGBM'] = {
        'train': evaluate_model(y_train, lgb_model.predict(X_train_scaled)),
        'val': evaluate_model(y_val, lgb_model.predict(X_val_scaled)),
        'test': evaluate_model(y_test, lgb_model.predict(X_test_scaled))
    }
    logger.info(f"LightGBM - Test RMSE: {results['LightGBM']['test']['RMSE']:.4f}")
    
    # 3. Random Forest
    logger.info("Training Random Forest...")
    rf_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_train)
    
    models['RandomForest'] = rf_model
    results['RandomForest'] = {
        'train': evaluate_model(y_train, rf_model.predict(X_train_scaled)),
        'val': evaluate_model(y_val, rf_model.predict(X_val_scaled)),
        'test': evaluate_model(y_test, rf_model.predict(X_test_scaled))
    }
    logger.info(f"RandomForest - Test RMSE: {results['RandomForest']['test']['RMSE']:.4f}")
    
    # 4. Linear Regression (baseline)
    logger.info("Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train_scaled, y_train)
    
    models['LinearRegression'] = lr_model
    results['LinearRegression'] = {
        'train': evaluate_model(y_train, lr_model.predict(X_train_scaled)),
        'val': evaluate_model(y_val, lr_model.predict(X_val_scaled)),
        'test': evaluate_model(y_test, lr_model.predict(X_test_scaled))
    }
    logger.info(f"LinearRegression - Test RMSE: {results['LinearRegression']['test']['RMSE']:.4f}")
    
    logger.info("✅ All models trained successfully!")
    
    return models, results, scaler


def select_best_model(models, results):
    """
    Select the best model based on test RMSE.
    
    Args:
        models: Dictionary of trained models
        results: Dictionary of model results
        
    Returns:
        tuple: (best_model_name, best_model)
    """
    best_model_name = min(results.keys(), 
                          key=lambda k: results[k]['test']['RMSE'])
    best_model = models[best_model_name]
    
    logger.info(f"🏆 Best Model: {best_model_name}")
    logger.info(f"   Test RMSE: {results[best_model_name]['test']['RMSE']:.4f}")
    logger.info(f"   Test R²: {results[best_model_name]['test']['R²']:.4f}")
    
    return best_model_name, best_model
