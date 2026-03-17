@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: 🛡️ AutoRoads - Presentation Panic Shield
:: (Goes straight to Demo Mode - No WSL required)
:: ============================================================

title AutoRoads Presentation Mode
echo ============================================================
echo   🎭 ACTIVATING PRESENTATION SIMULATION MODE
echo   (Bypassing WSL checks for a smooth demo...)
echo ============================================================

:: 1. Start the AI Assistant in the background
echo 🐍 Initializing AI Assistant Dashboard...
start "AutoRoads Backend" cmd /c "python run.py"

:: 2. Show the "Rocket SoC" Design Flow Simulation
echo 🏗️ Starting TinyRocket Design Execution...
echo.
timeout /t 1 /nobreak >nul
echo [INFO] Loading Design: tinyRocket SoC...
echo [INFO] Found SRAM Macro Blocks: 42
timeout /t 2 /nobreak >nul
echo [INFO MPL-001] Macro placement successful.
echo [INFO MPL-002] Locked 42 instances at (X, Y) grid.
timeout /t 2 /nobreak >nul
echo [INFO GPL-001] Starting Global Placement...
echo [INFO GPL-004] Core area initialized: 500x500um.
timeout /t 2 /nobreak >nul
echo [INFO CTS-001] Clock placement complete. (WNS: 0.02ns)
echo [INFO GRT-001] Global route: 100%% Success.
echo.
echo ✅ [PRESENTATION MODE] CHIP GENERATION COMPLETE
echo.

:: 3. Open the Web Browser for the AI portion
echo 🌐 Opening AI Assistant at http://localhost:8000 ...
timeout /t 3 /nobreak >nul
start http://localhost:8000

echo ============================================================
echo   ✨ DEMO READY! 
echo   You can now show the AI Dashboard in the browser.
echo ============================================================
pause
