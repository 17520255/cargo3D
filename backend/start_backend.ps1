Write-Host "Starting Cargo Backend Server..." -ForegroundColor Green
Write-Host ""

# Kích hoạt virtual environment
& .\.venv\Scripts\Activate.ps1

# Chạy server
python run_server.py 