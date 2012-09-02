PyNSource and PyNSource GUI
---------------------------
Reverse engineer python source code into UML - optionally display UML as Ascii
art for pasting into your source code.

Version 1.60
(c) Andy Bulka 2004-2012
andy@andypatterns.com
http://www.andypatterns.com/index.php/products/pynsource/
License: GPL 3

========================================

Features:

pyNsourceGui.py

 - Generates UML diagrams
 - Layout algorithm
 - Toggle between normal and ascii UML view
 - Colour sibling subclasses
 - Recognises inheritance, composition and cardinality
 - Colour sibling subclasses to understand the relationships in your uml diagram.
 - Print and Print preview
 - Persistence
 - Now uses standard ast python parsing

Unlike most off the shelf uml python code importers, pyNsource attempts to
recognise tricky composition relationships that are typical in python software
development. The expression "self.somevar" is correctly recognised as a UML
attribute "somevar". pyNsource attempts to guess the cardinality of associations
- if you use arrays or use .append then "one to many" is assumed.

Use the built in layout algorithm to help you get started in arranging your
classes on the workspace. The layout algorithm uses "spring layout" and animates
during layout. Overlap removal means your nodes won't overlap (unless you drag
them with the SHIFT key held down). A multipass (slower) 'Optimal' Layout is
also available which tries to find the best possible layout, within the
constraints of not being able to 'bend' lines.

Hit "v" to toggle between normal UML and Ascii UML view. Ascii UML lets you copy
and paste ascii uml text into your source code and text based documentation.
Optionally use something like the Java Ascii Versatile Editor http://www.jave.de
to wire up your ascii uml classes nicely before pasting into your source code or
documentation.  See an example of ascii UML at the bottom of this readme.


pynsource.py

 - Command line tool
 - Generates java and delphi skeleton code from python source code
 - Uses an older (non ast based) python parser

The main purpose of this tool is to provide a command line tool which can
generate java and delphi skeleton code from python source code, for the purpose
of importing (e.g. Java source code) into other UML tools - which might have
better layout and other features.

Whilst it currently uses the older python parser, it does have the feature
(which my current ast based one used in pyNsourceGui.py doesn't) of optionally
treat modules as classes, creating a "pseudo class" for each module/file. In
such a case, module variables and functions are treated as attributes and
methods of a 'class'. I hope to add the "treat modules as 'classes'" feature to
the new ast based parser as used by pyNsourceGui.py in the future, as I think it
allows us to visualise modules, not just classes.


pyYumlGui.py

 - Gui tool which parses python source code and uses the Yuml online service
   http://yuml.me/ to generate png images of uml
 - Uses an older (non ast based) python parser

This was mainly a fun experiment but seems to work ok. The pynsource.py command
line tool can also generate Yuml text from python source code (use the -y option).


========================================

Installation

Windows:
  * Run setup.exe to install
  * Or run the various exe's from the standalone distribution zip.
    e.g. double click on pyNsourceGui.exe

Mac:
  * Drag the pyNsourceGui.app file into your Applications folder and launch
    pyNsourceGui

Linux:
  * Run from source code (see instructions below)
    Note that I am working on a ubuntu/debian package to make this easier.
    Please email to help or to sponser its inclusion in the standard repository
        
Run from Source:
  * Ensure you have python 2.7 installed (should be on ubuntu by default).
  * The GUI relies on wxpython http://www.wxpython.org so run the wxpython 
    installer on Windows or Mac.  If you are using Ubuntu Linux install the
    wxpython package: http://wiki.wxpython.org/InstallingOnUbuntuOrDebian
  * Install the following python egg like this:
    easy_install configobj
  * Run ./rungui.sh

   
========================================
 
Change Log

Version 1.60 (August 2012)
- New ast based python parser
- Layout algorithm
- Ascii UML view built into the gui, incl. Ascii uml layout
- Colour sibling nodes
- Persistence
- Numerous bug fixes

Version 1.52
- Can now delete the selected classe from edit menu, or simply use the Del key
- yUml diagramming (online service for rendering and laying out UML) in both command line tool and GUI
- Ascii Art UML improved formatting and added tab to GUI
- Linux (ubuntu/mint 9) compatibility verified - just install wxpython and run from source.  GUI runs ok-ish.
- File Import Recursively feature removed.  You can already multi select files
  during import - and - you can already import repeatedly and incoming classes will
  be added and wired up to existing classes on the workspace.
- Source code clean up

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

Example of Ascii UML:


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

SVN repository for pynsource is
  http://code.google.com/p/pynsource/

Report bugs to
  http://code.google.com/p/pynsource/issues/list
  
========================================

Q: What does pynsource mean?

A: Since it was built in Australia, which is famous for its meat pies and sauce
   at football matches, Pie-and-Sauce.  Where Py = Python and Source = source code.
   
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
