"""Fetch historical weather and air quality data"""
import requests
import pandas as pd
from datetime import datetime
import openmeteo_requests
from src.config import Config


def fetch_historical_weather(lat=None, lon=None, start_date=None, end_date=None):
    """Fetch historical weather data from Open-Meteo Archive API"""
    lat = lat or Config.LATITUDE
    lon = lon or Config.LONGITUDE
    start_date = start_date or Config.HISTORICAL_START_DATE
    end_date = end_date or Config.HISTORICAL_END_DATE
    
    om = openmeteo_requests.Client()
    
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': start_date,
        'end_date': end_date,
        'hourly': ['temperature_2m', 'relative_humidity_2m', 'dew_point_2m', 
                   'precipitation', 'surface_pressure', 'wind_speed_10m', 'wind_direction_10m']
    }
    
    response = om.weather_api(Config.OPENMETEO_ARCHIVE_URL, params=params)[0]
    hourly = response.Hourly()
    
    weather_data = {
        'timestamp': pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit='s'),
            end=pd.to_datetime(hourly.TimeEnd(), unit='s'),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive='left'
        ),
        'temperature': hourly.Variables(0).ValuesAsNumpy(),
        'humidity': hourly.Variables(1).ValuesAsNumpy(),
        'dew_point': hourly.Variables(2).ValuesAsNumpy(),
        'precipitation': hourly.Variables(3).ValuesAsNumpy(),
        'pressure': hourly.Variables(4).ValuesAsNumpy(),
        'wind_speed': hourly.Variables(5).ValuesAsNumpy(),
        'wind_direction': hourly.Variables(6).ValuesAsNumpy()
    }
    
    return pd.DataFrame(weather_data)


def fetch_historical_pollution(lat=None, lon=None, start_date=None, end_date=None):
    """Fetch historical air quality data from OpenWeather API"""
    lat = lat or Config.LATITUDE
    lon = lon or Config.LONGITUDE
    start_date = start_date or Config.HISTORICAL_START_DATE
    end_date = end_date or Config.HISTORICAL_END_DATE
    
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    
    params = {
        'lat': lat,
        'lon': lon,
        'start': start_timestamp,
        'end': end_timestamp,
        'appid': Config.OPENWEATHER_API_KEY
    }
    
    response = requests.get(Config.AIR_POLLUTION_HISTORY_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    pollution_records = []
    for record in data['list']:
        pollution_records.append({
            'timestamp': datetime.utcfromtimestamp(record['dt']),
            'aqi': record['main']['aqi'],
            'co': record['components']['co'],
            'no': record['components']['no'],
            'no2': record['components']['no2'],
            'o3': record['components']['o3'],
            'so2': record['components']['so2'],
            'pm2_5': record['components']['pm2_5'],
            'pm10': record['components']['pm10'],
            'nh3': record['components']['nh3']
        })
    
    return pd.DataFrame(pollution_records)
