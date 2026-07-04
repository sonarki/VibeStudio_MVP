@echo off
rem ASCII-only bootstrap. All logic lives in start-jarbiseo.ps1
rem (PowerShell handles Korean text and errors much more reliably than cmd).
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-jarbiseo.ps1"
pause
