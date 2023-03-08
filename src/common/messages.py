# Constants used by both pynsource and pynsourcegui

WEB_VERSION_CHECK_URL_TRACKED = "http://bit.ly/pynsource-update-check-gh"
WEB_VERSION_CHECK_URL_TRACKED_DEVEL = "https://bit.ly/pynsource-update-check-devel-gh"

WEB_PYNSOURCE_HOME_URL = "http://www.pynsource.com"
WEB_PYNSOURCE_YOUTUBE_URL = "https://www.youtube.com/channel/UCDHB9YT4BruI8hhCSsCbTkw"
PYNSOURCE_CONFIG_FILE = "pynsource.ini"
PYNSOURCE_CONFIGWX_FILE = "pynsource_wx.ini"
PYNSOURCE_CONFIG_DIR = "Pynsource"

ABOUT_AUTHORS = """
Andy Bulka
 
With thanks to the free software authors Robin Dunn, 
Pierre Hjälm, Julian Smart, Erik R. Lechak and all 
those who contributed to wxPython, OGL, Python and 
its ecosystem of libraries. 
Also thanks to the wxasync project for bringing 
async/await support to wxPython.   
""".strip()

ABOUT_AUTHOR = "(c) Andy Bulka 2004-2023"
ABOUT_APPNAME = "Pynsource"
VENDOR_NAME = "Wware"
ABOUT_LICENSE = "License: GPL 3"
ABOUT_LICENSE_PRO = "License: Purchased Pro"
ABOUT_LICENSE_DETAILS = """Pynsource Community Edition is free software; 
you can redistribute it and/or modify it under the terms of the 
GNU General Public License as published by the Free Software Foundation; 
either version 2 of the License, or (at your option) any later version.

Pynsource PRO edition is a Commercial product and requires a valid paid license.
Please support further development of this project by purchasing a 
license www.pynsource.com/buy

Pynsource is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
"""
ABOUT_MSG = """
UML diagramming and reverse engineering for Python.
"""
# ABOUT_FEATURES = """
# Resilient: doesn't import the python files, thus will never get "stuck" when syntax is wrong.
# Fast
# Free
# Recognises inheritance and composition  relationships
# Recognises ocurrences of self.somevar as UML fields (no other UML tool does this for python)
# Detects the cardinality of associations e.g. one to one or 1..*  etc
# Optionally treat modules as classes - creating a pseudo class for each module - module variables and functions are  treated as attributes and methods of a class
# Has been developed using unit tests (supplied) so that you can trust it just that little bit more ;-)
# Can generate UML Ascii-art :-)
# Can generate Java and Delphi code skeletons (out of your python code) so that you can import those into a proper UML tool.
# """

WEB_UPDATE_MSG = """
There is a newer version of Pynsource available:  %s

%s

Do you wish to visit the download page now?
"""


HELP_COMMAND_LINE_USAGE = """
Usage: pynsource -v -m [-j|d outdir] | [-y outfile.png | nopng] sourcedir_or_pythonfiles...

-a generate ascii art uml (default option, no need to specify)
   NOTE: this ascii art is old alpha code - run the pynsource_gui.py
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

Note: pynsource uses an old alpha python parser.  pynsource_gui.py runs
      a newer, superior, ast based python parser.
      
UML ASCI-ART EXAMPLES
---------------------
python pynsource.py tests/python-in/testmodule01.py
python pynsource.py -m tests/python-in/testmodule03.py

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
ASCII_UML_HELP_MSG = (
    "Use the file menu to import python source code "
    "and generate UML ascii art here.\n\n"
    "Optionally join up your asci art UML using a tool like "
    "e.g Java Ascii Versatile Editor http://www.jave.de/\n\n"
    "Idea: Paste your UML Ascii art into your source code as comments!\n\n"
)

PY_YUML_ABOUT_APPNAME = "PyYuml Gui"
PY_YUML_APP_VERSION = 1.0
PY_YUML_HOME_URL = "http://yuml.me/"
PY_YUML_ABOUT_MSG = """
Convert python source code into a UML diagram.

