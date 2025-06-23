@echo off
echo Starting AI Chatbot Service...

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
set FLASK_RUN_PORT=5000
set USE_FIREBASE=true

REM Start the Flask application
echo Starting Flask application...
python run.py

pause 