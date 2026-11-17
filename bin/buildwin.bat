@echo off
REM Local Windows build. CI is .github/workflows/build-win.yml - prefer that.
REM Prerequisites: pyinstaller, Inno Setup 6 (ISCC.exe on PATH), 7-Zip (optional).

echo Building sample UML diagrams...
call python bin\_buildsamples.py

echo Running PyInstaller (onedir)...
pyinstaller --noconfirm bin\pynsource-github-actions.spec

echo Running Inno Setup...
iscc .requirement-extras\buildwin_github-actions.iss

echo Done. Look in dist\Pynsource\ and dist-inno\.
