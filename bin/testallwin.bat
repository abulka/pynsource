@echo off
REM Run the full test suite, wx included (needs a desktop session). Equivalent of bin/testall.
REM set TRAVIS=1 to skip every wx test - legacy escape hatch.
setlocal
set ROOT=%~dp0..
set PYTHON=%ROOT%\.venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python
cd /d "%ROOT%"
if not exist "src\tests\logs" mkdir "src\tests\logs"
"%PYTHON%" --version
"%PYTHON%" -m unittest discover -v -s src
endlocal
