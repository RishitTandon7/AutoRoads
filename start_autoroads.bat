@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: 🛣️ AutoRoads - Universal AI & Flow Launcher
:: (With 3-Second Demo Override)
:: ============================================================
title AutoRoads AI Assistant

:MENU
cls
echo ============================================================
echo   🛣️  AUTOROADS AI ASSISTANT MENU
echo ============================================================
echo   1. Start AI Assistant (Dashboard + Chat)
echo   2. Run TinyRocket SoC Flow (Real/Demo)
echo   3. Run MPW Wafer Flow (Real/Demo)
echo   4. [SAFE] Start Everything in PRESENTATION MODE
echo   5. Exit
echo ============================================================
set /p opt="Select an option (1-5): "

if "%opt%"=="1" goto :START_AI
if "%opt%"=="2" goto :RUN_TINY
if "%opt%"=="3" goto :RUN_MPW
if "%opt%"=="4" goto :SAFE_MODE
if "%opt%"=="5" exit

:START_AI
start "AutoRoads Backend" cmd /c "python run.py"
timeout /t 3 /nobreak >nul
start http://localhost:8000
goto :MENU

:RUN_TINY
echo 🔍 Checking OpenROAD... (Press 'D' within 3 seconds to skip to DEMO)
choice /c RD /t 3 /d R /n /m ""
if %errorlevel% equ 2 goto :DEMO_TINY
wsl command -v openroad >nul 2>&1
if %errorlevel% neq 0 goto :DEMO_TINY
wsl bash designs/gcd/setup_and_run.sh
pause
goto :MENU

:DEMO_TINY
echo 🎭 LOADING TINYROCKET DEMO...
timeout /t 1 /nobreak
echo [INFO] Floorplan -> Place -> Route...
echo ✅ [DEMO] Flow successful!
echo 🎨 Launching Visualizer (GUI)...
timeout /t 2 /nobreak >nul
start "" "%~dp0frontend\openroad_gui.html"
pause
goto :MENU

:RUN_MPW
echo 🔍 Checking OpenROAD... (Press 'D' within 3 seconds for DEMO)
choice /c RD /t 3 /d R /n /m ""
if %errorlevel% equ 2 goto :DEMO_MPW
wsl command -v openroad >nul 2>&1
if %errorlevel% neq 0 goto :DEMO_MPW
wsl bash designs/gcd/run_mpw.sh
pause
goto :MENU

:DEMO_MPW
echo 🎭 LOADING MPW WAFER DEMO...
echo ✅ [DEMO] Wafer simulation successful!
echo 🎨 Launching Visualizer (GUI)...
timeout /t 2 /nobreak >nul
start "" "%~dp0frontend\openroad_gui.html"
pause
goto :MENU

:SAFE_MODE
start "AutoRoads Backend" cmd /c "python run.py"
echo 🎭 Launching FULL SIMULATION...
timeout /t 1 /nobreak
echo ✅ SoC Simulation: Done.
echo ✅ Wafer Simulation: Done.
start http://localhost:8000
echo 🎨 Launching Visualizer (GUI)...
timeout /t 2 /nobreak >nul
start "" "%~dp0frontend\openroad_gui.html"
pause
goto :MENU
