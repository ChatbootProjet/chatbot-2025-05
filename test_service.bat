@echo off
echo Testing AI Chatbot Service Setup...
echo.

REM Change to project directory
cd /d "%~dp0"

echo ========================================
echo        System Requirements Test
echo ========================================

REM Test 1: Check Python installation
echo 1. Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ Python not found or not in PATH
    echo    Please install Python 3.8+ and add to PATH
    goto :error
) else (
    python --version
    echo    ✅ Python is installed
)

REM Test 2: Check pip
echo.
echo 2. Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ pip not found
    goto :error
) else (
    echo    ✅ pip is available
)

REM Test 3: Check virtual environment (optional)
echo.
echo 3. Checking virtual environment...
if exist "venv\Scripts\python.exe" (
    echo    ✅ Virtual environment found
    set PYTHON_PATH=venv\Scripts\python.exe
) else (
    echo    ⚠️  Virtual environment not found (using system Python)
    set PYTHON_PATH=python
)

REM Test 4: Check required packages
echo.
echo 4. Checking required packages...
%PYTHON_PATH% -c "import flask, nltk" >nul 2>&1
if %errorlevel% neq 0 (
    echo    ❌ Required packages not installed
    echo    Installing requirements...
    %PYTHON_PATH% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo    ❌ Failed to install requirements
        goto :error
    )
) else (
    echo    ✅ Required packages are installed
)

REM Test 5: Check port 80 availability
echo.
echo 5. Checking port 80 availability...
netstat -an | findstr :80 >nul
if %errorlevel% equ 0 (
    echo    ⚠️  Port 80 is already in use
    echo    This might cause conflicts. Common users:
    netstat -ano | findstr :80
    echo    Note: You may need to stop IIS or other web servers
) else (
    echo    ✅ Port 80 is available
)

REM Test 6: Check administrator privileges
echo.
echo 6. Checking administrator privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠️  Not running as Administrator
    echo    Some features may require admin privileges (port 80, firewall, service installation)
) else (
    echo    ✅ Running with Administrator privileges
)

REM Test 7: Check NSSM (optional)
echo.
echo 7. Checking NSSM availability...
if exist "nssm.exe" (
    echo    ✅ NSSM found - Service installation available
) else (
    echo    ⚠️  NSSM not found - Download from https://nssm.cc/download for service installation
)

REM Test 8: Check firewall rules
echo.
echo 8. Checking Windows Firewall...
netsh advfirewall firewall show rule name="AI Chatbot" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Firewall rule exists
) else (
    echo    ⚠️  Firewall rule not found - Run setup_firewall.bat as Administrator
)

REM Test 9: Test basic Flask functionality
echo.
echo 9. Testing Flask application...
echo    Starting Flask test (will stop automatically after 10 seconds)...

REM Start Flask in background and test
start /b %PYTHON_PATH% -c "
import sys
sys.path.append('.')
from app import app
import threading
import time
def stop_server():
    time.sleep(10)
    import os
    os._exit(0)
threading.Thread(target=stop_server, daemon=True).start()
app.run(host='127.0.0.1', port=8080, debug=False)
" >nul 2>&1

REM Wait and test connection
timeout /t 3 /nobreak >nul
powershell -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8080' -TimeoutSec 5 | Out-Null; Write-Host '    ✅ Flask application responds correctly' } catch { Write-Host '    ❌ Flask application test failed' }"

REM Test 10: Check disk space
echo.
echo 10. Checking disk space...
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set FREE_SPACE=%%a
if defined FREE_SPACE (
    echo    ✅ Disk space check completed
) else (
    echo    ⚠️  Could not check disk space
)

echo.
echo ========================================
echo           Test Summary
echo ========================================
echo.
echo ✅ = Passed    ⚠️ = Warning    ❌ = Failed
echo.
echo If all tests pass, you can proceed with:
echo - Service installation: install_service.bat (as Administrator)
echo - Task Scheduler: create_task_scheduler.bat (as Administrator)
echo - Direct run: start_service.bat
echo.
echo For network access from other devices:
echo 1. Run setup_firewall.bat as Administrator
echo 2. Use start_global_access.bat for testing
echo 3. Access via: http://[YOUR-IP]
echo.
pause
goto :end

:error
echo.
echo ❌ Setup test failed. Please fix the issues above.
pause

:end 