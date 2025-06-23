@echo off
echo Uninstalling AI Chatbot Windows Service...

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
set NSSM_PATH=%PROJECT_DIR%nssm.exe

REM Check if NSSM exists
if not exist "%NSSM_PATH%" (
    echo NSSM not found. Please download nssm.exe and place it in the project directory.
    echo Download from: https://nssm.cc/download
    pause
    exit /b 1
)

REM Stop the service
echo Stopping service...
"%NSSM_PATH%" stop "%SERVICE_NAME%" >nul 2>&1

REM Remove the service
echo Removing service...
"%NSSM_PATH%" remove "%SERVICE_NAME%" confirm

echo.
echo Service uninstalled successfully!
echo Service Name: %SERVICE_NAME%
echo.
pause 