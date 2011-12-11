# Constants used by both pynsource and pynsourcegui

WEB_VERSION_CHECK_URL = "http://www.atug.com/downloads/pynsource-latest.txt"
WEB_PYNSOURCE_HOME_URL = "http://www.andypatterns.com/index.php/products/pynsource/"
PYNSOURCE_CONFIG_FILE = "pynsource.ini"
PYNSOURCE_CONFIG_DIR = "PyNSource"
ABOUT_AUTHOR = "(c) Andy Bulka 2004-2011"
ABOUT_APPNAME = "PyNSource"
ABOUT_LICENSE = "License: GPL 3 (free software)"
ABOUT_MSG = """
PyNSource is a UML modelling tool for Python source code.

Reverse engineer python source code into either a UML diagram or into an Ascii Art attempt at UML - and paste it into your source code!
"""
ABOUT_FEATURES = """
Resilient: doesn't import the python files, thus will never get "stuck" when syntax is wrong.
Fast
Free
Recognises inheritance and composition  relationships
Recognises ocurrences of self.somevar as UML fields (no other UML tool does this for python)
Detects the cardinality of associations e.g. one to one or 1..*  etc
Optionally treat modules as classes - creating a pseudo class for each module - module variables and functions are  treated as attributes and methods of a class
Has been developed using unit tests (supplied) so that you can trust it just that little bit more ;-)
Can generate UML Ascii-art :-)
Can generate Java and Delphi code skeletons (out of your python code) so that you can import those into a proper UML tool.
"""

WEB_UPDATE_MSG = """
There is a newer version of PyNSource GUI available:  %s

%s

Do you wish to visit the download page now?
"""

HELP_MSG = """
PyNSource Gui Help:

Import a python file and it will be reverse engineered and represented as UML.

Import multiple files by multiple selecting files (hold ctrl and/or shift) in the file open dialog.
You can import repeatedly and incoming classes will be added and wired up to existing classes on the workspace.

Whilst this is mainly a reverse engineering tool, you can add new classes by pressing Ins.  You can also delete uncessesary classes by pressing Del.
To draw lines between classes: Select the first class, hit 'q', select the second class, hit 'w'.

Use -> (right arrow) to expand the layout spacing and <- (left arrow) to contract.  Or use the MouseWheel.  Laying out lots of classes does better with an increased layout spacing, but takes up more room.

After a (possibly slow) 'Optimal' Layout, there may be layout variants that you can access by pressing 1, 2 ... 8 in order of perfection.
"""

HELP_COMMAND_LINE_USAGE = """
Usage: pynsource -v -m [-j|d outdir] | [-y outfile.png | nopng] sourcedir_or_pythonfiles...

-a generate ascii art uml (default option, no need to specify)
-j generate java files, specify output folder for java files
-d generate delphi files, specify output folder for delphi files
-y generate yUml text, specify output png or 'nopng' if you don't want one
-v verbose
-m create psuedo class for each module,
   module attrs/defs etc treated as class attrs/defs

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

