@echo off
echo Testing Network Access for AI Chatbot...
echo.

REM Get current IP address
echo 1. Getting current IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo    Local IP: !IP!
)

REM Enable delayed expansion for IP variable
setlocal enabledelayedexpansion

REM Show network interfaces
echo.
echo 2. Network interfaces:
ipconfig | findstr /c:"IPv4 Address"

REM Test if port 5000 is available
echo.
echo 3. Checking if port 5000 is available...
netstat -an | findstr :5000
if %errorlevel% neq 0 (
    echo    ✅ Port 5000 is available
) else (
    echo    ⚠️  Port 5000 is already in use
)

REM Check Windows Firewall status
echo.
echo 4. Checking Windows Firewall...
netsh advfirewall show allprofiles state | findstr "State"

REM Test if we can add firewall rule
echo.
echo 5. Testing firewall rule creation...
echo    Note: This requires Administrator privileges
netsh advfirewall firewall show rule name="AI Chatbot" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Firewall rule already exists
) else (
    echo    ⚠️  Firewall rule does not exist
    echo    To create it, run as Administrator:
    echo    netsh advfirewall firewall add rule name="AI Chatbot" dir=in action=allow protocol=TCP localport=5000
)

echo.
echo ========================================
echo           Network Access Summary
echo ========================================
echo.
echo To access from other devices on your network:
echo   http://[YOUR-IP]:5000
echo.
echo Common IP addresses to try:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo   http://!IP!:5000
)

echo.
echo If you can't access from other devices:
echo 1. Make sure Windows Firewall allows port 5000
echo 2. Check your router/network settings
echo 3. Make sure the service is running
echo.
pause 