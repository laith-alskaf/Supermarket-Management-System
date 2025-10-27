@echo off
chcp 65001 > nul
title بناء ملف exe قابل للتشغيل

echo ====================================
echo   بناء ملف EXE للبرنامج
echo ====================================
echo.

REM تثبيت PyInstaller
echo جاري تثبيت PyInstaller...
pip install pyinstaller

echo.
echo جاري بناء ملف EXE...
echo هذه العملية قد تستغرق عدة دقائق...
echo.

REM بناء الملف
pyinstaller --onefile --windowed --icon=NONE --name="SuperMarket" main.py

echo.
if exist "dist\SuperMarket.exe" (
    echo [✓] تم بناء الملف بنجاح!
    echo.
    echo ستجد الملف في مجلد: dist\SuperMarket.exe
    echo.
    echo يمكنك نسخ هذا الملف وتشغيله على أي جهاز Windows
    echo بدون الحاجة لتثبيت Python
    echo.
    echo ملاحظة مهمة: يجب نسخ مجلد database معه إذا كانت لديك بيانات
) else (
    echo [✗] فشل بناء الملف
    echo يرجى التحقق من الأخطاء أعلاه
)

echo.
pause
