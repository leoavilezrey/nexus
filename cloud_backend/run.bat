@echo off
echo Iniciando Nexus Cloud Backend (desarrollo local)...
echo.

cd /d %~dp0..
echo Directorio actual de trabajo de Uvicorn: %CD%

REM Verificar que existe el archivo .env de desarrollo
IF NOT EXIST cloud_backend\.env (
    echo ERROR: No se encontro el archivo .env
    echo Copia cloud_backend\.env.example como cloud_backend\.env y configura DATABASE_URL local
    pause
    exit /b 1
)
uvicorn cloud_backend.main:app --reload --port 8000
pause
