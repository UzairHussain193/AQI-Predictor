"""One-time setup: Fetch historical data and upload to MongoDB"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
from src.data.fetch_historical import fetch_historical_weather, fetch_historical_pollution
from src.data.mongodb_handler import MongoDBHandler
from src.features.engineering import apply_all_features


def main():
    """Setup historical data in feature store"""
    
    print("Fetching historical weather data...")
    weather_df = fetch_historical_weather()
    print(f"✓ Fetched {len(weather_df)} weather records")
    
    print("Fetching historical pollution data...")
    pollution_df = fetch_historical_pollution()
    print(f"✓ Fetched {len(pollution_df)} pollution records")
    
    print("Merging data...")
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
    pollution_df['timestamp'] = pd.to_datetime(pollution_df['timestamp'])
    merged_df = pd.merge(weather_df, pollution_df, on='timestamp', how='inner')
    print(f"✓ Merged: {len(merged_df)} records")
    
    print("Applying feature engineering...")
    features_df = apply_all_features(merged_df, include_lags=True)
    print(f"✓ Created {len(features_df.columns)} features")
    
    print("Uploading to MongoDB...")
    mongo = MongoDBHandler()
    uploaded = mongo.upload_features(features_df, collection_name='historical_features')
    mongo.close()
    print(f"✓ Uploaded {uploaded} records to MongoDB")
    
    print("\n✓ Historical setup complete!")


if __name__ == '__main__':
    main()
