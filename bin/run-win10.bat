@echo off
REM Run the GUI from source. Equivalent of bin/run on mac/linux.
setlocal
set ROOT=%~dp0..
set PYTHON=%ROOT%\.venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python
cd /d "%ROOT%\src"
"%PYTHON%" pynsource_gui.py %*
endlocal
