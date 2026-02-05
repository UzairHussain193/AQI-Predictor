"""
Command-Line Tool for AQI Predictions

Usage:
    python predict_aqi.py              # Get 3-day forecast
    python predict_aqi.py --local      # Use local model instead of MongoDB
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import argparse
import logging
from src.models.predict import AQIPredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for CLI tool."""
    parser = argparse.ArgumentParser(description='AQI 3-Day Forecast Predictor')
    parser.add_argument(
        '--local',
        action='store_true',
        help='Use local model instead of MongoDB'
    )
    parser.add_argument(
        '--model-dir',
        type=str,
        default='models',
        help='Path to local model directory (if --local is used)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize predictor
        if args.local:
            logger.info(f"Using local model from: {args.model_dir}")
            predictor = AQIPredictor(use_mongodb=False, local_model_path=args.model_dir)
        else:
            logger.info("Using active model from MongoDB registry")
            predictor = AQIPredictor(use_mongodb=True)
        
        # Make predictions
        predictions = predictor.predict_next_3_days()
        
        # Check for alerts
        alerts = predictor.check_hazardous_alert(predictions)
        
        # Display results
        print("\n" + "=" * 70)
        print("📊 AQI 3-DAY FORECAST")
        print("=" * 70)
        
        for day, pred in predictions.items():
            print(f"\n{day} - {pred['date']} ({pred['timestamp'].strftime('%A')})")
            print(f"  AQI:      {pred['aqi']}")
            print(f"  Category: {pred['category']}")
            
            # Add color coding
            aqi_val = pred['aqi']
            if aqi_val <= 50:
                emoji = "✅"
            elif aqi_val <= 100:
                emoji = "🟡"
            elif aqi_val <= 150:
                emoji = "🟠"
            elif aqi_val <= 200:
                emoji = "🔴"
            elif aqi_val <= 300:
                emoji = "🟣"
            else:
                emoji = "🟤"
            
            print(f"  Status:   {emoji} {pred['category']}")
        
        print("\n" + "=" * 70)
        print(alerts['message'])
        print("=" * 70)
        
        if alerts['has_alert']:
            print("\n⚠️ ALERT DETAILS:")
            for alert_day in alerts['alert_days']:
                print(f"  {alert_day['day']} ({alert_day['date']}): "
                      f"AQI {alert_day['aqi']} - {alert_day['category']}")
        
        print()
        
    except Exception as e:
        logger.error(f"❌ Prediction failed: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
