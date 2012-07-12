@echo off
REM easy_install bbfreeze
REM ensure "c:\Program Files\7-Zip" or (x86) version is in your path

set outsourcezip=pyNsource-1.6-src.zip
set outstandalonezip=pyNsource-1.6-standalone.zip

svn info > build.txt

REM goto step3a

REM buildstandalone exe zip
cd src
del /q dist\*.*
del /q build\*.*
REM python setup.py py2exe
bb-freeze pyNsourceGui.py
cd ..

:step3a
7z a -tzip  dist\%outstandalonezip% .\src\dist\* .\Readme.txt .\build.txt


