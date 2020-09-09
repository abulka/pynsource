# Pynsource

Version number: Version 1.76 (Apr 22 2020)

Author: [Andy Bulka](www.andypatterns.com)

![Python application](https://github.com/abulka/pynsource/workflows/Python%20application/badge.svg)

## Overview

Reverse engineer Python source code into UML class diagrams.

## Installation / Usage

### Ready to run binary apps ###

 * [Mac download](http://bit.ly/pynsource-mac-1-76) (unzip and drag app into the Applications directory) 
 * [Windows 10 download](https://bit.ly/pynsource-win-1-73-setup-zip) (unzip and run the installer) 
 * [Ubuntu Linux 18.0.4 download](http://bit.ly/pynsource-ubuntu-18-1-76) (unzip and run the executable) 
 * [Ubuntu Linux 16.0.4 download](http://bit.ly/pynsource-ubuntu-16-1-76) (unzip and run the executable) 
 * [Linux snap installer](http://bit.ly/pynsource-snap) (install on any distro using Snapcraft) 
 
An affordable, commercial [Pro Edition](http://pynsource.com/pricing.html) is also available with extra features 
like zoom and the ability to drag to connect shapes.

### To run from source code ###

You need `python3`, specifically Python 3.7 or later *(Linux can be Python 3.6)*  installed, and `pip3`, then simply:

    $ git clone https://github.com/abulka/pynsource.git
    $ cd pynsource
    $ pip3 install -r requirements.txt
    $ ./bin/run           (Mac, Linux) or
    $ .\bin\run-win10.bat (Windows 10)

Linux Users: Please use the script `bin/install-linux` to pip install needed dependencies,
including a wxPython wheel specific to Ubuntu 18. Edit the script to change to your version 
number of Ubuntu.

The GUI toolkit [wxpython](https://wxpython.org/) that `Pynsource` relies on unfortunately needs a ‘proper’ **framework** Python environment to run in, which means no virtual environments - use your main Python e.g. brew Python on a Mac or an official install from python.org for Windows 10. The default Python 3 on Ubuntu 18.04 is fine too. 
However I've recently discovered that you can use a [pyenv](https://github.com/pyenv/pyenv) environment for building and running Pynsource, see [this issue](https://github.com/abulka/pynsource/issues/68#issuecomment-605612292) for more info on how to do this.

Or simply use the prebuilt binaries executables listed above! 
If you are on linux, then install Pynsource via the one-click [Linux snap](http://bit.ly/pynsource-snap).

### To run the tests

```
./bin/testall            (Mac, Linux) or
.\bin\testall-win10.bat  (Windows 10)
```

from the root of the project. You may need to alter the version of Python being invoked by the script e.g. `python` or `python3`.

The environment variable `TRAVIS` is set by the script to avoid tests that involve loading the wxPython package - this is especially needed on Travis and GitHub actions. It may also not be possible on your machine if you are running certain Python environments e.g. I had a problem with a framework pyenv install on my Mac running any tests that imported `wx`, even though Pynsource itself ran OK.  P.S. The subset of packages `requirements-travis.txt` is all you need to run the tests, and these exclude wx.

Alternatively you can also run all the tests by `cd src` then `./bin/testall` (because there is a testall script both in ./bin/ and in src/bin - for Mac/Linux, anyway).

### Current Test Suite status

![Python application](https://github.com/abulka/pynsource/workflows/Python%20application/badge.svg)


# Features

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
                                    
## What does Pynsource mean?

    Py = Python
    N = and
    Source = Source code

Long Answer: Since it was built in Australia, which is famous for its meat pies and sauce
   at football matches, Pie-and-Sauce.  Where Py = Python and Source = source code.
   
## Home Page and Documentation

More screenshots, videos and documentation can be found at

www.pynsource.com

Help is built into the app - hit `F1`

View a [Youtube video tutorial](https://youtu.be/FEXeDI18LMs) on the basic usage of Pynsource (pro edition is featured).

If you want more control over the Pynsource initial window size and position see 
[this link](https://github.com/abulka/pynsource/issues/49#issuecomment-475069439)

## Run your own PlantUML server
When using PlantUML view (which is not necessary to use the app), if you want to run your own PlantUML server (faster, larger diagrams, more secure), see the Pynsource built in help for installation and configuration instructions.  

## Support the project
Help support the project by [purchasing a Pro Edition license](https://pynsource.com/pricing.html) which contains extra features.  Future plans include
undo/redo, recognition of Python type annotations, line labels, module and package visualisation.

## Study the Source Code

Create instant UML and [Literate Code Map](http://bit.ly/lcodemaps) diagrams of this GitHub project.

[![button](https://www.dropbox.com/s/auynuqlfbrrxyhm/open_in_gituml_flat.png?raw=1)](http://gituml.com/ztree_scratchpad?user=abulka&repo=pynsource&commit=master)

# Changelog

View the [Changelog](CHANGELOG.md)

# License

The Community Edition is open source, GPL3 licensed.

The Pro Edition is commercially licensed and requires a valid license to use.
  
