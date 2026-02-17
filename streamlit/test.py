"""
Streamlit Dashboard for AQI Prediction System
Air Quality Index Predictor for Hyderabad, Sindh
"""

import streamlit as st
import sys
from pathlib import Path
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone, timedelta
import time

# # Import project modules
# from src.data.mongodb_handler import MongoDBHandler
# from src.models.predict import AQIPredictor
# from src.models.model_registry import ModelRegistry

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


# Page configuration
st.set_page_config(
    page_title="AQI Predictor - Hyderabad",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
