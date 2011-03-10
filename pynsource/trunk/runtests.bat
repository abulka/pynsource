@echo off
REM goto delphi

:unittests
cd tests
python alltests.py
cd ..
REM pause

:java
cd tests\testing-generate-java
python ..\..\pynsource\pynsource.py -j java-out python-in\*.py
cd ..\..

:delphi
cd tests\testing-generate-delphi
python ..\..\pynsource\pynsource.py -d delphi-out python-in\*.py
cd ..\..

:end
echo OK, Done
pause

