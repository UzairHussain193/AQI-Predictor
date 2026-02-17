"""
Streamlit Dashboard for AQI Prediction System
Air Quality Index Predictor for Hyderabad, Sindh
"""

import sys
from pathlib import Path
import os

# Add project root to path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # Go up from streamlit/ to project root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# # Debug: Verify paths (can remove after fixing)
# print(f"🔍 DEBUG INFO:")
# print(f"Current file: {current_file}")
# print(f"Project root: {project_root}")
# print(f"Project root exists: {project_root.exists()}")
# print(f"src folder exists: {(project_root / 'src').exists()}")
# print(f"src/data exists: {(project_root / 'src' / 'data').exists()}")
# print(f"src/__init__.py exists: {(project_root / 'src' / '__init__.py').exists()}")
# print(f"sys.path[0]: {sys.path[0]}")

import streamlit as st

# SET ENVIRONMENT VARIABLES FROM SECRETS (before other imports)
# This ensures MongoDB handler and data fetchers use the correct credentials
# os.environ["MONGODB_URI"] = st.secrets.get("MONGODB_URI", os.getenv("MONGODB_URI", ""))
# os.environ["MONGODB_DATABASE"] = st.secrets.get("MONGODB_DATABASE", os.getenv("MONGODB_DATABASE", "aqi_feature_store"))

# Around line 30, change to:
os.environ["MONGODB_USERNAME"] = st.secrets.get("MONGODB_USERNAME", os.getenv("MONGODB_USERNAME", ""))
os.environ["MONGODB_PASSWORD"] = st.secrets.get("MONGODB_PASSWORD", os.getenv("MONGODB_PASSWORD", ""))
os.environ["MONGODB_CLUSTER"] = st.secrets.get("MONGODB_CLUSTER", os.getenv("MONGODB_CLUSTER", ""))
os.environ["MONGODB_DATABASE"] = st.secrets.get("MONGODB_DATABASE", os.getenv("MONGODB_DATABASE", "aqi_feature_store"))
os.environ["OPENWEATHER_API_KEY"] = st.secrets.get("OPENWEATHER_API_KEY", os.getenv("OPENWEATHER_API_KEY", ""))

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone, timedelta
import time

# Import project modules
from src.data.mongodb_handler import MongoDBHandler
from src.models.predict import AQIPredictor
from src.models.model_registry import ModelRegistry


# Page configuration
st.set_page_config(
    page_title="AQI Predictor - Hyderabad",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Hero Header - Ultra Modern - Force Override */
    .main-header {
        font-size: 6.5rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #ff6ec7 75%, #ff9a56 100%) !important;
        background-size: 200% auto !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        padding: 3rem 1rem 1rem 1rem !important;
        letter-spacing: -4px !important;
        animation: fadeInDown 0.8s ease-out, gradientShift 8s ease infinite !important;
        text-shadow: 0 0 40px rgba(102, 126, 234, 0.5) !important;
        position: relative !important;
        line-height: 1.1 !important;
        display: block !important;
        margin: 0 auto !important;
    }
    
    /* Responsive sizing for smaller screens */
    @media (max-width: 768px) {
        .main-header {
            font-size: 3.5rem !important;
            letter-spacing: -2px !important;
        }
        .subtitle {
            font-size: 1.1rem !important;
        }
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 120%;
        height: 120%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.2) 0%, transparent 70%);
        z-index: -1;
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
        50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
    }
    
    .subtitle {
        font-size: 1.5rem !important;
        text-align: center !important;
        color: #a8b2c6 !important;
        font-weight: 600 !important;
        margin-top: -0.5rem !important;
        padding-bottom: 2rem !important;
        animation: fadeIn 1s ease-out 0.3s both !important;
        letter-spacing: 0.5px !important;
        display: block !important;
    }
    
    /* Modern Metric Card */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeIn 0.6s ease-out;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    /* Forecast Cards - Modern Glassmorphism */
    .forecast-card {
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: all 0.3s ease;
        animation: slideUp 0.5s ease-out;
        min-height: 180px;
    }
    
    .forecast-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* AQI Category Colors - Enhanced */
    .good { 
        background: linear-gradient(135deg, #00e400 0%, #00b300 100%);
        color: white;
    }
    .moderate { 
        background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%);
        color: white;
    }
    .unhealthy-sensitive { 
        background: linear-gradient(135deg, #ff7e00 0%, #ff6b00 100%);
        color: white;
    }
    .unhealthy { 
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
        color: white;
    }
    .very-unhealthy { 
        background: linear-gradient(135deg, #8f3f97 0%, #6d2077 100%);
        color: white;
    }
    .hazardous { 
        background: linear-gradient(135deg, #7e0023 0%, #5a0019 100%);
        color: white;
    }
    
    /* Model Performance Card */
    .model-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.3);
    }
    
    .metric-row {
        display: flex;
        justify-content: space-between;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        border-radius: 15px;
        margin-top: 2rem;
    }
    
    .footer-icon:hover {
        transform: translateY(-5px) scale(1.15) !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.6) !important;
        transition: all 0.3s ease !important;
    }
    
    /* Improved Spacing */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 2rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# Cache functions
