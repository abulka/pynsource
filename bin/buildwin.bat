@echo off
REM Local Windows build. CI is .github/workflows/build-win.yml - prefer that.
REM Prerequisites: Inno Setup 6 (ISCC.exe on PATH) and a booted venv (bin\boot on mac/linux
REM creates .venv; on Windows it is `uv venv --python 3.13 .venv` + `uv pip install -r requirements.txt`).
setlocal
cd /d "%~dp0.."

set PYTHON=.venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

echo Building sample UML diagrams...
call "%PYTHON%" buildtools\buildsamples.py
if errorlevel 1 goto :error

echo Running PyInstaller (onedir)...
call "%PYTHON%" -m PyInstaller --noconfirm buildtools\pynsource.spec
if errorlevel 1 goto :error

echo Running Inno Setup...
iscc .requirement-extras\buildwin_github-actions.iss
if errorlevel 1 goto :error

echo Done. Look in dist\Pynsource\ and dist-inno\.
goto :eof

:error
echo Build failed.
exit /b 1
