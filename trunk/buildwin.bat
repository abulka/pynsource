@echo off
REM easy_install bbfreeze
REM ensure "c:\Program Files\7-Zip" or (x86) version is in your path
REM ensure "c:\Program Files (x86)\Inno Setup 5\" is in your path

set outsourcezip=pyNsource-1.61-src.zip
set outstandalonezip=pyNsource-1.61-win32-standalone.zip

:regen_version_info_from_subversion
svn up
svn info > version.txt

:build_sample_uml_diagrams_as_resource
python buildsamples.py

REM goto build_inno_setup_exe
REM goto zip_source

:delete_existing_dist_dir
del /q dist\*.*

:build_standalone_exe
cd src
del /q dist\*.*
del /q build\*.*
bb-freeze pyNsourceGui.py pyYumlGui.py pynsource.py
cd ..
:zip_standalone_exe
7z a -tzip  dist\%outstandalonezip% .\src\dist\* .\Readme.txt .\version.txt

:zip_source
7z a -tzip  -xr!".svn" -xr!"build" -xr!"dist" -xr!*.pyc dist\%outsourcezip% src\* tests\* Readme.txt build* run* version.txt

:build_inno_setup_exe
iscc buildwin_setupexe.iss

:end
dir dist
echo All done!
