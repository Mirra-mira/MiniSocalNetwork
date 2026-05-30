param(
    [string]$venvPath = "venv"
)

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "ERROR: venv not found at '$venvPath'" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
    exit 1
}

& $activateScript

Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "Server running at http://127.0.0.1:8000/index.html" -ForegroundColor Green
Write-Host ""

uvicorn app.main:app --reload
