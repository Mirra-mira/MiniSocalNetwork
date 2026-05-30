param(
    [string]$venvPath = "venv"
)

Write-Host "========== MINI SOCIAL NETWORK - SETUP ==========" -ForegroundColor Green

# Tao venv
if (-not (Test-Path $venvPath)) {
    Write-Host "Tao virtual environment tai '$venvPath'..." -ForegroundColor Cyan
    python -m venv $venvPath
    Write-Host "OK - Tao venv thanh cong" -ForegroundColor Green
} else {
    Write-Host "OK - Virtual environment da ton tai" -ForegroundColor Green
}

# Kich hoat venv
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    throw "Khong tim thay Activate.ps1 trong venv"
}

Write-Host "Kich hoat venv..." -ForegroundColor Cyan
& $activateScript

# Cai dependency
Write-Host "Cap nhat pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host "Cai dependency tu requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt
Write-Host "OK - Cai dependency xong" -ForegroundColor Green

Write-Host ""
Write-Host "========== SETUP HOAN TAT ==========" -ForegroundColor Green
Write-Host "Tiep theo:"
Write-Host "  1. Dam bao PostgreSQL dang chay"
Write-Host "  2. Chay: createdb mini_social"
Write-Host "  3. Copy .env.example -> .env va chinh DATABASE_URL"
Write-Host "  4. Chay migration: psql -f migrations/001_init.sql"
Write-Host "  5. Chay ung dung: .\run.ps1"
Write-Host ""
