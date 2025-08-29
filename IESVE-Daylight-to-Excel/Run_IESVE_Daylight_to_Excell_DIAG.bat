@echo on
setlocal EnableExtensions EnableDelayedExpansion

REM ==================================================================
REM  IESVE Daylight Metrics -> Excel : DIAG Runner (separate cmd /k)
REM  - Spawns a NEW console window that will NOT close automatically.
REM  - Shows all stdout/stderr live (no redirection).
REM ==================================================================

cd /d "%~dp0"

set "SCRIPT_NAME=IESVE_Dayilght_Metrics_to_Excel.py"
set "SCRIPT=%CD%\%SCRIPT_NAME%"
set "VENV=%CD%\.venv_daylight_excel"
set "PYEXE=%VENV%\Scripts\python.exe"
set "REQ=%CD%\requirements.txt"

echo [INFO] CWD=%CD%
echo [INFO] SCRIPT=%SCRIPT%

if not exist "%SCRIPT%" (
  echo [ERROR] Script not found: "%SCRIPT%"
  pause
  exit /b 1
)

set "PY_CMD="
where py >nul 2>nul && set "PY_CMD=py -3"
if not defined PY_CMD ( where python >nul 2>nul && set "PY_CMD=python" )
if not defined PY_CMD (
  echo [ERROR] Python 3.10+ not found on PATH.
  pause
  exit /b 1
)

if not exist "%PYEXE%" (
  echo [INFO] Creating venv ...
  %PY_CMD% -m venv "%VENV%"
  if errorlevel 1 ( echo [ERROR] venv creation failed. & pause & exit /b 1 )
  "%PYEXE%" -m pip install --upgrade pip
  if exist "%REQ%" (
    "%PYEXE%" -m pip install -r "%REQ%"
  ) else (
    "%PYEXE%" -m pip install pandas openpyxl
  )
)

echo [INFO] Launching in a NEW window that stays open...
start "IESVE Daylight -> Excel (DIAG)" cmd /k ^
    ""%PYEXE%" "%SCRIPT%" ^& echo. ^& echo [INFO] Script finished. Press any key to close... ^& pause"
exit /b 0
