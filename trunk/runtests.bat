@echo off
REM goto delphi

:unittests
cd tests
python alltests.py
cd ..
REM pause
REM goto end

:java
cd tests\testing-generate-java
python ..\..\src\pynsource.py -j java-out python-in\*.py
cd ..\..

:delphi
cd tests\testing-generate-delphi
python ..\..\src\pynsource.py -d delphi-out python-in\*.py
cd ..\..

echo OK, Done
:end
pause

