@echo off
REM All in one build script
set outsourceexe1=PyNsource-1.5.win32.exe
set outsourceexe=PyNsource-1.5.win32-py26.exe
set outsourcezip=pyNsource-1.5-src.zip
set outstandalonezip=pyNsource-1.5-standalone.zip
set outsetupexe=pyNsource-1.5-setup.exe

REM delete all generated files and regen the build.txt file from subversion
del /q dist\*.*
svn info > build.txt

REM goto step3

:step1
REM Build source distribution via setup tools exe
del /q build\lib\pynsource\*.*
c:\python26\python.exe setup.py bdist_wininst
move dist\%outsourceexe1% dist\%outsourceexe%

:step2
REM Build raw source zip by zipping up appropriate files
"c:\Program Files\7-Zip"\7z a -tzip  -xr!".svn" -xr!"build" -xr!"dist" -xr!*.pyc dist\%outsourcezip% pynsource\* Tests\*.py setup.py Readme.txt rungui.bat build.txt

:step3
REM buildstandaloneexe.bat
cd pynsource
del /q dist\*.*
python setup.py py2exe
cd ..
:step3a
"c:\Program Files\7-Zip"\7z a -tzip  dist\%outstandalonezip% .\pynsource\dist\* .\Readme.txt .\build.txt

:step4
REM Build standalone with convenient setup using innosetup
"c:\Program Files\Inno Setup 5\ISCC.exe" buildSetupExeWin.iss
move build\setup.exe dist\%outsetupexe%

:end
dir dist
echo All done!