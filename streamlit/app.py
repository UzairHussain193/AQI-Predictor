"""
Streamlit Dashboard for AQI Prediction System
Air Quality Index Predictor for Hyderabad, Sindh
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import streamlit as st
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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .forecast-card {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .good { background-color: #00e400; }
    .moderate { background-color: #ffff00; }
    .unhealthy-sensitive { background-color: #ff7e00; }
    .unhealthy { background-color: #ff0000; color: white; }
    .very-unhealthy { background-color: #8f3f97; color: white; }
    .hazardous { background-color: #7e0023; color: white; }
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
    data = _db_handler.query_features(collection_name='historical_features', limit=1)
    if not data.empty:
        latest = data.iloc[-1]
        return latest['aqi'], latest['timestamp']
    return None, None

@st.cache_data(ttl=3600)
def load_historical_data(_db_handler, days=7):
    """Load historical AQI data"""
    data = _db_handler.query_features(collection_name='historical_features', limit=days*24)
    return data

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
    
    pollutants = {
        'PM2.5': latest.get('pm25', 0),
        'PM10': latest.get('pm10', 0),
        'O3': latest.get('o3', 0),
        'NO2': latest.get('no2', 0),
        'CO': latest.get('co', 0)
    }
    
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
    
    # Header
    st.markdown('<p class="main-header">🌍 Air Quality Index Predictor</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: gray;">Hyderabad, Sindh, Pakistan (25.3960°N, 68.3578°E)</p>', unsafe_allow_html=True)
    
    # Initialize
    try:
        db_handler = init_db_handler()
    except Exception as e:
        st.error(f"❌ Failed to connect to MongoDB: {str(e)}")
        st.info("Please check your MONGODB_URI environment variable and network connection.")
        st.stop()
    
    # Initialize predictor (may fail if no model exists yet)
    predictor = None
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
        
        # Model info
        st.subheader("🤖 Active Model")
        try:
            registry = ModelRegistry(db_handler)
            result = registry.load_active_model()
            if result:
                _, _, _, metadata = result
                st.write(f"**Model:** {metadata.get('model_name', 'Unknown')}")
                st.write(f"**Version:** {metadata.get('version', 'N/A')}")
                
                # Performance metrics
                perf = metadata.get('performance', {})
                if perf:
                    st.write(f"**RMSE:** {perf.get('test_rmse', 0):.2f}")
                    st.write(f"**R²:** {perf.get('test_r2', 0):.3f}")
                
                # Created date
                created = metadata.get('created_at')
                if created:
                    try:
                        st.write(f"**Updated:** {created.strftime('%Y-%m-%d')}")
                    except:
                        st.write(f"**Updated:** {str(created)[:10]}")
            else:
                st.warning("No active model found")
        except Exception as e:
            st.warning("Model info unavailable")
            st.caption(f"Details: {str(e)}")
        
        st.divider()
        
        # About
        st.subheader("ℹ️ About")
        st.info("""
        **Data Sources:**
        - OpenWeather API
        - Open-Meteo Archive
        
        **Update Frequency:**
        - Hourly data collection
        - Daily model retraining
        
        **Features:**
        - 3-day AQI forecast
        - Real-time monitoring
        - Historical trends
        """)
    
    # Main content
    try:
        # Load data
        current_aqi, current_time = load_current_aqi(db_handler)
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
        
        # 3-Day Forecast
        st.header("🔮 3-Day Forecast")
        
        if predictions:
            cols = st.columns(3)
            for idx, (day, pred) in enumerate(predictions.items()):
                category, color_class, emoji = get_aqi_category(pred['aqi'])
                with cols[idx]:
                    st.markdown(f"""
                    <div class="forecast-card {color_class}">
                        <h3>{day}</h3>
                        <p style="margin: 0.5rem 0; font-weight: bold;">{pred['date']}</p>
                        <h1 style="margin: 0.5rem 0;">{emoji} {pred['aqi']:.1f}</h1>
                        <p style="margin: 0; font-weight: 500;">{category}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
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
                pollutant_data = {
                    'Pollutant': ['PM2.5', 'PM10', 'O3', 'NO2', 'CO'],
                    'Current Level': [
                        f"{latest.get('pm25', 0):.2f} µg/m³",
                        f"{latest.get('pm10', 0):.2f} µg/m³",
                        f"{latest.get('o3', 0):.2f} µg/m³",
                        f"{latest.get('no2', 0):.2f} µg/m³",
                        f"{latest.get('co', 0):.2f} µg/m³"
                    ]
                }
                st.dataframe(pd.DataFrame(pollutant_data), use_container_width=True)
            else:
                st.warning("No pollutant data available")
        
        with tab3:
            if not historical_data.empty:
                st.subheader("Statistical Summary")
                
                # Descriptive statistics
                stats = historical_data[['aqi', 'pm25', 'pm10', 'o3', 'no2', 'co']].describe()
                st.dataframe(stats, use_container_width=True)
                
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
                # Prepare download data
                download_data = historical_data[['timestamp', 'aqi', 'pm25', 'pm10', 'o3', 'no2', 'co']].copy()
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
    st.caption("© 2026 AQI Predictor | Data updated hourly | Models retrained daily")


if __name__ == "__main__":
    main()
