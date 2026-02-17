"""
Streamlit Dashboard for AQI Prediction System
Air Quality Index Predictor for Hyderabad, Sindh
"""
import streamlit as st
import sys
from pathlib import Path
import os


# Page configuration
st.set_page_config(
    page_title="AQI Predictor - Hyderabad",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# WEBAPP_DIR = Path(__file__).parent
# PROJECT_ROOT = WEBAPP_DIR.parent
# sys.path.insert(0, str(PROJECT_ROOT))

# Lines 19-21: Change to
PROJECT_ROOT = Path(__file__).parent     # AQI Predictor/
sys.path.insert(0, str(PROJECT_ROOT))
# # Import project modules
# from src.data.mongodb_handler import MongoDBHandler
# from src.models.predict import AQIPredictor
# from src.models.model_registry import ModelRegistry

import pandas as pd
from dotenv import load_dotenv
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone, timedelta
import time



# 4. Load .env for local dev (optional)
# if (PROJECT_ROOT / '.env').exists():
#     load_dotenv(PROJECT_ROOT / '.env')


def setup_environment():
    os.environ["MONGODB_USERNAME"] = st.secrets.get("MONGODB_USERNAME", os.getenv("MONGODB_USERNAME", ""))
    os.environ["MONGODB_PASSWORD"] = st.secrets.get("MONGODB_PASSWORD", os.getenv("MONGODB_PASSWORD", ""))
    os.environ["MONGODB_CLUSTER"] = st.secrets.get("MONGODB_CLUSTER", os.getenv("MONGODB_CLUSTER", ""))
    os.environ["MONGODB_DATABASE"] = st.secrets.get("MONGODB_DATABASE", os.getenv("MONGODB_DATABASE", "aqi_feature_store"))
    os.environ["OPENWEATHER_API_KEY"] = st.secrets.get("OPENWEATHER_API_KEY", os.getenv("OPENWEATHER_API_KEY", ""))


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
    
    setup_environment()  # Call the setup function
    
    # Import project modules
    from src.data.mongodb_handler import MongoDBHandler
    from src.models.predict import AQIPredictor
    from src.models.model_registry import ModelRegistry

    # Hero Header
    st.markdown('<p class="main-header">🌍 Air Quality Index Predictor</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">📍 Hyderabad, Sindh, Pakistan (25.3960°N, 68.3578°E)</p>', unsafe_allow_html=True)
    
    # AQI Information Panel
    with st.expander("ℹ️ What is AQI? (Click to learn more)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📊 Air Quality Index Scale
            
            **AQI** measures air pollution levels:
            
            - **0-50**: Good 🟢  
              Air quality is satisfactory, and air pollution poses little or no risk.
            
            - **51-100**: Moderate 🟡  
              Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.
            
            - **101-150**: Unhealthy for Sensitive Groups 🟠  
              Members of sensitive groups may experience health effects. The general public is less likely to be affected.
            
            - **151-200**: Unhealthy 🔴  
              Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.
            
            - **201-300**: Very Unhealthy 🟣  
              Health alert: The risk of health effects is increased for everyone.
            
            - **301+**: Hazardous 🟤  
              Health warning of emergency conditions: everyone is more likely to be affected.
            """)
        
        with col2:
            st.markdown("""
            ### 🧪 Major Pollutants
            
            **PM2.5** (Fine Particulate Matter)  
            Tiny particles ≤2.5 micrometers that can penetrate deep into lungs and bloodstream.
            
            **PM10** (Coarse Particulate Matter)  
            Particles ≤10 micrometers from dust, pollen, and mold.
            
            **O₃** (Ozone)  
            Ground-level ozone, a key component of smog that can trigger asthma.
            
            **NO₂** (Nitrogen Dioxide)  
            Gas from vehicle emissions and power plants that irritates airways.
            
            **SO₂** (Sulfur Dioxide)  
            Gas from fossil fuel combustion that can cause respiratory issues.
            
            **CO** (Carbon Monoxide)  
            Colorless, odorless gas that reduces oxygen delivery to organs.
            
            ---
            
            ### 🏃 Health Recommendations
            
            - **Good (0-50)**: Ideal for all outdoor activities
            - **Moderate (51-100)**: Sensitive groups should limit prolonged outdoor exertion
            - **Unhealthy for Sensitive (101-150)**: Reduce prolonged/heavy outdoor exertion
            - **Unhealthy (151-200)**: Everyone should reduce outdoor activities
            - **Very Unhealthy (201-300)**: Avoid all outdoor exertion
            - **Hazardous (301+)**: Stay indoors, use air purifiers
            """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Initialize with loading animation
    with st.spinner('🔄 Connecting to database...'):
        try:
            db_handler = init_db_handler()
        except Exception as e:
            st.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            st.info("Please check your MONGODB_URI environment variable and network connection.")
            st.stop()
    
    # Initialize predictor (may fail if no model exists yet)
    predictor = None
    with st.spinner('🤖 Loading prediction model...'):
        try:
            predictor = init_predictor()
        except Exception as e:
            st.warning(f"⚠️ Predictor initialization: {str(e)}")
            st.info("The dashboard will run in read-only mode. Train a model first using Model_Training.ipynb")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        
        # Date range selector
        st.subheader("📅 Historical Data")
        days_to_show = st.slider("Days to display", 1, 30, 7)
        
        st.divider()
        
        # Model info - Enhanced Display
        st.subheader("🤖 Active Model")
        try:
            registry = ModelRegistry(db_handler)
            result = registry.load_active_model()
            if result:
                _, _, _, metadata = result
                
                # Model Card
                st.markdown(f"""
                <div class="model-card">
                    <h3 style="margin: 0 0 1rem 0;">🎯 {metadata.get('model_name', 'Unknown')}</h3>
                    <div class="metric-row">
                        <span>Version</span>
                        <strong>{metadata.get('version', 'N/A')}</strong>
                    </div>
                """, unsafe_allow_html=True)
                
                # Performance metrics
                perf = metadata.get('performance', {})
                if perf:
                    rmse = perf.get('test_rmse', 0)
                    r2 = perf.get('test_r2', 0)
                    mae = perf.get('test_mae', 0)
                    
                    st.markdown(f"""
                    <div class="metric-row">
                        <span>RMSE</span>
                        <strong>{rmse:.3f}</strong>
                    </div>
                    <div class="metric-row">
                        <span>R² Score</span>
                        <strong>{r2:.3f}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if mae:
                        st.markdown(f"""
                        <div class="metric-row">
                            <span>MAE</span>
                            <strong>{mae:.3f}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Created date
                created = metadata.get('created_at')
                if created:
                    try:
                        date_str = created.strftime('%Y-%m-%d')
                    except:
                        date_str = str(created)[:10]
                    st.markdown(f"""
                    <div class="metric-row">
                        <span>Last Updated</span>
                        <strong>{date_str}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Performance interpretation
                if perf:
                    r2 = perf.get('test_r2', 0)
                    if r2 >= 0.9:
                        st.success("✅ Excellent model performance!")
                    elif r2 >= 0.8:
                        st.info("✓ Good model performance")
                    else:
                        st.warning("⚠️ Model may need retraining")
            else:
                st.warning("No active model found")
        except Exception as e:
            st.warning("Model info unavailable")
            st.caption(f"Details: {str(e)}")
        
        st.divider()
        
        # Data Info
        st.subheader("📊 Data Info")
        try:
            collection = db_handler.db['historical_features']
            total_records = collection.count_documents({})
            st.write(f"**Total Records:** {total_records:,}")
            
            # Get latest record to show available fields
            latest = collection.find_one(sort=[('timestamp', -1)])
            if latest:
                st.write(f"**Latest Data:** {latest['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                
                # Show available pollutant fields
                pollutants = []
                for key in ['pm25', 'pm2_5', 'pm10', 'o3', 'no2', 'co', 'so2']:
                    if key in latest:
                        pollutants.append(key.upper())
                
                if pollutants:
                    st.write(f"**Pollutants:** {', '.join(pollutants)}")
        except Exception as e:
            st.caption(f"Could not load data info")
    
    # Main content
    try:
        # Load data with loading animation
        with st.spinner('📊 Loading current AQI data...'):
            current_aqi, current_time = load_current_aqi(db_handler)
        
        with st.spinner('📈 Loading historical data...'):
            historical_data = load_historical_data(db_handler, days_to_show)
        
        # Get predictions (only if predictor initialized)
        predictions = None
        alerts = {'has_alert': False}
        if predictor:
            try:
                predictions, alerts = get_predictions(predictor)
            except Exception as e:
                st.warning(f"⚠️ Could not generate predictions: {str(e)}")
        
        # Last updated
        st.caption(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Current AQI Section
        st.header("📊 Current Air Quality")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if current_aqi:
                category, color_class, emoji = get_aqi_category(current_aqi)
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="margin: 0;">{emoji} {current_aqi:.1f}</h2>
                    <h3 style="margin: 0.5rem 0;">{category}</h3>
                    <p style="margin: 0; font-size: 0.9rem;">{current_time.strftime('%Y-%m-%d %H:%M') if current_time else 'N/A'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.info(get_health_message(current_aqi))
            else:
                st.warning("No current AQI data available")
        
        with col2:
            if current_aqi:
                st.plotly_chart(create_gauge_chart(current_aqi), use_container_width=True)
        
        st.divider()
        
        # Alerts
        if alerts and alerts.get('has_alert'):
            st.error(f"⚠️ {alerts['message']}")
            with st.expander("View Alert Details"):
                for alert_day in alerts['alert_days']:
                    st.write(f"**{alert_day['day']}** ({alert_day['date']}): AQI {alert_day['aqi']:.1f} - {alert_day['category']}")
        
        # 3-Day Forecast - Enhanced Layout
        st.header("🔮 3-Day Forecast")
        
        if predictions:
            # Forecast Cards with better spacing
            cols = st.columns([1, 1, 1], gap="large")
            for idx, (day, pred) in enumerate(predictions.items()):
                category, color_class, emoji = get_aqi_category(pred['aqi'])
                with cols[idx]:
                    st.markdown(f"""
                    <div class="forecast-card {color_class}">
                        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700;">{day}</h2>
                        <p style="margin: 0.8rem 0; font-weight: 600; font-size: 0.95rem; opacity: 0.9;">{pred['date']}</p>
                        <div style="margin: 1.5rem 0;">
                            <div style="font-size: 3.5rem; margin: 0.5rem 0;">{emoji}</div>
                            <h1 style="margin: 0.5rem 0; font-size: 2.5rem; font-weight: 800;">{pred['aqi']:.1f}</h1>
                        </div>
                        <p style="margin: 0; font-weight: 600; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.5px;">{category}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Chart with animation
            with st.spinner('📊 Generating forecast chart...'):
                st.plotly_chart(create_forecast_chart(predictions), use_container_width=True)
        else:
            st.info("📝 3-day predictions unavailable. Please train a model first using Model_Training.ipynb")
        
        st.divider()
        
        # Tabs for detailed views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Historical Trends", "🧪 Pollutant Breakdown", "📊 Statistics", "📥 Download Data"])
        
        with tab1:
            if not historical_data.empty:
                fig = create_historical_chart(historical_data, days_to_show)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Average AQI", f"{historical_data['aqi'].mean():.1f}")
                with col2:
                    st.metric("Max AQI", f"{historical_data['aqi'].max():.1f}")
                with col3:
                    st.metric("Min AQI", f"{historical_data['aqi'].min():.1f}")
                with col4:
                    trend = "↑" if historical_data['aqi'].iloc[-1] > historical_data['aqi'].iloc[-24] else "↓"
                    st.metric("24h Trend", trend)
            else:
                st.warning("No historical data available")
        
        with tab2:
            if not historical_data.empty:
                fig = create_pollutant_chart(historical_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Pollutant table
                latest = historical_data.iloc[-1]
                
                # Find available pollutant columns
                pollutant_mappings = {
                    'PM2.5': ['pm25', 'pm2_5', 'pm2.5', 'PM25'],
                    'PM10': ['pm10', 'PM10'],
                    'O3': ['o3', 'O3'],
                    'NO2': ['no2', 'NO2'],
                    'CO': ['co', 'CO']
                }
                
                pollutant_data = {'Pollutant': [], 'Current Level': []}
                for name, possible_cols in pollutant_mappings.items():
                    value = 0
                    for col in possible_cols:
                        if col in latest.index:
                            value = latest.get(col, 0)
                            break
                    pollutant_data['Pollutant'].append(name)
                    pollutant_data['Current Level'].append(f"{value:.2f} µg/m³")
                
                st.dataframe(pd.DataFrame(pollutant_data), use_container_width=True)
            else:
                st.warning("No pollutant data available")
        
        with tab3:
            if not historical_data.empty:
                st.subheader("Statistical Summary")
                
                # Select available columns for statistics
                available_cols = ['aqi']
                pollutant_cols = ['pm25', 'pm2_5', 'pm10', 'o3', 'no2', 'co', 'so2', 'nh3']
                for col in pollutant_cols:
                    if col in historical_data.columns:
                        available_cols.append(col)
                
                if len(available_cols) > 1:
                    stats = historical_data[available_cols].describe()
                    st.dataframe(stats, use_container_width=True)
                else:
                    st.warning("Limited data available for statistics")
                
                # AQI distribution
                fig = px.histogram(historical_data, x='aqi', nbins=50, 
                                   title="AQI Distribution",
                                   labels={'aqi': 'AQI', 'count': 'Frequency'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for statistics")
        
        with tab4:
            st.subheader("Download Historical Data")
            
            if not historical_data.empty:
                # Prepare download data - select available columns
                base_cols = ['timestamp', 'aqi']
                pollutant_cols = ['pm25', 'pm2_5', 'pm10', 'o3', 'no2', 'co', 'so2', 'nh3']
                
                cols_to_export = base_cols.copy()
                for col in pollutant_cols:
                    if col in historical_data.columns:
                        cols_to_export.append(col)
                
                download_data = historical_data[cols_to_export].copy()
                download_data['timestamp'] = download_data['timestamp'].astype(str)
                
                csv = download_data.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"aqi_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.info(f"Dataset contains {len(download_data)} records")
            else:
                st.warning("No data available for download")
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.exception(e)
    
    # Footer
    st.divider()
    st.markdown("### 🌍 AQI Predictor")
    st.caption("Air Quality Monitoring & Prediction System for Hyderabad, Sindh")
    st.caption("Data updated hourly | Models retrained daily")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("💻 GitHub", "https://github.com/uzairhussain193/")
    with col2:
        st.link_button("💼 LinkedIn", "https://linkedin.com/in/uzairhussain1")
    with col3:
        st.link_button("🌐 Portfolio", "https://bitly.cx/uzairhussain/")

    st.caption("© 2026 Built with ❤️ using Streamlit | Part of 10 Pearls Shine Internship")




if __name__ == "__main__":
    main()
