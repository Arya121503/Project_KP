@echo off
echo ================================================================
echo        TELKOM PROPERTY PREDICTION SYSTEM - QUICK START
echo ================================================================
echo.

:: Pindah ke direktori script
cd /d "%~dp0"

:: Cek apakah Python terinstall
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python terlebih dahulu dari https://python.org
    pause
    exit /b 1
)

:: Cek apakah virtual environment ada
if not exist ".venv" (
    echo [INFO] Membuat virtual environment...
    python -m venv .venv
)

:: Aktivasi virtual environment
echo [INFO] Mengaktifkan virtual environment...
call .venv\Scripts\activate.bat

:: Install dependencies
echo [INFO] Menginstall dependencies...
pip install -r requirements.txt

:: Jalankan launcher
echo [INFO] Menjalankan sistem...
python launcher.py

pause
