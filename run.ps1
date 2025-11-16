# Script para ejecutar la aplicacion de Distribuidora
# PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Sistema de Distribuidora Fran Villagra" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python esta instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no esta instalado o no esta en PATH" -ForegroundColor Red
    Write-Host "Descarga desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Verificar si Kivy esta instalado
try {
    python -c "import kivy" 2>$null
    Write-Host "[OK] Kivy detectado" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Instalando Kivy..." -ForegroundColor Yellow
    pip install kivy
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] No se pudo instalar Kivy" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}

Write-Host ""

# Verificar si la BD existe
$dbPath = "data\distribuidora.db"
if (-not (Test-Path $dbPath)) {
    Write-Host "[INFO] Creando base de datos..." -ForegroundColor Yellow
    python scripts/create_distribuidora_db.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] No se pudo crear la BD" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}

Write-Host "[OK] Base de datos lista" -ForegroundColor Green
Write-Host ""

# Ejecutar la aplicacion
Write-Host "Iniciando aplicacion..." -ForegroundColor Cyan
Write-Host ""

python main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Algo salio mal durante la ejecucion" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

exit 0
