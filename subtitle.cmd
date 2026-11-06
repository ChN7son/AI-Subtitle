@echo off
setlocal DisableDelayedExpansion
if not exist "%~dp0.venv\Scripts\python.exe" (
  echo Install the dependencies first. See README.md. 1>&2
  exit /b 1
)
"%~dp0.venv\Scripts\python.exe" -X utf8 "%~dp0subtitle.py" %*
exit /b %errorlevel%
