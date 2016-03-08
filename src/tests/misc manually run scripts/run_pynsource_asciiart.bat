@echo off
REM generate an asciiart uml diagram
REM @echo on
python ..\..\src\pynsource.py -a ..\python-in\testmodule01.py > output\outasciiart.txt
@echo off
echo.
echo Note the command line ascii UML generation is an early alpha.
echo The pyNsourceGui produces far superior ascii UML generation
echo.
echo Copy your asci art UML into e.g Java Ascii Versatile Editor http://www.jave.de/
notepad output\outasciiart.txt