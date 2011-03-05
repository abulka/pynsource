REM \python23\python.exe setup.py bdist_wininst
REM move dist\PyNsource-1.4c.win32.exe   dist\PyNsource-1.4c.win32_python23.exe

REM \python24\python.exe setup.py bdist_wininst
REM move dist\PyNsource-1.4c.win32.exe   dist\PyNsource-1.4c.win32_python24.exe

del /Q build\lib\pynsource\*.*
del /Q build\lib\pynsource\ogl\*.*
c:\python26\python.exe setup.py bdist_wininst
move dist\PyNsource-1.5.win32.exe   dist\PyNsource-1.5.win32_python26.exe

del /Q dist\pyNsource1.5.zip
"c:\Program Files\7-Zip"\7z a -tzip  -x!"pynsource\.svn" -x!"pynsource\ogl\.svn" -x!"pynsource\build" -x!"pynsource\dist" dist\pyNsource1.5.zip pynsource\* setup.py 
