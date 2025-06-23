@echo off
echo Starting AI Chatbot with Global Access...
echo.
echo ⚠️  WARNING: This will make your chatbot accessible from anywhere on the internet!
echo    Only use this if you understand the security implications.
echo.
pause

REM Change to the project directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Set environment variables for global access
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_RUN_HOST=0.0.0.0
set FLASK_RUN_PORT=80
set FLASK_DEBUG=1
set USE_FIREBASE=true

echo.
echo Starting Flask application with global access...
echo.
echo The chatbot will be accessible from:
echo - Local: http://localhost
echo - Network: http://[YOUR-IP]  
echo - Internet: http://[YOUR-PUBLIC-IP] (if ports are forwarded)
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python run.py

pause 