@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Please run setup_windows.bat first.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" popup_clicker.py
pause
