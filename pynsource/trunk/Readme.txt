PyNSource and PyNSource GUI
---------------------------
Reverse engineer python source code into UML - display UML as Ascii art or in a proper diagramming visual workspace.
You can also generate java and delphi skeleton code from the python, for the purpose of importing that into other UML tools.

Version 1.51
(c) Andy Bulka 2004-2011
andy@andypatterns.com
http://www.andypatterns.com/index.php/products/pynsource/
License: GPL 3 (free software).

========================================

Features

 - Resilient: doesn't import the python files, thus will never get "stuck" when syntax is wrong.
 - Fast
 - Recognises inheritance and composition  relationships
 - Recognises ocurrences of self.somevar as UML fields (no other UML tool does this for python)
 - Detects the cardinality of associations e.g. one to one or 1..*  etc
 - Optionally treat modules as classes - creating a pseudo class for each 
   module - module variables and functions are  treated as attributes and methods of a class
 - Has been developed using unit tests (supplied) so that you can trust it just that little bit more ;-)
 - Can generate UML Ascii-art :-)
 - Can generate Java and Delphi code skeletons (out of your python code) so that you can import those into a proper UML tool.
 - Free

========================================

Quick Start

Run the GUI tool pynsourcegui.exe and:
 - Import a python file and it will be reverse engineered and represented as UML.
 - Import multiple files by multiple selecting files (hold ctrl and/or shift) in the file open dialog.
 - Import recursively at your own peril - too many classes will clutter you diagrams.
 - Layout is a bit dodgy so arrange your layout a little and then do a screen grab (using your favourite screen grabbing tool) or print.
 - You cannot add new classes in the GUI, this is just a reverse engineering tool.  You can however delete uncessesary classes by right clicking on the node.

Run the Command Line tool pynsource.py and:
 - Reverse engineer python source code into UML - display UML as Ascii art.
 - You can also generate java and delphi skeleton code from the python, for the purpose of importing that into other UML tools.

========================================

Installation

There are 4 distributions variations

pyNsource-X.X-setup.exe       - windows setup, install and run pynsourcegui.exe from the shortcut
pyNsource-X.X-src.zip         - source code deployment, unzip anywhere and run python pynsourcegui.py or python pynsource.py
pyNsource-X.X-standalone.zip  - standalone exe deployment, unzip anywhere and run pynsourcegui.exe or pynsource.exe
PyNsource-X.X.win32-py26.exe  - source code / package deployment via Distutils exe

