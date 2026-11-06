@echo off
setlocal DisableDelayedExpansion
chcp 65001 >nul
if "%~1"=="" goto usage
if not "%~2"=="" goto usage
if not exist "%~dp0.venv\Scripts\python.exe" (
  echo Install the dependencies first. See README.md. 1>&2
  pause
  exit /b 1
)
"%~dp0.venv\Scripts\python.exe" -X utf8 "%~dp0subtitle.py" "%~f1" --srt "%~dp0校對\%~n1.zh-TW.srt" --output-dir "%~dp0校對"
set "status=%errorlevel%"
pause
exit /b %status%
:usage
echo Drag one original video onto this batch file.
pause
exit /b 2
