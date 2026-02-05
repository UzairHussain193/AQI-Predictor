"""Feature engineering functions for AQI prediction"""
import pandas as pd
from src.config import Config


def create_temporal_features(df):
    """Create temporal features from timestamp"""
    df = df.copy()
    
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month
    df['day'] = df['timestamp'].dt.day
    df['hour'] = df['timestamp'].dt.hour
    df['weekday'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = (df['weekday'] >= 5).astype(int)
    
    df['season'] = df['month'].apply(lambda m: 
        1 if m in [12, 1, 2] else 
        2 if m in [3, 4, 5] else 
        3 if m in [6, 7, 8] else 4
    )
    
    df['time_of_day'] = df['hour'].apply(lambda h:
        0 if h < 6 else 1 if h < 12 else 2 if h < 18 else 3
    )
    
    return df


def create_lag_features(df, columns=None, lags=None):
    """Create lag features for specified columns"""
    df = df.copy()
    columns = columns or Config.LAG_FEATURES
    lags = lags or Config.LAG_HOURS
    
    for col in columns:
        if col in df.columns:
            for lag in lags:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)
    
    return df


def create_rolling_features(df, columns=None, windows=None):
    """Create rolling statistics for specified columns"""
    df = df.copy()
    columns = columns or Config.ROLLING_FEATURES
    windows = windows or Config.ROLLING_WINDOWS
    
    for col in columns:
        if col in df.columns:
            for window in windows:
                df[f'{col}_rolling_mean_{window}h'] = df[col].rolling(window=window, min_periods=1).mean()
                df[f'{col}_rolling_std_{window}h'] = df[col].rolling(window=window, min_periods=1).std()
                df[f'{col}_rolling_min_{window}h'] = df[col].rolling(window=window, min_periods=1).min()
                df[f'{col}_rolling_max_{window}h'] = df[col].rolling(window=window, min_periods=1).max()
    
    return df


def create_change_rate_features(df, columns=None):
    """Create change rate features"""
    df = df.copy()
    columns = columns or Config.CHANGE_RATE_FEATURES
    
    for col in columns:
        if col in df.columns:
            df[f'{col}_change_rate'] = df[col].pct_change()
    
    return df


def create_interaction_features(df):
    """Create interaction features"""
    df = df.copy()
    
    df['temp_humidity_interaction'] = df['temperature'] * df['humidity']
    df['wind_pm2_5_interaction'] = df['wind_speed'] * df['pm2_5']
    df['wind_temp_interaction'] = df['wind_speed'] * df['temperature']
    df['humidity_pm2_5_interaction'] = df['humidity'] * df['pm2_5']
    
    return df


def create_alert_features(df):
    """Create binary alert features"""
    df = df.copy()
    
    df['high_pollution_alert'] = (df['aqi'] > 3).astype(int)
    df['rain_alert'] = (df['precipitation'] > 0).astype(int)
    df['high_pm2_5_alert'] = (df['pm2_5'] > 15).astype(int)
    df['high_temp_alert'] = (df['temperature'] > 35).astype(int)
    
    return df


def apply_all_features(df, include_lags=True):
    """Apply all feature engineering transformations"""
    df = df.copy()
    
    df = create_temporal_features(df)
    
    if include_lags:
        df = create_lag_features(df)
        df = create_rolling_features(df)
    
    df = create_change_rate_features(df)
    df = create_interaction_features(df)
    df = create_alert_features(df)
    
    df = df.ffill().bfill().dropna()
    
    return df
