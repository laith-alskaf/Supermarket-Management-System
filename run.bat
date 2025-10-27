@echo off
chcp 65001 > nul
title نظام إدارة السوبر ماركت

echo ====================================
echo   نظام إدارة السوبر ماركت
echo ====================================
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [خطأ] Python غير مثبت على جهازك
    echo يرجى تحميل Python من https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [✓] Python مثبت

REM تثبيت المكتبات إذا لزم الأمر
echo.
echo جاري التحقق من المكتبات المطلوبة...
pip install -r requirements.txt --quiet

echo.
echo [✓] جاري تشغيل البرنامج...
echo.

REM تشغيل البرنامج
python main.py

echo.
echo تم إغلاق البرنامج
pause
