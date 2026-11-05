# run_backend_online.ps1 - Khởi động Backend + Mở đường hầm Cloudflare Tunnel công khai
$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " KHỞI ĐỘNG BACKEND + CLOUDFLARE TUNNEL (KẾT NỐI VỚI VERCEL) - PTIT" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Kiểm tra môi trường Python
$pythonPath = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "[ERROR] Không tìm thấy môi trường ảo tại .venv. Vui lòng tạo venv trước." -ForegroundColor Red
    exit 1
}

# 2. Đảm bảo có công cụ cloudflared.exe
$cloudflaredPath = ".\tools\cloudflared.exe"
if (-not (Test-Path $cloudflaredPath)) {
    Write-Host "[1/4] Đang tải công cụ Cloudflare Tunnel tự động..." -ForegroundColor Yellow
    if (!(Test-Path "tools")) { New-Item -ItemType Directory -Path "tools" | Out-Null }
    curl.exe -L -o $cloudflaredPath "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
}

# 3. Kiểm tra xem Backend đã chạy chưa, nếu chưa thì khởi động
$backendAlreadyRunning = $false
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -Method Get -TimeoutSec 1
    if ($resp.status -eq "healthy") {
        $backendAlreadyRunning = $true
        Write-Host "[2/4] Backend FastAPI đã chạy sẵn tại cổng 8000." -ForegroundColor Green
    }
} catch {}

$backendProcess = $null
if (-not $backendAlreadyRunning) {
    Write-Host "[2/4] Đang khởi động Backend FastAPI (Port 8000)..." -ForegroundColor Yellow
    $backendProcess = Start-Process -FilePath $pythonPath -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--port", "8000", "--host", "127.0.0.1" -PassThru

    $maxRetries = 20
    $retries = 0
    $backendReady = $false
    while (-not $backendReady -and $retries -lt $maxRetries) {
        Start-Sleep -Seconds 1
        $retries++
        try {
            $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -Method Get -TimeoutSec 2
            if ($resp.status -eq "healthy") {
                $backendReady = $true
                Write-Host "     Backend đã sẵn sàng!" -ForegroundColor Green
            }
        } catch {
            Write-Host "     Đang nạp mô hình AI... ($retries/$maxRetries)" -ForegroundColor Gray
        }
    }

    if (-not $backendReady) {
        Write-Host "[WARNING] Backend chưa phản hồi, nhưng vẫn thử mở tunnel..." -ForegroundColor Yellow
    }
}

# 4. Khởi động Cloudflare Tunnel và trích xuất URL
Write-Host "[3/4] Đang thiết lập đường hầm bảo mật Cloudflare Tunnel..." -ForegroundColor Yellow

$tunnelLog = "$PSScriptRoot\tools\tunnel.log"
if (Test-Path $tunnelLog) { Remove-Item $tunnelLog -Force }

$tunnelProcess = Start-Process -FilePath $cloudflaredPath -ArgumentList "tunnel", "--url", "http://127.0.0.1:8000" -RedirectStandardError $tunnelLog -PassThru -WindowStyle Hidden

$tunnelUrl = $null
$retries = 0
while (-not $tunnelUrl -and $retries -lt 30) {
    Start-Sleep -Seconds 1
    $retries++
    if (Test-Path $tunnelLog) {
        $content = Get-Content $tunnelLog -Raw -ErrorAction SilentlyContinue
        if ($content -match 'https://[a-zA-Z0-9-]+\.trycloudflare\.com') {
            $tunnelUrl = $matches[0]
        }
    }
}

if ($tunnelUrl) {
    try { Set-Clipboard $tunnelUrl } catch {}
    Write-Host "`n======================================================================" -ForegroundColor Green
    Write-Host " 🎉 ĐƯỜNG HẦM CLOUDFLARE ĐÃ KẾT NỐI THÀNH CÔNG!" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "🔗 URL BACKEND CỦA BẠN: " -NoNewline
    Write-Host "$tunnelUrl" -ForegroundColor Cyan -BackgroundColor Black
    Write-Host "   (👉 Đã tự động sao chép vào Clipboard của bạn!)" -ForegroundColor Yellow
    Write-Host "`nCÁCH DÁN VÀO VERCEL:" -ForegroundColor White
    Write-Host " 1. Vào Vercel -> Chọn dự án -> Settings -> Environment Variables" -ForegroundColor Gray
    Write-Host " 2. Đặt VITE_API_BASE_URL = $tunnelUrl" -ForegroundColor Gray
    Write-Host " 3. Vào tab Deployments -> Bấm nút ... -> Chọn Redeploy" -ForegroundColor Gray
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "`nĐang giữ kết nối... Nhấn Ctrl+C để dừng." -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Không thể lấy URL từ Cloudflare Tunnel. Vui lòng kiểm tra $tunnelLog" -ForegroundColor Red
}

try {
    while ($true) {
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "`nĐang đóng đường hầm Cloudflare..." -ForegroundColor Yellow
    if ($tunnelProcess -and -not $tunnelProcess.HasExited) {
        Stop-Process -Id $tunnelProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Write-Host "Đang tắt Backend FastAPI..." -ForegroundColor Yellow
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Đã dừng hệ thống thành công." -ForegroundColor Green
}
