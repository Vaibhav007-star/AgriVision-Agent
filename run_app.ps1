# AgriVision Agent - PowerShell Web Launcher
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "======================================================================" -ForegroundColor Green
Write-Host "[*] Launching AgriVision Agent Web & Mobile PWA Application..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Green

$PythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "[!] Virtual environment not found at: $PythonExe" -ForegroundColor Red
    Write-Host "[!] Please ensure .venv is installed." -ForegroundColor Yellow
    exit 1
}

# Open browser to local web portal after server starts up
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000"
} | Out-Null

# Execute server with UTF-8 encoding
& $PythonExe (Join-Path $ScriptDir "app\server.py")

