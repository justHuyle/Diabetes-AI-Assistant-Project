# run_app.ps1 - Khởi động toàn bộ Hệ đa agent (Backend + Frontend) bằng một lệnh duy nhất
$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " HỆ ĐA AGENT HỖ TRỢ TƯ VẤN TIỂU ĐƯỜNG - PTIT" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Kiểm tra môi trường Python
$pythonPath = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "[ERROR] Không tìm thấy môi trường ảo tại .venv. Vui lòng tạo venv trước." -ForegroundColor Red
    exit 1
}

# 2. Khởi động Backend FastAPI
Write-Host "[1/3] Đang khởi động Backend FastAPI (Port 8000)..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath $pythonPath -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--port", "8000", "--host", "127.0.0.1" -PassThru

# 3. Đợi Backend sẵn sàng
$maxRetries = 15
$retries = 0
$backendReady = $false
while (-not $backendReady -and $retries -lt $maxRetries) {
    Start-Sleep -Seconds 1
    $retries++
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -Method Get -TimeoutSec 2
        if ($resp.status -eq "healthy") {
            $backendReady = $true
            Write-Host "[2/3] Backend đã sẵn sàng! (Trạng thái: $($resp.status))" -ForegroundColor Green
        }
    } catch {
        Write-Host "Đang đợi backend nạp các mô hình... ($retries/$maxRetries)" -ForegroundColor Gray
    }
}

if (-not $backendReady) {
    Write-Host "[WARNING] Backend chưa phản hồi kịp thời, vui lòng kiểm tra log." -ForegroundColor Yellow
}

# 4. Khởi động Frontend Vite
Write-Host "[3/3] Đang khởi động Frontend Vite (Port 5173)..." -ForegroundColor Yellow
Write-Host "Truy cập ứng dụng tại: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Nhấn Ctrl+C để dừng hệ thống." -ForegroundColor Gray

try {
    Set-Location frontend
    npm run dev
} finally {
    Write-Host "`nĐang dọn dẹp tiến trình backend..." -ForegroundColor Yellow
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Đã tắt hệ thống." -ForegroundColor Green
}
