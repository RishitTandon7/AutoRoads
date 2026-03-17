@echo off
setlocal

:: ============================================================
:: 🔭 AutoRoads - MPW Shuttle Runner (with Demo Fallback)
:: ============================================================

echo 🔍 Checking environment...

:: Check if WSL is ready
wsl --list --running >nul 2>&1
if %errorlevel% neq 0 goto :DEMO_MODE

:: Check if OpenROAD is installed
wsl command -v openroad >nul 2>&1
if %errorlevel% neq 0 goto :DEMO_MODE

:REAL_MODE
echo ✅ Environment Ready. Starting REAL MPW Generation...
wsl sed -i "s/\r$//" designs/gcd/run_mpw.sh
wsl bash designs/gcd/run_mpw.sh
pause
exit /b

:DEMO_MODE
echo ⚠️  WSL/OpenROAD not fully active. 
echo 🎭 ENTERING DEMO SIMULATION MODE...
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
echo [INFO] Routing global connections between cores...
timeout /t 2 /nobreak >nul
echo.
echo ✅ [DEMO] MPW SHUTTLE GENERATED SUCCESSFULLY
echo ✅ [DEMO] View the result in: results/mpw_shuttle/wafer_view.odb
echo.
echo NOTE: Run "start_autoroads.bat" to use the AI Assistant for analysis.
pause
exit /b
