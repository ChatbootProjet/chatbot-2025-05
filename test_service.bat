@echo off
echo Testing AI Chatbot Service...
echo.

REM Test if Python is available
echo 1. Testing Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
) else (
    echo ✅ Python is available
)
echo.

REM Test if required packages are installed
echo 2. Testing required packages...
python -c "import flask, nltk, google.generativeai" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Some required packages are missing!
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    echo ✅ All required packages are available
)
echo.

REM Test if config file exists
echo 3. Testing configuration...
if exist "config.py" (
    echo ✅ Configuration file found
) else (
    echo ❌ config.py not found!
    pause
    exit /b 1
)
echo.

REM Test if port 5000 is available
echo 4. Testing port availability...
netstat -an | findstr :5000 >nul
if %errorlevel% equ 0 (
    echo ⚠️  Port 5000 is already in use!
    echo This might cause conflicts. Consider stopping other services.
) else (
    echo ✅ Port 5000 is available
)
echo.

REM Test basic Flask app startup
echo 5. Testing Flask application startup...
echo Starting test server (will stop automatically in 10 seconds)...
timeout /t 2 /nobreak >nul

REM Start Flask in background and capture PID
start /B python run.py >test_output.log 2>&1
timeout /t 5 /nobreak >nul

REM Test if server responds
echo Testing server response...
curl -s http://localhost:5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Server is responding correctly
) else (
    echo ⚠️  Server might not be responding (curl not available or server issue)
    echo Check test_output.log for details
)

REM Stop test server
echo Stopping test server...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo           Test Summary
echo ========================================
echo.
if exist "test_output.log" (
    echo Server startup log:
    type test_output.log
    del test_output.log >nul 2>&1
)

echo.
echo Test completed! If all tests passed, you can proceed with service installation.
echo.
pause 