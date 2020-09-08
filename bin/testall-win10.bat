cd src
REM mkdir -p tests/logs
if not exist "tests/logs" mkdir "tests/logs"

REM avoid wx by setting the TRAVIS env var, which happens automatically on travis and
REM is set explicitly in .github/workflows/pythonapp.yml 
set TRAVIS=1
call python -m unittest discover -v -s tests
if %ERRORLEVEL% neq 0 goto ProcessError

:ProcessError
cd ..