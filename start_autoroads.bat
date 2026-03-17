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
    echo ❌ ERROR: Python is not installed.
    echo Fast install: winget install Python.Python.3.12
    pause
    exit /b
)

:: 1b. Check for Git (Optional but helpful)
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: Git is not installed. You won't be able to update from GitHub.
    echo Fast install: winget install Git.Git
)

:: 2. Launch X-Server (VcXsrv) if it exists
if exist "C:\Program Files\VcXsrv\vcxsrv.exe" (
    echo 🎨 Starting X-Server (VcXsrv)...
    start "" "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac
) else (
    echo ⚠️  WARNING: VcXsrv (X-Server) not found.
)

:: 3. Start the Backend
start "AutoRoads Backend" cmd /c "python run.py"

:: 4. Wait for server
timeout /t 5 /nobreak >nul

:: 5. Open Web UI
start http://localhost:8000

echo ✅ System Ready!
pause
