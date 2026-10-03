@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
title AgriVision Agent - Zenze Web Platform
echo ======================================================================
echo [*] Launching AgriVision Agent Full-Stack Web Application...
echo ======================================================================
call "%~dp0.venv\Scripts\activate.bat"
start "" http://localhost:8000
"%~dp0.venv\Scripts\python.exe" app/server.py
pause
