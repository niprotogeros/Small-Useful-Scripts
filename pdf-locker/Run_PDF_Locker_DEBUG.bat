@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_NAME=lockpdf_gui_qt.py"
set "SCRIPT=%SCRIPT_DIR%%SCRIPT_NAME%"
set "VENV=%SCRIPT_DIR%.venv_pdf_locker"
set "VENV_PY=%VENV%\Scripts\python.exe"

echo === PDF Locker DEBUG ===
echo Script: %SCRIPT%

if not exist "%SCRIPT%" (echo [ERROR] Missing script.& pause & exit /b 1)

set "PYCON="
where py >nul 2>&1  && set "PYCON=py -3"
if not defined PYCON where python >nul 2>&1 && set "PYCON=python"
if not defined PYCON (echo [ERROR] Python 3 not found in PATH.& pause & exit /b 1)

if not exist "%VENV_PY%" (
  echo Creating venv at %VENV% ...
  %PYCON% -m venv "%VENV%" || (echo [ERROR] Failed to create venv.& pause & exit /b 1)
)

echo Ensuring dependencies...
"%VENV_PY%" -m pip install --upgrade pip
if exist "%SCRIPT_DIR%requirements.txt" (
  "%VENV_PY%" -m pip install -r "%SCRIPT_DIR%requirements.txt"
) else (
  "%VENV_PY%" -m pip install pikepdf PySide6
)

echo Launching GUI with console visible...
"%VENV_PY%" "%SCRIPT%" %*
set ERR=%ERRORLEVEL%
echo.
echo --- Exit code: %ERR% ---
pause
exit /b %ERR%
