Pynsource
=========

Version number: Version 1.75 (November 25 2019)

Author: Andy Bulka

Overview
--------

Reverse engineer Python source code into UML class diagrams.

Installation / Usage
--------------------

### Ready to run binary apps ###

 * [Mac download](http://bit.ly/pynsource-mac-1-75) (unzip and drag app into the Applications directory) 
 * [Windows 10 download](http://bit.ly/pynsource-win-1-75) (unzip and run the installer) 
 * [Ubuntu Linux 18.0.4 download](http://bit.ly/pynsource-ubuntu-18-1-75) (unzip and run the executable) 
 * [Ubuntu Linux 16.0.4 download](http://bit.ly/pynsource-ubuntu-16-1-75) (unzip and run the executable) 
 * [Linux snap installer](http://bit.ly/pynsource-snap) (install on any distro using Snapcraft) 
 
An affordable, commercial [Pro Edition](http://pynsource.com/pricing.html) is also available with extra features 
like zoom and the ability to drag to connect shapes.

### To run from source code ###

You need Python 3.6 or later already installed, and pip3, then simply:

    $ git clone https://github.com/abulka/pynsource.git
    $ cd pynsource
    $ pip install -r requirements.txt
    $ ./run

Linux Users: Please use the script `bin/install-linux` to pip install needed dependencies,
including a wxPython wheel specific to Ubuntu 18. Edit the script to change to your version 
number of Ubuntu. Or simply use the prebuilt binaries executables! 

Features
--------

 - Generates UML diagrams from Python 3 or legacy Python source code
 - The only UML tool that recognises Python instance attributes (not just class attributes) 
 - Layout algorithm
 - Toggle between UML, Ascii art UML and PlantUML views
 - Automatically colour sibling subclasses to enhance understanding
 - Print and Print preview
 - Windows 10, Mac OSX Mojave, Linux compatibility
 - Open Source
 - Pro edition with
    - Faster performance
    - Zoom
    - Drag and Drop to connect shapes
    - Optimal layout algorithm
    - Access to generated PlantUML markup text 

Examples
--------

![](https://www.dropbox.com/s/aq4hu3hfdvtxkp8/pynsource-comments.png?raw=1)

![](https://www.dropbox.com/s/3o2p7h6qqf5hbhc/pynsource-zoom-line-edit.png?raw=1)

![](https://www.dropbox.com/s/w183c0vmt8o6qs9/pynsource-drag-drop-connect.png?raw=1)

Example of Ascii UML View:


                                   +-----------------------+
    +-------------------+          |RoleServicesObject     |
    |AI                 |          |.......................|
    |....................        * |role                   |
    |roleServiceObjects '''''''''''|gameservices           |----- .|
    |gameServices       |___       |_rolemanager           |       |
    |...................|   |      |_etc1                  |       |
    |API_RunABit        |   |      |.......................|       |
    |API_GetOrdersForR  |   |      |API_GetCurrentStoryline|       |
    |API_CreateRoleServc|   |      |API_GetCurrentRoleName |       |
    +-------------------+   |      |API_GetRoleSubordinates|       |
                            |      +-----------------------+       |
                            |                                      |
                            |                                      |
                            | 1 +---------------------------+ /    |
                            .---+GameServices               |_.....'
                                +---------------------------| -.
                                |_scenario                  |
                                |_game                      |
                                ............................|
                                |API_GetAstarTravelTimeBlah |
                                |API_GetOobtreeInfoOnOobId  |
                                |API_GetOobtreeInfoOnMe     |
                                +---------------------------+

Examples of PlantUML view:

![](https://www.dropbox.com/s/v6f5t2hohl97hja/pynsource-plantuml-1.png?raw=1)

![](https://www.dropbox.com/s/furf89q7b2brpr0/pynsource-plantuml-2.png?raw=1)

Note: PlantUML view requires an internet connection.
                                    
What does Pynsource mean?
-------------------------

    Py = Python
    N = and
    Source = Source code

Long Answer: Since it was built in Australia, which is famous for its meat pies and sauce
   at football matches, Pie-and-Sauce.  Where Py = Python and Source = source code.
   
Home Page and Documentation
---------------------------

More screenshots, videos and documentation can be found at

www.pynsource.com

Help is built into the app - hit F1

[Youtube video tutorial](https://youtu.be/FEXeDI18LMs) on basic usage of Pynsource (pro edition is featured).

If you want more control over the Pynsource initial window size and position see 
[this link](https://github.com/abulka/pynsource/issues/49#issuecomment-475069439)

When using PlantUML view, if you want to run your own PlantUML server (faster, larger diagrams), see the Pynsource built in help for installation and configuration instructions.  

Help support the project by Donating or purchasing a Pro Edition license.  Future plans include
undo/redo, recognition of Python type annotations, line labels, module and package visualisation.


License
-------

The Community Edition is open source, GPL3 licensed.

The Pro Edition is commercially licensed and requires a valid license to use.
  
