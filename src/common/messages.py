# Constants used by both pynsource and pynsourcegui

WEB_VERSION_CHECK_URL = "http://www.atug.com/downloads/pynsource-latest.txt"
WEB_PYNSOURCE_HOME_URL = "http://www.andypatterns.com/index.php/products/pynsource/"
PYNSOURCE_CONFIG_FILE = "pynsource.ini"
PYNSOURCE_CONFIG_DIR = "PyNSource"
ABOUT_AUTHOR = "(c) Andy Bulka 2004-2012"
ABOUT_APPNAME = "PyNSource"
ABOUT_LICENSE = "License: GPL 3"
ABOUT_MSG = """
PyNSource is a UML modelling tool for Python source code.

Reverse engineer python source code into either a UML diagram
or into Ascii Art UML which you can paste into your source code!
"""
#ABOUT_FEATURES = """
#Resilient: doesn't import the python files, thus will never get "stuck" when syntax is wrong.
#Fast
#Free
#Recognises inheritance and composition  relationships
#Recognises ocurrences of self.somevar as UML fields (no other UML tool does this for python)
#Detects the cardinality of associations e.g. one to one or 1..*  etc
#Optionally treat modules as classes - creating a pseudo class for each module - module variables and functions are  treated as attributes and methods of a class
#Has been developed using unit tests (supplied) so that you can trust it just that little bit more ;-)
#Can generate UML Ascii-art :-)
#Can generate Java and Delphi code skeletons (out of your python code) so that you can import those into a proper UML tool.
#"""

WEB_UPDATE_MSG = """
There is a newer version of PyNSource GUI available:  %s

%s

Do you wish to visit the download page now?
"""


HELP_COMMAND_LINE_USAGE = """
Usage: pynsource -v -m [-j|d outdir] | [-y outfile.png | nopng] sourcedir_or_pythonfiles...

-a generate ascii art uml (default option, no need to specify)
   NOTE: this ascii art is old alpha code - run the pyNsourceGui.py
    for superior uml as ascii
-j generate java files, specify output folder for java files
-d generate delphi files, specify output folder for delphi files
-l generate Plant Uml text, specify output png or 'nopng' if you don't want one
-y generate yUml text, specify output png or 'nopng' if you don't want one
   NOTE: run the pyYumlGui.py for a gui interface to this.
-v verbose
-m create psuedo class for each module,
   module attrs/defs etc treated as class attrs/defs
-x experimental test code (devel only)
-p show parse model, no code generated, diagostic

Note: pynsource uses an old alpha python parser.  pyNsourceGui.py runs
      a newer, superior, ast based python parser.
      
UML ASCI-ART EXAMPLES
---------------------
python pynsource.py Test\\testmodule01.py
python pynsource.py -m Test\\testmodule03.py

JAVA EXAMPLES
-------------
python pynsource.py -j c:\\try c:\\try
python pynsource.py -v -m -j c:\\try c:\\try
python pynsource.py -v -m -j c:\\try c:\\try\\s*.py
python pynsource.py -j c:\\try c:\\try\\s*.py Tests\\u*.py
python pynsource.py -v -m -j c:\\try c:\\try\\s*.py Tests\\u*.py c:\cc\Devel\Client\w*.py

DELPHI EXAMPLE
--------------
python pynsource.py -d c:\\delphiouputdir c:\\pythoninputdir\\*.py

yUML EXAMPLES
-------------
python pynsource.py -y yumlout.png tests\\python-in\\testmodule01.py
python pynsource.py -y None tests\\python-in\\testmodule01.py

Plant UML EXAMPLES
-------------
python pynsource.py -l out.png tests/python-in/testmodule01.py
python pynsource.py -l None tests/python-in/testmodule01.py

option_show_parse_model EXAMPLES
-------------
python pynsource.py -p tests/python-in/*
python pynsource.py -p None tests/python-in/testmodule01.py
"""

DELPHI_UNIT_FILE_TEMPLATE = """
unit unit_%s;

interface

type

    %s = class
    public
    end;

implementation

end.
"""
ASCII_UML_HELP_MSG = \
"Use the file menu to import python source code " \
"and generate UML ascii art here.\n\n" \
"Optionally join up your asci art UML using a tool like " \
"e.g Java Ascii Versatile Editor http://www.jave.de/\n\n" \
"Idea: Paste your UML Ascii art into your source code as comments!\n\n"

PY_YUML_ABOUT_APPNAME = "PyYuml Gui"
PY_YUML_APP_VERSION = 1.0
PY_YUML_HOME_URL = "http://yuml.me/"
PY_YUML_ABOUT_MSG = """
Convert python source code into a UML diagram.

Powered by the web service yUml at http://yuml.me and the Python source code reverse engineering tool PyNSource.

You cannot edit these diagrams, each import overwrites the previous.  You can however import multiple files at the same time.

You can zoom with CTRL-mousewheel.
You can annotate with SHIFT right mouse button drawing.
"""

PY_PLANTUML_ABOUT_APPNAME = "PlantUml Gui"
PY_PLANTUML_APP_VERSION = 1.0
PY_PLANTUML_HOME_URL = "http://plantuml.com/"
PY_PLANTUML_ABOUT_MSG = """
Convert python source code into a UML diagram.

Powered by the web service yUml at http://plantuml.com and the Python source code reverse engineering tool PyNSource.

You cannot edit these diagrams, each import overwrites the previous.  You can however import multiple files at the same time.

You can zoom with CTRL-mousewheel.
You can annotate with SHIFT right mouse button drawing.
"""

