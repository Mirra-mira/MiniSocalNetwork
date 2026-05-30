param(
    [string]$venvPath = "venv"
)

if (-not (Test-Path $venvPath)) {
    Write-Host "Tạo virtual environment tại '$venvPath'..."
    python -m venv $venvPath
}

$python = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Không tìm thấy Python trong venv. Đảm bảo virtualenv đã được tạo thành công."
}

Write-Host "Sử dụng Python: $python"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt
Write-Host "Cài đặt xong."