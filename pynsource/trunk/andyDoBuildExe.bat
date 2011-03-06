@echo off
REM All in one build script
set outsourceexe=PyNsource-1.5.win32_python26.exe
set outsourcezip=pyNsource1.5.zip
set outstandalone=pyNsource1.5standaloneexe.zip
REM goto end

del /q dist\*.*

REM Build source distribution via setup tools exe
del /q build\lib\pynsource\*.*
c:\python26\python.exe setup.py bdist_wininst
move dist\PyNsource-1.5.win32.exe   dist\%outsourceexe%

REM Build raw source zip
del /q dist\%outsourcezip%
"c:\Program Files\7-Zip"\7z a -tzip  -xr!".svn" -xr!"build" -xr!"dist" -xr!*.pyc dist\%outsourcezip% pynsource\* Tests\*.py setup.py

REM buildstandaloneexe.bat
cd pynsource
del /q dist\*.*
python setup.py py2exe
cd ..
"c:\Program Files\7-Zip"\7z a -tzip  dist\%outstandalone% pynsource\dist\*

:end
