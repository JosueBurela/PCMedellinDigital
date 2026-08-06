@echo off
title Servidor PCivil Digital
color 05
echo ===================================================================
echo     INICIANDO SERVIDOR DE PROTECCION CIVIL DIGITAL - MEDELLIN
echo ===================================================================
echo.
echo 1. Activando entorno de desarrollo de Django...
echo 2. Levantando base de datos relacional y servidor local...
echo.
echo [RED LOCAL] Accesible en tu red local desde: http://192.168.1.104:8000/
echo [ATENCION] Deja esta ventana abierta para mantener el sistema activo.
echo [ATENCION] Presiona CTRL+C en esta consola si deseas apagar el servidor.
echo.

:: Lanzar el servidor en segundo plano de la consola para ver los logs en vivo
:: Bindeado a 0.0.0.0:8000 para habilitar acceso desde red local
start "" /B venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

:: Esperar 2 segundos para dar tiempo a que Django inicialice la conexión
timeout /t 2 >nul

echo.
echo 3. Abriendo el Portal de Protección Civil en tu navegador...
start http://127.0.0.1:8000/
echo.
echo [LISTO] Servidor activo localmente en http://127.0.0.1:8000/
echo ===================================================================
echo.

:: Mantener la consola viva para mostrar la bitácora de peticiones http
pause >nul
