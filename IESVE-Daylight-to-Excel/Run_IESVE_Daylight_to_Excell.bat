@echo off
setlocal EnableExtensions

REM ------------------------------------------------------------------
REM  IESVE Daylight Metrics → Excel launcher
REM  - Creates a local virtual environment on first run
REM  - Installs required packages
REM  - Launches the GUI
REM ------------------------------------------------------------------

REM Resolve script directory (with trailing backslash)
set "SCRIPT_DIR=%~dp0"
set "VENV=%SCRIPT_DIR%.venv"
set "PYEXE=%VENV%\Scripts\python.exe"
set "REQUIREMENTS=%SCRIPT_DIR%requirements.txt"
set "APP=%SCRIPT_DIR%IESVE_Dayilght_Metrics_to_Excel.py"

if not exist "%APP%" (
  echo [ERROR] Could not find "%APP%". Make sure the .py file is in the same folder.
  pause
  exit /b 1
)

REM Create venv if needed
if not exist "%PYEXE%" (
  echo Creating virtual environment...
  where py >nul 2>nul
  if %ERRORLEVEL% EQU 0 (
    py -3 -m venv "%VENV%"
  ) else (
    echo Python Launcher (py) not found. Trying "python"...
    where python >nul 2>nul || (
      echo [ERROR] Python 3.10+ is not installed or not on PATH.
      echo Please install from https://www.python.org/downloads/ (check "Add python.exe to PATH") and re-run.
      pause
      exit /b 1
    )
    python -m venv "%VENV%"
  )
  if not exist "%PYEXE%" (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
  )
  echo Upgrading pip...
  "%PYEXE%" -m pip install --upgrade pip
  echo Installing requirements...
  if exist "%REQUIREMENTS%" (
    "%PYEXE%" -m pip install -r "%REQUIREMENTS%"
  ) else (
    echo [WARN] requirements.txt not found. Installing base packages...
    "%PYEXE%" -m pip install pandas openpyxl
  )
)

echo Launching IESVE Daylight Metrics → Excel...
"%PYEXE%" "%APP%"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo [INFO] The script exited with code %RC%.
  echo Press any key to close...
  pause >nul
)

endlocal
