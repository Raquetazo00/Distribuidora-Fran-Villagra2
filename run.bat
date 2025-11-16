@echo off
REM Script para ejecutar la aplicacion de Distribuidora
REM Windows PowerShell / CMD

echo ========================================
echo Sistema de Distribuidora Fran Villagra
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    echo Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detectado
echo.

REM Verificar si Kivy esta instalado
python -c "import kivy" >nul 2>&1
if errorlevel 1 (
    echo Instalando Kivy...
    pip install kivy
    if errorlevel 1 (
        echo ERROR: No se pudo instalar Kivy
        pause
        exit /b 1
    )
)

echo [OK] Kivy detectado
echo.

REM Verificar si la BD existe
if not exist "data\distribuidora.db" (
    echo Creando base de datos...
    python scripts/create_distribuidora_db.py
    if errorlevel 1 (
        echo ERROR: No se pudo crear la BD
        pause
        exit /b 1
    )
)

echo [OK] Base de datos lista
echo.

REM Ejecutar la aplicacion
echo Iniciando aplicacion...
echo.
python main.py

if errorlevel 1 (
    echo ERROR: Algo salio mal durante la ejecucion
    pause
    exit /b 1
)

exit /b 0