Powered by the web service yUml at http://yuml.me and the Python source code reverse engineering tool Pynsource.

You cannot edit these diagrams, each import overwrites the previous.  You can however import multiple files at the same time.

You can zoom with CTRL-mousewheel.
You can annotate with SHIFT right mouse button drawing.
"""

PY_PLANTUML_ABOUT_APPNAME = "PlantUml Gui"
PY_PLANTUML_APP_VERSION = 1.0
PY_PLANTUML_HOME_URL = "http://plantuml.com/"
PY_PLANTUML_ABOUT_MSG = """
Convert python source code into a UML diagram.

Powered by the web service yUml at http://plantuml.com and the Python source code reverse engineering tool Pynsource.

You cannot edit these diagrams, each import overwrites the previous.  You can however import multiple files at the same time.

You can zoom with CTRL-mousewheel.
You can annotate with SHIFT right mouse button drawing.
"""

PRO_DRAG_DROP_CONNECT_HELP = """
In the Pro Edition of Pynsource, not only do you get faster performance due to the newly rebuilt 
diagramming engine, you can drag drop to connect shapes.  

The Pro version also lets you zoom in and out of the workspace, as well as the handy 'zoom to fit'
feature, which sizes the diagram to fit the available window.

Click Yes to learn more about the Pro Edition.
"""
PRO_INFO_URL = WEB_PYNSOURCE_HOME_URL  # TODO, change to be more specific

PURE_MAC_FULLSCREEN_WARNING = """
Pure fullscreen (on Mac only) slows down this app due to a wxPython OGL bug. 

** This limitation does not affect the PRO edition which uses a different, faster rendering engine. **

Please limit yourself to maximised mode (hold ALT when pressing the maximise icon, or just double click on the titlebar).

WARNING: If you have accidentally managed to get into pure fullscreen mode, performance will be very slow, even after you exit pure fullscreen mode - YOU WILL NEED TO QUIT AND RESTART Pynsource to REGAIN PERFORMANCE. 
"""
# If zoomed, you may get up to three of these popup messages for each maximise attempt - sorry about that.")

PLANTUML_VIEW_INITAL_HELP = """
No diagram to render!

---------------------------------------------------------------------
Please:

 - Import one or more Python files to reverse engineer into UML
 
 - Open an existing Pynsource diagram

  or
  
 - Switch to UML view and manually create a diagram
---------------------------------------------------------------------
 




 
 
** Note: An internet connection is required to use the PlantUML rendering service.
""".strip()

PLANTUML_VIEW_FETCHING_MSG = "Rendering via PlantUML internet server... press ESC to abort "
PLANTUML_TRY_AGAIN_HELP = "Try again with View/Redraw Screen (CMD/Ctrl R)"

PLANTUML_VIEW_INTERNET_FAIL = """
Internet connection error %s

PlantUML rendering requires an internet connection.



Tip: This could simply be a one off server timeout.
""".strip() + "  " + PLANTUML_TRY_AGAIN_HELP + """





More Help:
----------

1. Your PlantUML text is still available if you r.click on this page.

2. To use a local PlantUML server, edit your pynsource.ini and add e.g. PlantUmlServerUrl = http://localhost:8080/plantuml/uml
"""

PLANTUML_VIEW_USER_ABORT = """
User cancelled PlantUML rendering.

%s
""".strip() % PLANTUML_TRY_AGAIN_HELP

STATUS_TEXT_UML_VIEW = "SHIFT drag to draw with pen.  Right click on workspace for menu.  Drag to pan.  CMD/Ctrl + Mousewheel to zoom (Pro)."

STATUS_TEXT_UML_VIEW_NO_PLANTUML_RESPONSE = "Error rendering with plantuml - do you have an internet connection? Please check the log file for errors Help/View Log..."