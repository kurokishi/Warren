#!/bin/bash

echo "Starting WarrenAI Stock Prediction App..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Install requirements if needed
echo "Checking dependencies..."
pip3 install -r requirements.txt

# Run the app
echo ""
echo "Starting Streamlit app..."
echo "Open your browser and go to: http://localhost:8501"
echo "Press Ctrl+C to stop"
echo ""

streamlit run app_streamlit.py
