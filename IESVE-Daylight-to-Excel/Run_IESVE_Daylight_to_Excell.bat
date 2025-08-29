@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ==================================================================
REM  IESVE Daylight Metrics -> Excel : FINAL (Same-Window, DIAG-style)
REM  - No 'start', no 'pythonw'.
REM  - Runs in this window so it cannot auto-close.
REM  - Creates/uses .venv_daylight_excel and installs deps.
REM ==================================================================

REM Change directory to the location of this batch file
cd /d "%~dp0"

set "SCRIPT_NAME=IESVE_Dayilght_Metrics_to_Excel.py"
set "SCRIPT_PATH=%~dp0%SCRIPT_NAME%"
set "VENV_PATH=%~dp0.venv_daylight_excel"
set "PY_EXE=%VENV_PATH%\Scripts\python.exe"
set "REQ_FILE=%~dp0requirements.txt"

echo [INFO] Working Directory: "%CD%"
echo [INFO] Script Path: "%SCRIPT_PATH%"
echo [INFO] Virtual Env Path: "%VENV_PATH%"

if not exist "%SCRIPT_PATH%" (
  echo [ERROR] Script not found: "%SCRIPT_PATH%"
  goto :END
)

REM ---- Find a suitable Python interpreter ----
set "PY_CMD="
where py >nul 2>nul && set "PY_CMD=py -3"
if not defined PY_CMD ( where python >nul 2>nul && set "PY_CMD=python" )

if not defined PY_CMD (
  echo [ERROR] Python 3.10+ not found on your system's PATH.
  echo [ERROR] Please install Python from python.org and ensure "Add to PATH" is checked during installation.
  goto :END
)
echo [INFO] Found Python launcher: %PY_CMD%

REM ---- Create virtual environment if it doesn't exist ----
if not exist "%PY_EXE%" (
  echo [INFO] Creating virtual environment...
  %PY_CMD% -m venv "%VENV_PATH%"
  if %errorlevel% neq 0 (
    echo [ERROR] Failed to create the virtual environment.
    goto :END
  )
)

REM ---- Install/update Python packages ----
echo [INFO] Installing/updating required packages...
if exist "%REQ_FILE%" (
  "%PY_EXE%" -m pip install --upgrade pip
  "%PY_EXE%" -m pip install -r "%REQ_FILE%"
) else (
  echo [INFO] 'requirements.txt' not found. Installing base packages...
  "%PY_EXE%" -m pip install --upgrade pip
  "%PY_EXE%" -m pip install pandas openpyxl
)

if %errorlevel% neq 0 (
  echo [ERROR] Failed to install Python packages. Check your internet connection and package names.
  goto :END
)

echo [INFO] Launching the Python application...
"%PY_EXE%" -u "%SCRIPT_PATH%"
set "RC=%errorlevel%"
echo [INFO] Python script finished with exit code: %RC%

:END
echo.
echo -------------------------------------------------------------
echo Finished. Please review any messages above.
echo Press any key to close this window...
echo -------------------------------------------------------------
pause >nul
endlocal