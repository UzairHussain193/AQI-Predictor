"""Fetch current weather and air quality data"""
import requests
import pandas as pd
from datetime import datetime
from src.config import Config
from src.utils.retry import exponential_backoff


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
    
    pollution_data = {
        'timestamp': datetime.utcfromtimestamp(pollution['dt']),
        'aqi': pollution['main']['aqi'],
        'co': pollution['components']['co'],
        'no': pollution['components']['no'],
        'no2': pollution['components']['no2'],
        'o3': pollution['components']['o3'],
        'so2': pollution['components']['so2'],
        'pm2_5': pollution['components']['pm2_5'],
        'pm10': pollution['components']['pm10'],
        'nh3': pollution['components']['nh3']
    }
    
    return pd.DataFrame([pollution_data])
