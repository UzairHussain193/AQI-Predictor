import streamlit as st
# import sys
# from pathlib import Path
# import os

# 1. Page config (FIRST st. command)
st.set_page_config(page_title="AQI Predictor", page_icon="🌍", layout="wide")

# # 2. Path setup
# WEBAPP_DIR = Path(__file__).parent
# PROJECT_ROOT = WEBAPP_DIR.parent
# sys.path.insert(0, str(PROJECT_ROOT))

# # 3. Other imports
# import pandas as pd
# from dotenv import load_dotenv
# # ... etc

# # 4. Load .env for local dev (optional)
# if (PROJECT_ROOT / '.env').exists():
#     load_dotenv(PROJECT_ROOT / '.env')

# # 5. Helper function for environment setup
# def setup_environment():
#     os.environ["MONGODB_USERNAME"] = st.secrets.get("MONGODB_USERNAME", os.getenv("MONGODB_USERNAME", ""))
#     os.environ["MONGODB_PASSWORD"] = st.secrets.get("MONGODB_PASSWORD", os.getenv("MONGODB_PASSWORD", ""))
#     os.environ["MONGODB_CLUSTER"] = st.secrets.get("MONGODB_CLUSTER", os.getenv("MONGODB_CLUSTER", ""))
#     os.environ["MONGODB_DATABASE"] = st.secrets.get("MONGODB_DATABASE", os.getenv("MONGODB_DATABASE", "aqi_feature_store"))
#     os.environ["OPENWEATHER_API_KEY"] = st.secrets.get("OPENWEATHER_API_KEY", os.getenv("OPENWEATHER_API_KEY", ""))

# 6. Main function
def main():
    # setup_environment()  # Call this FIRST
    
    st.title("Test App")
    # st.write(f"Username: {os.getenv('MONGODB_USERNAME')}")
    # st.write(f"Database: {os.getenv('MONGODB_DATABASE')}")
    # st.write(f"OpenWeather API Key: {os.getenv('OPENWEATHER_API_KEY')[:5]}...")  # Show first 5 chars for security
    # # ... rest of your app

# 7. Entry point
if __name__ == "__main__":
    main()