# Constants used by both pynsource and pynsourcegui

WEB_VERSION_CHECK_URL = "http://www.atug.com/downloads/pynsource-latest.txt"
WEB_PYNSOURCE_HOME_URL = "http://www.andypatterns.com/index.php/products/pynsource/"

ABOUT_MSG = """
PyNSource GUI

Version %s

A GUI front end to the python code scanner PyNSource that generates UML diagrams from Python Source code.

(c) Andy Bulka 2004-2011
http://www.andypatterns.com/index.php/products/pynsource/

License: GPL 3 (free software).
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

Layout is a bit dodgy so arrange your layout a little and then do a screen grab (using your favourite screen grabbing tool) or print.
You cannot add new classes in the GUI, this is just a reverse engineering tool.  You can however delete uncessesary classes by right clicking on the node.
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
