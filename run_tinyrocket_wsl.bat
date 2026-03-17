@echo off
setlocal

:: ============================================================
:: 🚀 AutoRoads - TinyRocket WSL Runner
:: Fixes line endings and executes the full flow
:: ============================================================

echo 🧹 Cleaning line endings for WSL compatibility...
wsl sed -i "s/\r$//" designs/gcd/setup_and_run.sh
wsl sed -i "s/\r$//" designs/gcd/run_mpw.sh

echo 🏗️ Starting Full Chip Flow (TinyRocket)...
wsl bash designs/gcd/setup_and_run.sh

pause
