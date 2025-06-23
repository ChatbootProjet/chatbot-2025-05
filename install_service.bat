@echo off
echo Installing AI Chatbot as Windows Service using NSSM...

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Set variables
set SERVICE_NAME=AIChatbotService
set PROJECT_DIR=%~dp0
set PYTHON_PATH=%PROJECT_DIR%venv\Scripts\python.exe
set SCRIPT_PATH=%PROJECT_DIR%run.py
set NSSM_PATH=%PROJECT_DIR%nssm.exe

REM Check if Python exists in virtual environment
if not exist "%PYTHON_PATH%" (
    echo Virtual environment not found. Using system Python...
    set PYTHON_PATH=python
)

REM Check if NSSM exists
if not exist "%NSSM_PATH%" (
    echo NSSM not found. Please download nssm.exe and place it in the project directory.
    echo Download from: https://nssm.cc/download
    pause
    exit /b 1
)

REM Remove existing service if it exists
echo Removing existing service if it exists...
"%NSSM_PATH%" remove "%SERVICE_NAME%" confirm >nul 2>&1

REM Install the service
echo Installing service...
"%NSSM_PATH%" install "%SERVICE_NAME%" "%PYTHON_PATH%" "%SCRIPT_PATH%"

REM Configure service parameters
echo Configuring service parameters...
"%NSSM_PATH%" set "%SERVICE_NAME%" DisplayName "AI Chatbot Service"
"%NSSM_PATH%" set "%SERVICE_NAME%" Description "AI Chatbot with Flask and Gemini API"
"%NSSM_PATH%" set "%SERVICE_NAME%" Start SERVICE_AUTO_START
"%NSSM_PATH%" set "%SERVICE_NAME%" AppDirectory "%PROJECT_DIR%"

REM Set environment variables
"%NSSM_PATH%" set "%SERVICE_NAME%" AppEnvironmentExtra "FLASK_APP=app.py" "FLASK_ENV=production" "USE_FIREBASE=true"

REM Configure logging
"%NSSM_PATH%" set "%SERVICE_NAME%" AppStdout "%PROJECT_DIR%logs\service_output.log"
"%NSSM_PATH%" set "%SERVICE_NAME%" AppStderr "%PROJECT_DIR%logs\service_error.log"

REM Create logs directory
if not exist "%PROJECT_DIR%logs" mkdir "%PROJECT_DIR%logs"

REM Start the service
echo Starting service...
"%NSSM_PATH%" start "%SERVICE_NAME%"

echo.
echo Service installed successfully!
echo Service Name: %SERVICE_NAME%
echo.
echo To manage the service:
echo - Start: nssm start %SERVICE_NAME%
echo - Stop: nssm stop %SERVICE_NAME%
echo - Remove: nssm remove %SERVICE_NAME% confirm
echo.
echo Logs are saved in: %PROJECT_DIR%logs\
echo.
pause
