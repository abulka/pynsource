@echo off
REM generate an asciiart uml diagram
@echo on
python src\pynsource.py -a tests\python-in\testmodule01.py > outasciiart.txt
@echo off
echo Copy your asci art UML into e.g Java Ascii Versatile Editor http://www.jave.de/
notepad outasciiart.txt