"""Fetch historical weather and air quality data"""
import requests
import pandas as pd
from datetime import datetime
import openmeteo_requests
from src.config import Config
from src.utils.aqi_calculator import calculate_epa_aqi


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
        components = record['components']
        
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
        
        pollution_records.append({
            'timestamp': datetime.utcfromtimestamp(record['dt']),
            'aqi': epa_aqi,  # US EPA AQI (0-500 scale)
            'openweather_aqi': record['main']['aqi'],  # Keep original (1-5 scale)
            'pm25': pm25,
            'pm2_5': pm25,  # Alias for compatibility
            'pm10': pm10,
            'o3': o3,
            'no2': no2,
            'so2': so2,
            'co': co,
            'no': components.get('no', 0),
            'nh3': components.get('nh3', 0)
        })
    
    return pd.DataFrame(pollution_records)
