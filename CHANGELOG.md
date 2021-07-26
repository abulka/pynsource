# Pynsource Change Log

### 1.79-3

- Fix missing app icon on Mac and Ubuntu builds
- Fix executable +x flag on ubuntu builds
- Export diagram to XML for importing into tools like Cytoscape https://cytoscape.org/ which have advanced layouts and visualisations

### 1.79

*July 2021*

- Built with Python 3.9 so Pynsource can handle parsing Python walrus operator
- Module Visualisation incl. variables and functions (Pro)
- Python parsing improvements and bug fixes (issues 85, 93, 94)
- Latest version of wxPython, wxasync and other Python packages
- More informative logging (see Help / View Log...)

- A note on Ubuntu Pynsource builds:
  - Ubuntu 20.04 Pynsource: is built with Python 3.8, not Python 3.9 due to the unavailability of a Python 3.9 build of `wxPython` for Ubuntu 20.04. This should one day be remedied. You can still parse the Python walrus operator with Python 3.8 ok, so this version of Pynsource is still fully capable.
  - Snap Pynsource: is built with Python 3.6 because Python 3.6 is the default on `core18`. Building under `core20` which has Python 3.8 not currently possible due to the snapcraft Python plug and GNOME `gnome-3-38` not yet being compatible.

### 1.78

  - beta release
  
### 1.77

*September 2020*

- Type annotations support e.g. the type annotation `param: SomeClass` will create a UML dependency to `SomeClass` etc.

- Static method detection bugfix

### 1.76 

*April 2020*

- Dark Mode Support (Mac)

- Import report dialog after importing Python files

- Improved handling of modules with syntax errors

- Improved logging of parsing process

### 1.75

*November 2019*

- Asyncronous performance fixes (Mac)

- Line joining accuracy improvements (Pro)

- Ability to pass files you want to reverse engineer via the command line

- Better debugging via Help/Logs... of PlantUML rendering via internet

- Improved Help including
  - YouTube video tutorial link
  - How to set up a local PlantUML server (optional)

### 1.74

*March 2019*

- Bug fixes:
    - fixed shape jumping back to drag start position if not selected (windows, linux)
    - add proper extension when saving files (linux)

- config file enhancement for people who have small or unusual displays (mac, windows, linux)

- first snap release (linux)

### 1.73

- Windows/Linux fixed select object refresh bug
  (you had to click twice to select an object)
- Major Linux bug fixes: 
  - scrolled area refresh bug fixed
  - fixed insert class and comment hotkeys
- Misc bug fixes

### 1.72

*February 2019*

- Improved Linux compatibility
- Misc fixes

### 1.71

- Python 3 parsing support
- PlantUML view
- Print and Print preview fixes
- Pro edition with faster performance, zoom, drag and drop to connect shapes

### 1.60

- New python parser based on built in AST parser
- Integrated ASCII UML view
- Animated layout algorithm
- Node colouring 
- Save your diagrams to disk
