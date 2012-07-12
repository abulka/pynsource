@echo off
REM All in one build script
set outsourceexe1=PyNsource-1.60.win32.exe
set outsourceexe=PyNsource-1.60.win32-py26.exe
set outsourcezip=pyNsource-1.60-src.zip
set outstandalonezip=pyNsource-1.60-standalone.zip
set outsetupexe=pyNsource-1.60-setup.exe

REM delete all generated files and regen the build.txt file from subversion
del /q dist\*.*

REM remember to run "svn update" before running this in order to get the correct repo number
svn info > build.txt

REM goto step3
goto step3

:step1
REM Build source distribution via setup tools exe
del /q build\lib\pynsource\*.*
c:\python27\python.exe setup.py bdist_wininst
move dist\%outsourceexe1% dist\%outsourceexe%

:step2
REM Build raw source zip by zipping up appropriate files
"c:\Program Files\7-Zip"\7z a -tzip  -xr!".svn" -xr!"build" -xr!"dist" -xr!"java-ide-import-results" -xr!*.pyc dist\%outsourcezip% pynsource\* tests\* setup.py Readme.txt rungui.bat runtests.bat build.txt

:step3
REM buildstandalone exe zip
cd pynsource
del /q dist\*.*
python setup.py py2exe
cd ..
:step3a
"c:\Program Files\7-Zip"\7z a -tzip  dist\%outstandalonezip% .\pynsource\dist\* .\Readme.txt .\build.txt

:step4
REM Build standalone with convenient setup using innosetup
REM "c:\Program Files\Inno Setup 5\ISCC.exe" buildSetupExeWin.iss
"C:\Program Files (x86)\Inno Setup 5\ISCC.exe" buildSetupExeWin.iss

move build\setup.exe dist\%outsetupexe%

:end
dir dist
echo All done!