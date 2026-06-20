@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -m venv .venv
) else (
  python -m venv .venv
)

if not exist ".venv\Scripts\python.exe" (
  echo Failed to create virtual environment.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
".venv\Scripts\python.exe" -m playwright install chromium
".venv\Scripts\python.exe" -m pytest -q

echo.
echo Setup complete. Run run_windows.bat to start.
pause
