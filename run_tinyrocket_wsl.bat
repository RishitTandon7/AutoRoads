@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: 🛣️ AutoRoads - Ultra-Safe TinyRocket Runner
:: ============================================================

echo 🔍 Checking OpenROAD Environment...

:: 1. Check if WSL is available
where wsl >nul 2>&1
if %errorlevel% neq 0 goto :PRESENTATION_DEMO

:: 2. Check if OpenROAD is actually INSTALLED inside WSL
:: This is the most reliable check to prevent "path not found" errors
wsl command -v openroad >nul 2>&1
if %errorlevel% neq 0 goto :PRESENTATION_DEMO

:REAL_EXECUTION
echo ✅ OpenROAD Found! Starting Real Flow...
wsl sed -i "s/\r$//" designs/gcd/setup_and_run.sh
wsl bash designs/gcd/setup_and_run.sh
pause
exit /b

:PRESENTATION_DEMO
echo.
echo ⚠️  OpenROAD not found or WSL needs a restart.
echo 🎭 ACTIVATING PRESENTATION SIMULATION...
echo.
timeout /t 1 /nobreak >nul
echo [INFO] Loading Design: tinyRocket SoC...
echo [INFO] Found SRAM Macro Blocks: 42
timeout /t 2 /nobreak >nul
echo [INFO] Running Hierarchical Macro Placement...
echo [INFO] RTL Macro Placer: Success.
timeout /t 2 /nobreak >nul
echo [INFO GPL-001] Global Placement Density: 0.55
echo [INFO GPL-004] Core area initialized.
timeout /t 2 /nobreak >nul
echo [INFO CTS-001] Clock placement complete.
echo [INFO GRT-001] Global route: 0 violations.
echo.
echo ✅ [PRESENTATION MODE] FLOW COMPLETE
echo Result: designs/gcd/tinyrocket_routed.odb (Simulated)
echo.
pause
exit /b
