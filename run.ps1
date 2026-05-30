param(
    [string]$venvPath = "venv"
)

Write-Host "Kích hoạt virtual environment..." -ForegroundColor Cyan
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "ERROR: Không tìm thấy venv tại '$venvPath'" -ForegroundColor Red
    Write-Host "Hãy chạy setup.ps1 trước" -ForegroundColor Yellow
    exit 1
}

& $activateScript

Write-Host "Chạy FastAPI server..." -ForegroundColor Green
Write-Host "🚀 Server đang chạy tại http://127.0.0.1:8000/index.html" -ForegroundColor Green
Write-Host ""

uvicorn app.main:app --reload
