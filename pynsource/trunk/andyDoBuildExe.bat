REM \python23\python.exe setup.py bdist_wininst
REM move dist\PyNsource-1.4c.win32.exe   dist\PyNsource-1.4c.win32_python23.exe

REM \python24\python.exe setup.py bdist_wininst
REM move dist\PyNsource-1.4c.win32.exe   dist\PyNsource-1.4c.win32_python24.exe

del /Q build\lib\pynsource\*.*
c:\python26\python.exe setup.py bdist_wininst
move dist\PyNsource-1.5.win32.exe   dist\PyNsource-1.5.win32_python26.exe

del /Q dist\pyNsource1.5.zip
"c:\Program Files\7-Zip"\7z a -tzip  -xr!".svn" -xr!"build" -xr!"dist" -xr!*.pyc dist\pyNsource1.5.zip pynsource\* Tests\*.py setup.py

REM buildstandaloneexe.bat
cd pynsource
del /q dist\*.*
python setup.py py2exe
cd ..
del /q dist\pyNsource1.5standaloneexe.zip
"c:\Program Files\7-Zip"\7z a -tzip  dist\pyNsource1.5standaloneexe.zip pynsource\dist\*
