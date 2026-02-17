import streamlit as st
import sys
from pathlib import Path
import os
import traceback

# Wrap everything in try-except to catch startup errors
try:
    st.set_page_config(page_title="AQI Predictor", page_icon="🌍", layout="wide")
    
    st.title("AQI Predictor - Test Page")
    st.write("✅ Streamlit is running successfully!")
    st.write("This is a test page to verify that the Streamlit app can access the MongoDB database and display data correctly.")
    
    # Debug information
    with st.expander("Debug Information"):
        st.write(f"Python Version: {sys.version}")
        st.write(f"Current Directory: {os.getcwd()}")
        st.write(f"Files in current directory: {os.listdir('.')}")
        
except Exception as e:
    st.error(f"Error during app initialization: {str(e)}")
    st.code(traceback.format_exc())