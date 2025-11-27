@echo off
REM Blue Team Toolkit V2 - Windows Launch Script

echo ================================================
echo  Blue Team Toolkit V2
echo  Professional Cybersecurity Analysis Platform
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Virtual environment not found. Creating...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies (this may take 5-10 minutes)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

echo.
echo ================================================
echo  Launching Application...
echo ================================================
echo.
echo [INFO] Opening browser at http://localhost:8501
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Launch Streamlit
streamlit run main.py

REM If streamlit exits, pause
pause