Note re Distutils package installation.  Your source code will be installed into 
   \PythonXX\Lib\site-packages\pynsource\ so adjust your python command line invocations to refer to that location.
   Using the pynsource as a package doesn't make sense at the moment as you can't import pynsource and do
   anything useful (well it hasn't been thought out yet, anyway) so its really just a handy place to keep the source.
   You'd probably want to write a script to invoke things more nicely.
   
========================================
 
Change Log

Version 1.51
- Check the web for updates feature (via help menu)

Version 1.5
- Python 2.6 compatibility
- Runs with latest wxpython
- Menus reworked, help added, command to visit website added.
- Print preview now much smarter about showing your entire uml workspace
- pynsource.exe added to standalone distribution
- Readme vastly improved

Version 1.4c
- Fixed some parsing bugs.
- Parsing now more correct under python 2.4 (python changed token.py !!)
- Unit tests now all pass

Version 1.4b
- Added wxpython 2.5 compatibility (thanks Thomas Margraf!)

Version 1.4a
- GUI changes:
- Right Click on a node to delete it.
- Run Layout anytime from menu.
- Left click on background will deselect any selected shapes

Version 1.4
- Fixed indentation error causing more output than normal in text ouput
- Module level functions not treated as classes any more
- Smarter detection of composition relationships, as long as classname 
  and variable name are the same (ignoring case) then PyNSource will detect e.g.

  class Cat:
    pass

  class A:
    def __init__(self, cat):
      self.cats.append(Cat())  # always has worked, composition detected.
      self.cats.append(cat)    # new 1.4 feature, composition detected here too.

Version 1.3a
- Announced: A reverse engineering tool for Python source code
- UML diagram models that you can layout, arrange and print out.
- UML text diagrams, which you can paste into your source code for documentation purposes.
- Java or Delphi code (which can be subsequently imported into more sophisticated UML 
  modelling tools, like Enterprise Architect or ESS-Model (free).)

========================================

Instructions for running the GUI

- Run the standalone: pynsourcegui.exe
- Run from source code: python pyNsourceGui.py

If you used the distutil installer your files might be in e.g.
  Python26\Lib\site-packages\pynsource\pyNsourceGui.py

The GUI relies on wxpython http://www.wxpython.org

The PyNSource command line tool is pynsource.py

========================================

Instructions for running the Command line tool

 pynsource -v -m [-j outdir] [-d outdir] sourceDirOrListOfPythonFiles...   

no options - generate UML Ascii art

-j generate java files, specify output folder for java files
-d generate pascal files, specify output folder for pascal files
-v verbose
-m create psuedo class for each module,
   module attrs/defs etc treated as class attrs/defs

Examples

BASIC ASCII UML OUTPUT from PYTHON - EXAMPLES
e.g. pynsource Test/testmodule01.py
e.g. pynsource -m Test/testmodule03.py

GENERATE JAVA FILES from PYTHON - EXAMPLES
e.g. pynsource -j c:/try c:/try
e.g. pynsource -v -m -j c:/try c:/try
e.g. pynsource -v -m -j c:/try c:/try/s*.py
e.g. pynsource -j c:/try c:/try/s*.py Tests/u*.py
e.g. pynsource -v -m -j c:/try c:/try/s*.py Tests/u*.py c:\cc\Devel\Client\w*.py

GENERATE DELPHI  FILES from PYTHON - EXAMPLE
e.g. pynsource -d c:/delphiouputdir c:/pythoninputdir/*.py
e.g. \python26\python.exe  \Python26\Lib\site-packages\pynsource\pynsource.py  -d  c:\delphiouputdir  c:\pythoninputdir\*.py
 (The above line will scan all the files in c:\pythoninputdir and generate a bunch of delphi files in the folder c:\delphiouputdir)

TIP on long path names and path names with spaces:  
  If you have long filenames, then enclosing paths and file references in double quotes is necessary and works ok. 
  e.g. "c:\Documents and Settings\Administrator\Desktop\stuff"

========================================

Displaying UML in Ascii using pynsource

Sample:

                                                               +---------------------------+
             +------------------------------------+            |RoleServicesObject         |
             |AI                                  |            |...........................|
             |.....................................          * |role                       |
             |roleServiceObjects                  '''''''''''''|gameservices               |----- ...|
 +-----+     |gameServices                        |_____       |_rolemanager               |         |
 |game `-.   |....................................|     |      |_etc1                      |         |
 +-----+  `-.|API_RunABit                         |     |      |...........................|         |
             |API_GetOrdersForRole                |     |      |API_GetCurrentStoryline    |         |
             |API_CreateRoleServicesObjectForRole |     |      |API_GetCurrentRoleName     |         |
             +------------------------------------+     |      |API_GetRoleSubordinates    |         |
                                                        |      +---------------------------+         |
                                                        |                                            |
                                                        |                                            |
                                                        | 1 +-------------------------------+ /      |
                                                        .---+GameServices                   |_.......'
                                                            +-------------------------------| -.
                                                            |_scenario                      |
                                                            |_game                          |
                                                            ................................|
                                                            |API_GetAstarTravelTimeBlahBlah |
                                                            |API_GetOobtreeInfoOnOobId      |
                                                            |API_GetOobtreeInfoOnMe         |
                                                            +-------------------------------+
  
See http://www.andypatterns.com/index.php/products/pynsource/asciiart/ for more into

========================================

Notes for building a pynsource release

Just run 
 - buildAllWin.bat

This will
 - Build win32 installers in dist as an exe.  
   People can run this exe to install the source code as a package into \PythonXX\Lib\site-packages\pynsource
 - Zip up pynsource source files and Tests and ./setup.py into a pure source code release e.g. pynsourceX.X.zip
 - Build a standalone exe using py2exe.  This is done in the pynsource subdirectory's dist dir.  
   These files (incl. the standalone pynsourcegui.exe) are zipped. 
 - Run Inno setup to create a standalone setup.exe, together with uninstall tool.   

========================================

SVN repository is
 http://pyidea.svn.sourceforge.net/svnroot/pyidea/pynsource/trunk

========================================

License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

========================================
