@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
title AgriVision Agent - Test Suite Execution
echo ======================================================================
echo [*] Running All AgriVision Agent Unit & Integration Tests...
echo ======================================================================
call "%~dp0.venv\Scripts\activate.bat"
"%~dp0.venv\Scripts\python.exe" -m pytest tests -v
pause

