@echo off
title AgriVision Agent - Live GPU Crop Training
cd /d "c:\Projects\AgriVision Agent"
powershell.exe -NoProfile -ExecutionPolicy Bypass -NoExit -File "c:\Projects\AgriVision Agent\run_live_training.ps1"
pause

