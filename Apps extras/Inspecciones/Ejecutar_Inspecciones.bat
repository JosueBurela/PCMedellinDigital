@echo off
title Sistema de Inspecciones - Proteccion Civil
cd /d "%~dp0"

if exist "dist\Inspecciones_ProteccionCivil\Inspecciones_ProteccionCivil.exe" (
    start "" "dist\Inspecciones_ProteccionCivil\Inspecciones_ProteccionCivil.exe"
) else (
    python main.py
)
