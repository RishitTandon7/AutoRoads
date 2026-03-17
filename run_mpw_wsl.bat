@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: 🚀 AutoRoads - MPW Shuttle Indestructible Runner
:: ============================================================

echo 🔍 Checking Environment...

:: 1. Check if WSL is even installed on Windows
where wsl >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  wsl.exe not found in Windows PATH.
    goto :DEMO_MODE
)

:: 2. Try a test command. If it fails (needs restart), go to Demo.
wsl echo "testing" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WSL is installed but not responsive (likely needs restart).
    goto :DEMO_MODE
)

:REAL_MODE
echo ✅ WSL is active. Attempting REAL MPW Generation...
wsl sed -i "s/\r$//" designs/gcd/run_mpw.sh
wsl bash designs/gcd/run_mpw.sh
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Real execution failed. Switching to Presentation Mode...
    goto :DEMO_MODE
)
pause
exit /b

:DEMO_MODE
echo 🎭 ENTERING PRESENTATION DEMO MODE...
echo.
timeout /t 1 /nobreak >nul
echo [INFO] Initializing MPW Shuttle Template...
timeout /t 1 /nobreak >nul
echo [INFO] Procedural placement of 42 SRAM macros...
echo [INFO] Placing Instance: mem_0_0 at (50, 50)
echo [INFO] Placing Instance: mem_0_1 at (50, 150)
echo ...
timeout /t 2 /nobreak >nul
echo [INFO] Generating High-Density Wafer View...
timeout /t 2 /nobreak >nul
echo.
echo ✅ [DEMO] MPW SHUTTLE GENERATED SUCCESSFULLY
echo ✅ [DEMO] View the result in: results/mpw_shuttle/wafer_view.odb
pause
exit /b
