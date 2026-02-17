"""
Diagnostic Version - Shows Exactly What's Failing
"""
import streamlit as st
import sys
from pathlib import Path
import os
import traceback

st.set_page_config(page_title="AQI Predictor - Diagnostic", page_icon="🔍", layout="wide")

# Setup paths
WEBAPP_DIR = Path(__file__).parent
PROJECT_ROOT = WEBAPP_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

st.title("🔍 Import Diagnostics")

# Show path info
with st.expander("📂 Path Information", expanded=True):
    st.code(f"Current file: {__file__}")
    st.code(f"WEBAPP_DIR: {WEBAPP_DIR}")
    st.code(f"PROJECT_ROOT: {PROJECT_ROOT}")
    st.code(f"sys.path[0]: {sys.path[0]}")

# Check directory structure
with st.expander("📁 Directory Structure", expanded=True):
    st.write("**Project Root Contents:**")
    try:
        for item in sorted(PROJECT_ROOT.iterdir()):
            emoji = "📁" if item.is_dir() else "📄"
            st.write(f"{emoji} {item.name}")
    except Exception as e:
        st.error(f"Error reading PROJECT_ROOT: {e}")
    
    st.write("**src/ Contents:**")
    src_dir = PROJECT_ROOT / "src"
    if src_dir.exists():
        for item in sorted(src_dir.iterdir()):
            emoji = "📁" if item.is_dir() else "📄"
            st.write(f"{emoji} {item.name}")
    else:
        st.error("src/ directory not found!")

# Test imports one by one
st.header("🧪 Testing Imports")

# Test 1: Basic imports
st.subheader("1️⃣ Testing Basic Python Packages")
basic_imports = {
    "pandas": "import pandas as pd",
    "numpy": "import numpy as np",
    "plotly": "import plotly.graph_objects as go",
    "pymongo": "import pymongo",
    "python-dotenv": "from dotenv import load_dotenv"
}

for name, import_code in basic_imports.items():
    try:
        exec(import_code)
        st.success(f"✅ {name}")
    except ImportError as e:
        st.error(f"❌ {name} - {str(e)}")
        st.caption(f"→ Add '{name}' to requirements.txt")

# Test 2: src package
st.subheader("2️⃣ Testing src Package")
try:
    import src
    st.success("✅ src package accessible")
    st.code(f"src location: {src.__file__}")
except ImportError as e:
    st.error(f"❌ Cannot import src: {e}")
    st.code(traceback.format_exc())

# Test 3: src.data
st.subheader("3️⃣ Testing src.data")
try:
    import src.data
    st.success("✅ src.data package accessible")
except ImportError as e:
    st.error(f"❌ Cannot import src.data: {e}")
    st.code(traceback.format_exc())

# Test 4: mongodb_handler
st.subheader("4️⃣ Testing MongoDBHandler")
try:
    from src.data.mongodb_handler import MongoDBHandler
    st.success("✅ MongoDBHandler imported successfully!")
    st.write(f"MongoDBHandler class: {MongoDBHandler}")
except ImportError as e:
    st.error(f"❌ Cannot import MongoDBHandler: {e}")
    st.code(traceback.format_exc())
except Exception as e:
    st.error(f"❌ Error in mongodb_handler.py: {e}")
    st.code(traceback.format_exc())

# Test 5: src.models
st.subheader("5️⃣ Testing src.models")
try:
    import src.models
    st.success("✅ src.models package accessible")
except ImportError as e:
    st.error(f"❌ Cannot import src.models: {e}")
    st.code(traceback.format_exc())

# Test 6: AQIPredictor
st.subheader("6️⃣ Testing AQIPredictor")
try:
    from src.models.predict import AQIPredictor
    st.success("✅ AQIPredictor imported successfully!")
    st.write(f"AQIPredictor class: {AQIPredictor}")
except ImportError as e:
    st.error(f"❌ Cannot import AQIPredictor: {e}")
    st.code(traceback.format_exc())
except Exception as e:
    st.error(f"❌ Error in predict.py: {e}")
    st.code(traceback.format_exc())

# Test 7: ModelRegistry
st.subheader("7️⃣ Testing ModelRegistry")
try:
    from src.models.model_registry import ModelRegistry
    st.success("✅ ModelRegistry imported successfully!")
    st.write(f"ModelRegistry class: {ModelRegistry}")
except ImportError as e:
    st.error(f"❌ Cannot import ModelRegistry: {e}")
    st.code(traceback.format_exc())
except Exception as e:
    st.error(f"❌ Error in model_registry.py: {e}")
    st.code(traceback.format_exc())

# Check for common issues
st.header("🔧 Common Issues Check")

issues_found = []

# Check requirements.txt
req_file = WEBAPP_DIR / "requirements.txt"
if req_file.exists():
    st.success(f"✅ requirements.txt found at {req_file}")
    with open(req_file) as f:
        st.code(f.read())
else:
    st.warning("⚠️ requirements.txt not found in streamlit/")
    issues_found.append("Missing requirements.txt")

# Check __init__.py files
init_files = [
    "src/__init__.py",
    "src/data/__init__.py",
    "src/models/__init__.py",
    "src/features/__init__.py"
]

for init_file in init_files:
    init_path = PROJECT_ROOT / init_file
    if init_path.exists():
        st.success(f"✅ {init_file} exists")
    else:
        st.warning(f"⚠️ {init_file} missing")
        issues_found.append(f"Missing {init_file}")

# Summary
st.header("📊 Summary")
if not issues_found:
    st.success("✅ No obvious issues found. Check the detailed errors above.")
else:
    st.error("❌ Issues found:")
    for issue in issues_found:
        st.write(f"- {issue}")

st.info("""
**Next Steps:**
1. Look at the error messages above to see which import is failing
2. Check if the required package is in requirements.txt
3. Check if there are any import errors WITHIN your module files
4. Make sure all dependencies of your modules are installed
""")