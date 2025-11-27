#!/bin/bash
# Blue Team Toolkit V2 - Linux/Mac Launch Script

set -e  # Exit on error

echo "================================================"
echo " Blue Team Toolkit V2"
echo " Professional Cybersecurity Analysis Platform"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "[OK] Virtual environment created"
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if ! python -c "import streamlit" &> /dev/null; then
    echo "[INFO] Installing dependencies (this may take 5-10 minutes)..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "[OK] Dependencies installed"
else
    echo "[OK] Dependencies already installed"
fi

echo ""
echo "================================================"
echo " Launching Application..."
echo "================================================"
echo ""
echo "[INFO] Opening browser at http://localhost:8501"
echo "[INFO] Press Ctrl+C to stop the server"
echo ""

# Launch Streamlit
streamlit run main.py


