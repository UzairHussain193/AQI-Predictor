"""Fetch current weather and air quality data"""
import requests
import pandas as pd
from datetime import datetime
from src.config import Config
from src.utils.retry import exponential_backoff
from src.utils.aqi_calculator import calculate_epa_aqi


@exponential_backoff()
def fetch_current_weather(lat=None, lon=None):
    """Fetch current weather data from OpenWeather API"""
    lat = lat or Config.LATITUDE
    lon = lon or Config.LONGITUDE
    
    params = {
        'lat': lat,
        'lon': lon,
        'appid': Config.OPENWEATHER_API_KEY,
        'units': 'metric'
    }
    
    response = requests.get(Config.CURRENT_WEATHER_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    weather_data = {
        'timestamp': datetime.utcfromtimestamp(data['dt']),
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'pressure': data['main']['pressure'],
        'wind_speed': data['wind']['speed'],
        'wind_direction': data['wind'].get('deg', 0),
        'precipitation': 0.0,
        'dew_point': data['main']['temp'] - ((100 - data['main']['humidity']) / 5)
    }
    
    return pd.DataFrame([weather_data])


@exponential_backoff()
def fetch_current_pollution(lat=None, lon=None):
    """Fetch current air quality data from OpenWeather API"""
    lat = lat or Config.LATITUDE
    lon = lon or Config.LONGITUDE
    
    params = {
        'lat': lat,
        'lon': lon,
        'appid': Config.OPENWEATHER_API_KEY
    }
    
    response = requests.get(Config.AIR_POLLUTION_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    pollution = data['list'][0]
    components = pollution['components']
    
    # Extract pollutant concentrations (μg/m³)
    pm25 = components.get('pm2_5', 0)
    pm10 = components.get('pm10', 0)
    o3 = components.get('o3', 0)
    no2 = components.get('no2', 0)
    so2 = components.get('so2', 0)
    co = components.get('co', 0)
    
    # Calculate US EPA AQI (0-500 scale) from pollutant concentrations
    epa_aqi = calculate_epa_aqi(
        pm25=pm25,
        pm10=pm10,
        o3=o3,
        no2=no2,
        so2=so2,
        co=co
    )
    
    pollution_data = {
        'timestamp': datetime.utcfromtimestamp(pollution['dt']),
        'aqi': epa_aqi,  # US EPA AQI (0-500 scale)
        'openweather_aqi': pollution['main']['aqi'],  # Keep original (1-5 scale)
        'pm25': pm25,
        'pm2_5': pm25,  # Alias for compatibility
        'pm10': pm10,
        'o3': o3,
        'no2': no2,
        'so2': so2,
        'co': co,
        'no': components.get('no', 0),
        'nh3': components.get('nh3', 0)
    }
    
    return pd.DataFrame([pollution_data])
