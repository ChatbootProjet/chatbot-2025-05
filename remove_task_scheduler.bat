@echo off
echo Removing AI Chatbot Task Scheduler entry...

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Set variables
set TASK_NAME=AIChatbotAutoStart

REM Delete existing task
echo Removing scheduled task...
schtasks /delete /tn "%TASK_NAME%" /f

if %errorlevel% equ 0 (
    echo.
    echo Task removed successfully!
    echo Task Name: %TASK_NAME%
    echo.
) else (
    echo.
    echo Error removing scheduled task or task does not exist!
    echo.
)

pause 