@echo off
echo Creating Task Scheduler entry for AI Chatbot...

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
set PROJECT_DIR=%~dp0
set BATCH_FILE=%PROJECT_DIR%start_service.bat

REM Delete existing task if it exists
echo Removing existing task if it exists...
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

REM Create new task
echo Creating new scheduled task...
schtasks /create /tn "%TASK_NAME%" /tr "\"%BATCH_FILE%\"" /sc onstart /ru "SYSTEM" /rl highest /f

if %errorlevel% equ 0 (
    echo.
    echo Task created successfully!
    echo Task Name: %TASK_NAME%
    echo.
    echo The AI Chatbot will now start automatically when Windows starts.
    echo.
    echo To manage the task:
    echo - Run: schtasks /run /tn "%TASK_NAME%"
    echo - Delete: schtasks /delete /tn "%TASK_NAME%" /f
    echo - View: schtasks /query /tn "%TASK_NAME%"
    echo.
) else (
    echo.
    echo Error creating scheduled task!
    echo Please check the error messages above.
    echo.
)

pause 