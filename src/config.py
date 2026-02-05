"""
Configuration file for AQI Predictor Project
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the project"""
    
    # API Configuration
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    
    # OpenWeather API Endpoints
    CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
    AIR_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
    AIR_POLLUTION_HISTORY_URL = "https://api.openweathermap.org/data/2.5/air_pollution/history"
    OPENMETEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    # Location Configuration (Hyderabad, Sindh)
    LATITUDE = float(os.getenv('LATITUDE', 25.3960))
    LONGITUDE = float(os.getenv('LONGITUDE', 68.3578))
    CITY_NAME = os.getenv('CITY_NAME', 'Hyderabad')
    
    # MongoDB Configuration
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
    MONGODB_CLUSTER = os.getenv('MONGODB_CLUSTER')
    MONGODB_DATABASE = 'aqi_feature_store'
    
    # Data Collection Settings
    DATA_FETCH_INTERVAL = int(os.getenv('DATA_FETCH_INTERVAL', 3600))
    HISTORICAL_START_DATE = '2025-11-01'
    HISTORICAL_END_DATE = '2026-01-31'
    
    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    RETRY_BACKOFF = 2
    
    # Feature Engineering Configuration
    LAG_HOURS = [1, 6, 12, 24]
    ROLLING_WINDOWS = [6, 12, 24]
    LAG_FEATURES = ['aqi', 'pm2_5', 'pm10', 'co', 'no2']
    ROLLING_FEATURES = ['aqi', 'pm2_5', 'pm10', 'co', 'no2']
    CHANGE_RATE_FEATURES = ['pm2_5', 'pm10', 'co', 'no2', 'temperature', 'humidity', 'wind_speed']
    
    # File Paths
    BASE_DIR = Path(__file__).parent.parent
    LOGS_PATH = BASE_DIR / 'logs'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENWEATHER_API_KEY:
            raise ValueError("OPENWEATHER_API_KEY not set in .env file")
        if not all([cls.MONGODB_USERNAME, cls.MONGODB_PASSWORD, cls.MONGODB_CLUSTER]):
            raise ValueError("MongoDB credentials not set in .env file")
        return True

# Validate configuration on import
Config.validate()
