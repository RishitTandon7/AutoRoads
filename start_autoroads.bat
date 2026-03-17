@echo off

:: ============================================================
:: AutoRoads - One-Click Launcher (Robust Version)
:: ============================================================
title AutoRoads AI Assistant

echo ============================================================
echo   Starting AutoRoads AI Assistant...
echo ============================================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 goto :NO_PYTHON

:: 1b. Check for Git
git --version >nul 2>&1
if %errorlevel% neq 0 echo Warning: Git not found. Updates disabled.

:: 2. Launch X-Server (VcXsrv)
if not exist "C:\Program Files\VcXsrv\vcxsrv.exe" goto :NO_VCXSRV
echo Starting X-Server...
start "" "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac
goto :START_BACKEND

:NO_VCXSRV
echo Warning: VcXsrv not found. Graphical UI may not show.
goto :START_BACKEND

:START_BACKEND
echo Initializing Backend and Dependencies...
:: Using START to run python in a new window so logs are visible
start "AutoRoads Backend" cmd /c "python run.py"

:: 4. Wait for server
echo Waiting for server to start (5 seconds)...
timeout /t 5 /nobreak >nul

:: 5. Open Web UI
echo Opening Web Assistant...
start http://localhost:8000

echo ============================================================
echo   System Ready!
echo ============================================================
pause
exit /b

:NO_PYTHON
echo ERROR: Python is not installed.
echo Please run: winget install Python.Python.3.12
pause
exit /b
