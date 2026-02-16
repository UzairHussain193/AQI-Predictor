"""
Clear old data and re-fetch with correct EPA AQI calculations

This script:
1. Backs up existing data (optional)
2. Clears historical_features collection
3. Re-runs setup_historical.py with corrected AQI
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.mongodb_handler import MongoDBHandler


def main():
    """Clear and re-fetch data"""
    
    print("=" * 60)
    print("CLEAR & RE-FETCH DATA WITH CORRECTED EPA AQI")
    print("=" * 60)
    
    # Connect to MongoDB
    mongo = MongoDBHandler()
    collection = mongo.db['historical_features']
    
    # Check current data
    current_count = collection.count_documents({})
    print(f"\n📊 Current records: {current_count:,}")
    
    if current_count > 0:
        # Show sample old AQI
        sample = collection.find_one()
        old_aqi = sample.get('aqi') if sample else None
        print(f"   Sample old AQI: {old_aqi} (OpenWeather 1-5 scale)")
    
    # Confirm deletion
    print(f"\nThis will DELETE all {current_count:,} records")
    print("   and re-fetch with correct EPA AQI (0-500 scale)")
    
    response = input("\n   Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\nCancelled.")
        return
    
    # Delete all records
    print("\nDeleting old data...")
    result = collection.delete_many({})
    print(f"   ✓ Deleted {result.deleted_count:,} records")
    
    mongo.close()
    
    print("\n🔄 Now run setup_historical.py to re-fetch data:")
    print("   python src/pipelines/setup_historical.py")
    print("\n✓ Database cleared successfully!")


if __name__ == '__main__':
    main()
