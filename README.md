# Pynsource

Author: [Andy Bulka](http://www.andypatterns.com)

![Python application](https://github.com/abulka/pynsource/workflows/Python%20application/badge.svg)

## Overview

Reverse engineer Python source code into UML class diagrams.

## Installation

[Download](DOWNLOADS.md) - ready to run builds are available for Mac, Windows and Linux.

> Mac users please [right click open](https://www.howtogeek.com/205393/gatekeeper-101-why-your-mac-only-allows-apple-approved-software-by-default/) the first time, 
Mac Big Sur, Monterey, Ventura users need to first `xattr -dr com.apple.quarantine /Applications/Pynsource.app`. 
🎉 Easier Technique for Mac Users: Right click on the supplied bash script `fix-permissions.command` and choose "Open" to apply the correct permissions to `Pynsource`.
Then you can copy the app to you Applications/ folder and run it as normal.

An affordable, commercial [Pro Edition](http://pynsource.com/pricing.html) is also available with extra features 
like zoom and the ability to drag to connect shapes.

To build and install from source code, see [building from source](BUILDING.md)

# Features

 - Generates UML diagrams from Python 3 or legacy Python source code
 - The only UML tool that recognises Python instance attributes (not just class attributes)
 - Type annotation support *(new for 2020)*
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
    - Module Visualisation incl. variables and functions *(new for 2021, [youtube demo](https://youtu.be/AovrE7nWGss))*

# Examples

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

![](https://www.dropbox.com/s/3gqiyn7vlxbnhj3/pynsource-module-visualisation.gif?raw=1)

Note: Module Visualisation is a Pro feature.
                                    
## What does Pynsource mean?

    Py = Python
    N = and
    Source = Source code

Long Answer: Since it was built in Australia, which is famous for its meat pies and sauce
   at football matches, Pie-and-Sauce.  Where Py = Python and Source = source code.
   
## Home Page and Documentation

More screenshots, videos and documentation can be found at
www.pynsource.com

- Help is built into the app - hit `F1`

- View a [Youtube video tutorial](https://youtu.be/FEXeDI18LMs) on the basic usage of Pynsource (pro edition is featured).
- [Module Visualisation](https://youtu.be/AovrE7nWGss) youtube demo.

- If you want more control over the Pynsource initial window size and position see 
[this link](https://github.com/abulka/pynsource/issues/49#issuecomment-475069439)

### Run your own PlantUML server
When using PlantUML view (which is not necessary to use the app), if you want to run your own PlantUML server (faster, larger diagrams, more secure), see the Pynsource built in help for installation and configuration instructions.  

### Support the project
Help support the project by [purchasing a Pro Edition license](https://pynsource.com/pricing.html) which contains extra features.  Future plans include
undo/redo and line labels.
  
## Study the Source Code

Create instant UML and [Literate Code Map](http://bit.ly/lcodemaps) diagrams of this GitHub project.

[![button](https://www.dropbox.com/s/auynuqlfbrrxyhm/open_in_gituml_flat.png?raw=1)](http://gituml.com/ztree_scratchpad?user=abulka&repo=pynsource&commit=master)


# Changelog

View the [Changelog](CHANGELOG.md)
<!-- https://github.com/abulka/pynsource/blob/master/CHANGELOG.md -->

# License

The Community Edition is open source, GPL3 licensed.

The Pro Edition is commercially licensed and requires a valid license to use.
  