@st.cache_resource
def init_db_handler():
    """Initialize MongoDB handler"""
    return MongoDBHandler()

@st.cache_resource
def init_predictor():
    """Initialize AQI Predictor"""
    return AQIPredictor(use_mongodb=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_current_aqi(_db_handler):
    """Load current AQI from MongoDB"""
    collection = _db_handler.db['historical_features']
    # Get the most recent record by sorting timestamp descending
    latest_doc = collection.find_one(sort=[('timestamp', -1)])
    if latest_doc:
        return latest_doc.get('aqi'), latest_doc.get('timestamp')
    return None, None

@st.cache_data(ttl=3600)
def load_historical_data(_db_handler, days=7):
    """Load historical AQI data"""
    from datetime import timedelta
    collection = _db_handler.db['historical_features']
    
    # Calculate cutoff time for last N days
    cutoff_time = datetime.now() - timedelta(days=days)
    
    # Query records from last N days, sorted by timestamp
    cursor = collection.find(
        {'timestamp': {'$gte': cutoff_time}}
    ).sort('timestamp', 1)  # 1 = ascending
    
    documents = list(cursor)
    
    if not documents:
        return pd.DataFrame()
    
    # Convert to DataFrame - flatten all nested fields
    rows = []
    for doc in documents:
        row = {}
        # Flatten document - handle nested features
        for key, value in doc.items():
            if key == '_id':
                row['_id'] = str(value)
            elif isinstance(value, dict):
                # If value is dict, flatten it
                row.update(value)
            else:
                row[key] = value
        rows.append(row)
    
    df = pd.DataFrame(rows)
    return df

@st.cache_data(ttl=3600)
def get_predictions(_predictor):
    """Get 3-day predictions"""
    predictions = _predictor.predict_next_3_days()
    alerts = _predictor.check_hazardous_alert(predictions)
    return predictions, alerts


def get_aqi_category(aqi):
    """Get AQI category and color"""
    if aqi <= 50:
        return "Good", "good", "🟢"
    elif aqi <= 100:
        return "Moderate", "moderate", "🟡"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "unhealthy-sensitive", "🟠"
    elif aqi <= 200:
        return "Unhealthy", "unhealthy", "🔴"
    elif aqi <= 300:
        return "Very Unhealthy", "very-unhealthy", "🟣"
    else:
        return "Hazardous", "hazardous", "🟤"


def get_health_message(aqi):
    """Get health recommendation based on AQI"""
    if aqi <= 50:
        return "Air quality is good. It's a great day to be active outside!"
    elif aqi <= 100:
        return "Air quality is acceptable. Unusually sensitive people should consider reducing prolonged outdoor exertion."
    elif aqi <= 150:
        return "Sensitive groups should reduce prolonged or heavy outdoor exertion."
    elif aqi <= 200:
        return "Everyone should reduce prolonged or heavy outdoor exertion."
    elif aqi <= 300:
        return "Everyone should avoid prolonged or heavy outdoor exertion."
    else:
        return "Health alert: Everyone should avoid all outdoor exertion."


def create_gauge_chart(aqi, title="Current AQI"):
    """Create gauge chart for AQI"""
    category, color_class, emoji = get_aqi_category(aqi)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = aqi,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, 500], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "#00e400"},
                {'range': [50, 100], 'color': "#ffff00"},
                {'range': [100, 150], 'color': "#ff7e00"},
                {'range': [150, 200], 'color': "#ff0000"},
                {'range': [200, 300], 'color': "#8f3f97"},
                {'range': [300, 500], 'color': "#7e0023"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 200
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def create_forecast_chart(predictions):
    """Create 3-day forecast bar chart"""
    days = list(predictions.keys())
    aqi_values = [pred['aqi'] for pred in predictions.values()]
    dates = [pred['date'] for pred in predictions.values()]
    
    colors = []
    for aqi in aqi_values:
        if aqi <= 50:
            colors.append('#00e400')
        elif aqi <= 100:
            colors.append('#ffff00')
        elif aqi <= 150:
            colors.append('#ff7e00')
        elif aqi <= 200:
            colors.append('#ff0000')
        elif aqi <= 300:
            colors.append('#8f3f97')
        else:
            colors.append('#7e0023')
    
    fig = go.Figure(data=[
        go.Bar(
            x=dates,
            y=aqi_values,
            marker_color=colors,
            text=aqi_values,
            texttemplate='%{text:.1f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>AQI: %{y:.1f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="3-Day AQI Forecast",
        xaxis_title="Date",
        yaxis_title="AQI",
        height=400,
        showlegend=False,
        hovermode='x'
    )
    
    return fig


def create_historical_chart(data, days=7):
    """Create historical AQI trend chart"""
    if data.empty:
        return None
    
    # Get last N days
    data_sorted = data.sort_values('timestamp')
    recent_data = data_sorted.tail(days * 24)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=recent_data['timestamp'],
        y=recent_data['aqi'],
        mode='lines+markers',
        name='AQI',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4),
        hovertemplate='%{x}<br>AQI: %{y:.1f}<extra></extra>'
    ))
    
    # Add threshold lines
    fig.add_hline(y=50, line_dash="dash", line_color="green", annotation_text="Good")
    fig.add_hline(y=100, line_dash="dash", line_color="yellow", annotation_text="Moderate")
    fig.add_hline(y=150, line_dash="dash", line_color="orange", annotation_text="Unhealthy for Sensitive")
    fig.add_hline(y=200, line_dash="dash", line_color="red", annotation_text="Unhealthy")
    
    fig.update_layout(
        title=f"AQI Trend - Last {days} Days",
        xaxis_title="Date",
        yaxis_title="AQI",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_pollutant_chart(data):
    """Create pollutant breakdown chart"""
    if data.empty:
        return None
    
    latest = data.iloc[-1]
    
    # Map possible column names to pollutants
    pollutant_mappings = {
        'PM2.5': ['pm25', 'pm2_5', 'pm2.5', 'PM25'],
        'PM10': ['pm10', 'PM10'],
        'O3': ['o3', 'O3'],
        'NO2': ['no2', 'NO2'],
        'CO': ['co', 'CO']
    }
    
    pollutants = {}
    for name, possible_cols in pollutant_mappings.items():
        value = 0
        for col in possible_cols:
            if col in latest.index:
                value = latest.get(col, 0)
                break
        pollutants[name] = value
    
    fig = go.Figure(data=[
        go.Bar(
            y=list(pollutants.keys()),
            x=list(pollutants.values()),
            orientation='h',
            marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7'],
            text=[f"{v:.1f}" for v in pollutants.values()],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Current Pollutant Levels",
        xaxis_title="Concentration",
        yaxis_title="Pollutant",
        height=350,
        showlegend=False
    )
    
    return fig


def main():
    """Main Streamlit app"""
    
    # DEBUG: Print to logs
    print("🚀 App starting...")
    print(f"📝 Secrets available: {list(st.secrets.keys())}")
    st.write("If you see this, secrets and imports work!")
    st.write(f"MongoDB Username: {os.getenv('MONGODB_USERNAME')}")
    st.write(f"Database: {os.getenv('MONGODB_DATABASE')}")



if __name__ == "__main__":
    main()
