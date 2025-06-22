@echo off
cd /d "%~dp0"

:: عرض المستخدم الحالي المستخدم في Git (للتأكيد)
echo -----------------------------------------------
echo 👤 المستخدم الحالي في Git:
git config user.name
git config user.email
echo -----------------------------------------------

:: ضبط معلومات الكوميت فقط (لا تؤثر على الحساب الفعلي للدفع)
git config user.name "oussama idiken"
git config user.email "chatbootprojet@gmail.com"

:: التحقق من عنوان الريبو (يفترض أنه SSH)
echo.
echo 🔍 التحقق من الريبو:
git remote -v

:: إضافة التعديلات
echo.
echo 📦 Adding changes...
git add .

:: طلب رسالة الكوميت
echo.
set /p commitMsg=✍️  Enter commit message: 

:: التحقق مما إذا كانت هناك تغييرات جاهزة للإرسال
git diff --cached --quiet
if %errorlevel%==0 (
    echo.
    echo ⚠️  No changes to commit. Skipping commit step.
) else (
    echo.
    echo ✅ Committing changes...
    git commit -m "%commitMsg%"
)

:: سحب آخر التحديثات من الريبو
echo.
echo 🔄 Pulling latest changes from GitHub...
git pull origin main --rebase

:: دفع التغييرات إلى الريبو
echo.
echo 🚀 Pushing to GitHub (branch: main)...
git push origin main

:: الانتهاء
echo.
echo 🎉 ✅ Done.
pause
