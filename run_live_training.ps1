# AgriVision Agent: Live Stepwise GPU Training Runner
$Host.UI.RawUI.WindowTitle = "AgriVision Agent - Live GPU Stepwise Crop Training"

Write-Host "================================================================================" -ForegroundColor Green
Write-Host "[*] AGRIVISION AGENT: LIVE GPU STEPWISE CROP TRAINING" -ForegroundColor Yellow
Write-Host "[*] Hardware: NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA 12.1 + PyTorch)" -ForegroundColor Cyan
Write-Host "[*] Curriculum: 6 Crops x 22 Haryana Districts" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""

Set-Location "c:\Projects\AgriVision Agent"

$pythonPath = "c:\Projects\AgriVision Agent\.venv\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    Write-Host "[!] Virtual environment python not found at $pythonPath" -ForegroundColor Red
    Pause
    exit 1
}

$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "[+] Testing PyTorch CUDA GPU Detection..." -ForegroundColor Gray
& $pythonPath -c "import torch; print('>>> PyTorch:', torch.__version__, '| CUDA Available:', torch.cuda.is_available(), '| Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "[+] STARTING STEPWISE TRAINING ONE BY ONE ACROSS ALL 6 HARYANA CROPS" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""

& $pythonPath "src\models\haryana_stepwise_gpu_trainer.py" --step all --epochs 3

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "[+] ALL 6 HARYANA CROP STEPS COMPLETED ON GPU!" -ForegroundColor Green
Write-Host "[+] Checkpoints saved in: models\haryana_checkpoints\" -ForegroundColor Cyan
Write-Host "[+] Unified Model in:     models\haryana_models\" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host

