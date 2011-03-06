@echo off
REM All in one build script
set outsourceexe1=PyNsource-1.5.win32.exe
set outsourceexe=PyNsource-1.5.win32-py26.exe
set outsourcezip=pyNsource-1.5-src.zip
set outstandalonezip=pyNsource-1.5-standalone.zip
set outstandalonesetupexe=pyNsource-1.5-standalone-setup.exe

REM delete all generated files and regen the build.txt file from subversion
del /q dist\*.*
svn info > build.txt

goto step3a

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
copy build.txt pynsource\dist
copy Readme.txt pynsource\dist
"c:\Program Files\7-Zip"\7z a -tzip  dist\%outstandalonezip% pynsource\dist\*

:step3a
REM Build standalone with convenient setup using innosetup
if not exist pynsource\dist\Readme.txt goto skipdeletereadme
  del /q pynsource\dist\Readme.txt
:skipdeletereadme
"c:\Program Files\Inno Setup 5\ISCC.exe" "standalone exe inno\pynsourcegui.iss"
move "standalone exe inno\Output\setup.exe" dist\%outstandalonesetupexe%

:end
