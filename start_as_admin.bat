@echo off
echo Starting AI Chatbot with Administrator Privileges on Port 80...

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% equ 0 (
    echo ✅ Running with Administrator privileges
    goto :run_app
) else (
    echo ⚠️  Not running as Administrator
    echo 🔄 Requesting Administrator privileges...
    
    REM Re-run this script with admin privileges
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:run_app
REM Change to the project directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Set environment variables for port 80
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_RUN_HOST=0.0.0.0
set FLASK_RUN_PORT=80
set USE_FIREBASE=true

echo.
echo ========================================
echo     AI Chatbot - Administrator Mode
echo ========================================
echo.
echo ✅ Running with Administrator privileges
echo 🌐 Starting on port 80 (HTTP default)
echo 📱 Accessible at: http://localhost
echo 🌍 Network access: http://[YOUR-IP]
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the Flask application
python run.py

pause 