setlocal
echo "PRIVATE: This script is only used by the author Andy Bulka for development of the PRO version of pynsource."
cd src
REM set PYTHONPATH=\Users\Andy\Devel\pynsource-project\wxdiagram;\Users\Andy\Devel\pynsource-rego
set PYTHONPATH=\Users\Andy\Devel\pynsource-project\wxdiagram;\Users\Andy\Devel\pynsource-rego
rem exit /b
python pynsource_gui.py
endlocal
