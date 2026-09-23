@echo off
title Conector WhatsApp Evolution API - Proteccion Civil
color 0A
cd /d "%~dp0"

echo ========================================================
echo   CONECTANDO CON EVOLUTION API (LAPTOP LOCAL)
echo ========================================================
echo.

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" generar_qr_interactivo.py
) else (
    python generar_qr_interactivo.py
)

pause
