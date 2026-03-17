@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: 🛣️ AutoRoads - One-Click Launcher
:: ============================================================
title AutoRoads AI Assistant

echo ============================================================
echo   🚀 Starting AutoRoads AI Assistant...
echo ============================================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH.
    echo Please install Python and try again.
    pause
    exit /b
)

:: 2. Launch X-Server (VcXsrv) if it exists
:: This is needed for the OpenROAD GUI to appear
if exist "C:\Program Files\VcXsrv\vcxsrv.exe" (
    echo 🎨 Starting X-Server (VcXsrv)...
    start "" "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac
) else (
    echo ⚠️  WARNING: VcXsrv (X-Server) not found in C:\Program Files\VcXsrv.
    echo Graphical layouts might not appear until you install it.
)

:: 3. Start the Backend in a separate window
:: (run.py will auto-install missing dependencies)
echo 🐍 Initializing Backend and Dependencies...
start "AutoRoads Backend" cmd /c "python run.py"

:: 4. Wait for server to initialize
echo ⏳ Waiting for server to start (5 seconds)...
timeout /t 5 /nobreak >nul

:: 5. Open the Web UI
echo 🌐 Opening Web Assistant at http://localhost:8000
start http://localhost:8000

echo ============================================================
echo   ✅ System Ready! 
echo   Keep the "AutoRoads Backend" window open.
echo ============================================================
pause
