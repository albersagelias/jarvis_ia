@echo off
REM Instalador de Jarvis para Windows: haz doble clic en este archivo.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_windows.ps1"
echo.
pause
