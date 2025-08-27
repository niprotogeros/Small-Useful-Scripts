@echo off
setlocal EnableExtensions

rem === CONFIG =============================================================
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_NAME=lockpdf_gui_qt.py"
set "SCRIPT=%SCRIPT_DIR%%SCRIPT_NAME%"
set "VENV=%SCRIPT_DIR%.venv_pdf_locker"
set "VENV_PY=%VENV%\Scripts\python.exe"
set "VENV_PYW=%VENV%\Scripts\pythonw.exe"
set "VBS=%SCRIPT_DIR%run_hidden.vbs"
rem =======================================================================

if not exist "%SCRIPT%" (
  echo [ERROR] Can't find "%SCRIPT%"
  pause & exit /b 1
)

rem Find a base Python
set "PYCON="
where py >nul 2>&1  && set "PYCON=py -3"
if not defined PYCON where python >nul 2>&1 && set "PYCON=python"
if not defined PYCON (
  echo [ERROR] Python 3 not found in PATH.
  echo Install from https://www.python.org/downloads/ and ensure it's in PATH.
  pause & exit /b 1
)

rem Create venv if missing
if not exist "%VENV_PY%" (
  echo Creating virtual environment at %VENV% ...
  %PYCON% -m venv "%VENV%" || (echo [ERROR] Venv creation failed.& pause & exit /b 1)
  "%VENV_PY%" -m pip install --upgrade pip
  if exist "%SCRIPT_DIR%requirements.txt" (
    "%VENV_PY%" -m pip install -r "%SCRIPT_DIR%requirements.txt"
  ) else (
    "%VENV_PY%" -m pip install pikepdf PySide6
  )
) else (
  rem Ensure deps
  "%VENV_PY%" -c "import pikepdf; import PySide6" 1>nul 2>nul || (
    if exist "%SCRIPT_DIR%requirements.txt" (
      "%VENV_PY%" -m pip install --upgrade -r "%SCRIPT_DIR%requirements.txt"
    ) else (
      "%VENV_PY%" -m pip install --upgrade pikepdf PySide6
    )
  )
)

rem ===== Launch order: pythonw.exe -> VBS (hidden) -> console visible =====
if exist "%VENV_PYW%" (
  start "" "%VENV_PYW%" "%SCRIPT%" %*
  exit /b 0
)

if exist "%VBS%" (
  wscript //nologo "%VBS%" "%VENV_PY%" "%SCRIPT%" %*
  exit /b 0
)

echo [WARN] run_hidden.vbs not found. Running with console visible...
"%VENV_PY%" "%SCRIPT%" %*
pause
exit /b 0
