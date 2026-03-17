@echo off
setlocal

:: ============================================================
:: 🔭 AutoRoads - MPW Shuttle (Wafer View) Runner
:: ============================================================

echo 🧹 Cleaning line endings...
wsl sed -i "s/\r$//" designs/gcd/run_mpw.sh

echo 🎲 Starting MPW Shuttle Wafer Generation...
wsl bash designs/gcd/run_mpw.sh

pause
