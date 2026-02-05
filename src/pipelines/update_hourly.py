"""Hourly update: Fetch current data and append to MongoDB"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
from datetime import datetime, timezone
from src.data.fetch_current import fetch_current_weather, fetch_current_pollution
from src.data.mongodb_handler import MongoDBHandler
from src.features.engineering import apply_all_features


def main():
    """Update feature store with current hour data"""
    
    try:
        print(f"Fetching current data at {datetime.now(timezone.utc)}")
        weather_df = fetch_current_weather()
        pollution_df = fetch_current_pollution()
        
        # Normalize timestamps to the same hour (APIs may return slightly different times)
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp']).dt.floor('H')
        pollution_df['timestamp'] = pd.to_datetime(pollution_df['timestamp']).dt.floor('H')
        
        current_df = pd.merge(weather_df, pollution_df, on='timestamp', how='inner')
        
        if current_df.empty:
            print("✗ Error: Merge resulted in empty dataframe. Check API responses.")
            print(f"Weather timestamp: {weather_df['timestamp'].iloc[0] if not weather_df.empty else 'None'}")
            print(f"Pollution timestamp: {pollution_df['timestamp'].iloc[0] if not pollution_df.empty else 'None'}")
            sys.exit(1)
        
        current_timestamp = current_df['timestamp'].iloc[0]
        
        mongo = MongoDBHandler()
        
        if mongo.check_timestamp_exists(current_timestamp, 'historical_features'):
            print(f"Data for {current_timestamp} already exists. Skipping.")
            mongo.close()
            return
        
        print("Getting last 24 hours for lag features...")
        historical_24h = mongo.get_last_n_hours(24, 'historical_features')
        
        if historical_24h is not None:
            combined_df = pd.concat([historical_24h, current_df], ignore_index=True)
            features_df = apply_all_features(combined_df, include_lags=True)
            new_record = features_df.tail(1)
        else:
            new_record = apply_all_features(current_df, include_lags=False)
        
        added, skipped = mongo.append_features(new_record, 'historical_features')
        mongo.close()
        
        print(f"✓ Added: {added}, Skipped: {skipped}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
