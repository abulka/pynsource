cd src
REM mkdir -p tests/logs
if not exist "tests/logs" mkdir "tests/logs"

REM Full suite, wx included (needs a desktop session).
REM set TRAVIS=1 to skip every wx test - legacy escape hatch
call python -m unittest discover -v -s tests
if %ERRORLEVEL% neq 0 goto ProcessError

:ProcessError
cd ..