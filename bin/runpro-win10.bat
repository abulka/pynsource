setlocal
echo "PRIVATE: This script is only used by the author Andy Bulka for development of the PRO version of pynsource."
cd src
REM set PYTHONPATH=\Users\Andy\ogl2;\Users\Andy\pynsource-rego
set PYTHONPATH=\Users\Andy\Devel\ogl2;\Users\Andy\Devel\pynsource-rego
rem exit /b
python pynsource-gui.py
endlocal
