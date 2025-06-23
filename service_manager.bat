@echo off
title AI Chatbot Service Manager
color 0A

:menu
cls
echo ========================================
echo      AI Chatbot Service Manager
echo ========================================
echo.
echo 1. Install Service (NSSM)
echo 2. Uninstall Service (NSSM)
echo 3. Start Service
echo 4. Stop Service
echo 5. Restart Service
echo 6. Check Service Status
echo 7. View Service Logs
echo 8. Create Task Scheduler Entry
echo 9. Remove Task Scheduler Entry
echo A. Setup Firewall Rules
echo B. Test Network Access
echo 0. Exit
echo.
set /p choice="Enter your choice (0-9, A, B): "

if "%choice%"=="1" goto install_service
if "%choice%"=="2" goto uninstall_service
if "%choice%"=="3" goto start_service
if "%choice%"=="4" goto stop_service
if "%choice%"=="5" goto restart_service
if "%choice%"=="6" goto check_status
if "%choice%"=="7" goto view_logs
if "%choice%"=="8" goto create_task
if "%choice%"=="9" goto remove_task
if "%choice%"=="A" goto setup_firewall
if "%choice%"=="a" goto setup_firewall
if "%choice%"=="B" goto test_network
if "%choice%"=="b" goto test_network
if "%choice%"=="0" goto exit
goto menu

:install_service
cls
echo Installing Service...
call install_service.bat
pause
goto menu

:uninstall_service
cls
echo Uninstalling Service...
call uninstall_service.bat
pause
goto menu

:start_service
cls
echo Starting Service...
net start AIChatbotService
if %errorlevel% equ 0 (
    echo Service started successfully!
) else (
    echo Error starting service!
)
pause
goto menu

:stop_service
cls
echo Stopping Service...
net stop AIChatbotService
if %errorlevel% equ 0 (
    echo Service stopped successfully!
) else (
    echo Error stopping service!
)
pause
goto menu

:restart_service
cls
echo Restarting Service...
net stop AIChatbotService >nul 2>&1
timeout /t 2 /nobreak >nul
net start AIChatbotService
if %errorlevel% equ 0 (
    echo Service restarted successfully!
) else (
    echo Error restarting service!
)
pause
goto menu

:check_status
cls
echo Checking Service Status...
sc query AIChatbotService
pause
goto menu

:view_logs
cls
echo Service Logs:
echo ========================================
if exist "logs\service_output.log" (
    echo Output Log:
    type "logs\service_output.log"
    echo.
) else (
    echo No output log found.
)
if exist "logs\service_error.log" (
    echo Error Log:
    type "logs\service_error.log"
) else (
    echo No error log found.
)
pause
goto menu

:create_task
cls
echo Creating Task Scheduler Entry...
call create_task_scheduler.bat
pause
goto menu

:remove_task
cls
echo Removing Task Scheduler Entry...
call remove_task_scheduler.bat
pause
goto menu

:setup_firewall
cls
echo Setting up Firewall Rules...
call setup_firewall.bat
pause
goto menu

:test_network
cls
echo Testing Network Access...
call network_test.bat
pause
goto menu

:exit
echo Goodbye!
timeout /t 2 /nobreak >nul
exit