@echo off
REM All in one build script
set outsourceexe1=PyNsource-1.5.win32.exe
set outsourceexe=PyNsource-1.5.win32-py26.exe
set outsourcezip=pyNsource-1.5.zip
set outstandalone=pyNsource-1.5-standaloneexe.zip
REM goto end

del /q dist\*.*

REM Build source distribution via setup tools exe
del /q build\lib\pynsource\*.*
c:\python26\python.exe setup.py bdist_wininst
move dist\%outsourceexe1% dist\%outsourceexe%

REM Build raw source zip by zipping up appropriate files
del /q dist\%outsourcezip%
"c:\Program Files\7-Zip"\7z a -tzip  -xr!".svn" -xr!"build" -xr!"dist" -xr!*.pyc dist\%outsourcezip% pynsource\* Tests\*.py setup.py

REM buildstandaloneexe.bat
cd pynsource
del /q dist\*.*
python setup.py py2exe
cd ..
"c:\Program Files\7-Zip"\7z a -tzip  dist\%outstandalone% pynsource\dist\*

:end
