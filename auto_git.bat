@echo off
cd /d "%~dp0"

:: ضبط هوية Git
git config user.name "Walid Chawakate"
git config user.email "youremail@example.com"

echo.
echo Adding changes...
git add .

echo.
set /p commitMsg=Enter commit message: 

:: التحقق مما إذا كانت هناك تغييرات للإرسال
git diff --cached --quiet
if %errorlevel%==0 (
    echo.
    echo No changes to commit. Skipping commit step.
) else (
    echo.
    echo Committing changes...
    git commit -m "%commitMsg%"
)

echo.
echo Pulling latest changes from GitHub...
git pull origin main --rebase

echo.
echo Pushing to GitHub (branch: main)...
git push origin main

echo.
echo ✅ Done.
pause