@echo off
echo Setting up Windows Firewall for AI Chatbot...

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo Adding firewall rules for AI Chatbot on port 80...

REM Remove existing rules first
echo Removing existing rules...
netsh advfirewall firewall delete rule name="AI Chatbot" >nul 2>&1
netsh advfirewall firewall delete rule name="AI Chatbot - Inbound" >nul 2>&1
netsh advfirewall firewall delete rule name="AI Chatbot - Outbound" >nul 2>&1

REM Add inbound rule for port 80
echo Adding inbound rule for port 80...
netsh advfirewall firewall add rule name="AI Chatbot - Inbound" dir=in action=allow protocol=TCP localport=80

REM Add outbound rule for port 80 (optional but recommended)
echo Adding outbound rule for port 80...
netsh advfirewall firewall add rule name="AI Chatbot - Outbound" dir=out action=allow protocol=TCP localport=80

REM Show the created rules
echo.
echo Created firewall rules:
netsh advfirewall firewall show rule name="AI Chatbot - Inbound"
echo.
netsh advfirewall firewall show rule name="AI Chatbot - Outbound"

echo.
echo ========================================
echo        Firewall Setup Complete
echo ========================================
echo.
echo AI Chatbot is now accessible from:
echo - Local machine: http://localhost
echo - Network devices: http://[YOUR-IP]
echo - Internet: http://[YOUR-PUBLIC-IP] (if router configured)
echo.
echo To find your IP address, run: ipconfig
echo.
pause 