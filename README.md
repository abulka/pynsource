# Pynsource

Reverse engineer Python source code into UML class diagrams.

[![latest release](https://img.shields.io/github/v/release/abulka/pynsource?include_prereleases&label=download)](https://github.com/abulka/pynsource/releases)
[![license](https://img.shields.io/badge/license-GPL3%20%2F%20commercial-blue)](https://github.com/abulka/pynsource#license)
[![website](https://img.shields.io/badge/docs-pynsource.com-informational)](https://www.pynsource.com)

![Screenshot of Pynsource showing a UML class diagram](https://www.dropbox.com/s/aq4hu3hfdvtxkp8/pynsource-comments.png?raw=1)

## Install

| | |
|---|---|
| **macOS** (Apple silicon) | `brew install --cask abulka/pynsource/pynsource` — or download the zip |
| **Windows 10/11** (64-bit) | download `pynsource-win-<version>-setup.exe` and run it |
| **Linux** (AppImage) | download `…-x86_64.AppImage` or `…-aarch64.AppImage` (`uname -m`) |
| **Ubuntu/Debian** (snap) | `sudo snap install pynsource --edge` (edge while being tested) |

Full instructions, including the one-off Gatekeeper (macOS) and SmartScreen (Windows) prompts
and Linux troubleshooting: **[DOWNLOADS.md](DOWNLOADS.md)**.

Viewing and editing diagrams is free. The Pro features (zoom, drag-to-connect, module
visualisation) need a [licence](https://pynsource.com/pricing.html) on macOS and Windows — they
are **free on Linux**.

Building from source: **[BUILDING.md](BUILDING.md)**.

## Features

- Generates UML diagrams from Python 3 source
- The only UML tool that recognises Python instance attributes (not just class attributes)
- Type annotation support
- Layout algorithm, and a toggle between UML, ASCII-art UML and PlantUML views
- Automatically colours sibling subclasses to make inheritance easier to follow
- Print and print preview
- Runs on macOS, Windows and Linux

Pro Edition adds:

- Zoom, and drag-and-drop to connect shapes
- Faster (re)layout, and access to the generated PlantUML markup
- Module visualisation, including variables and functions
  ([youtube demo](https://youtu.be/AovrE7nWGss)) — free on Linux

## Examples

![Zoom and line editing](https://www.dropbox.com/s/3o2p7h6qqf5hbhc/pynsource-zoom-line-edit.png?raw=1)

![Drag to connect shapes](https://www.dropbox.com/s/w183c0vmt8o6qs9/pynsource-drag-drop-connect.png?raw=1)

ASCII-art UML view:

```
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
                        | 1 +---------------------------+ /    |
                        .---+GameServices               |_.....'
                            +---------------------------| -.
                            |_scenario                  |
                            |_game                      |
                            ............................|
                            |API_GetAstarTravelTimeBlah |
                            |API_GetOobtreeInfoOnOobId  |
                            +---------------------------+
```

PlantUML view (needs an internet connection, or your own PlantUML server):

![PlantUML view](https://www.dropbox.com/s/v6f5t2hohl97hja/pynsource-plantuml-1.png?raw=1)

## Learn more

- Website and screenshots: [www.pynsource.com](https://www.pynsource.com)
- Help is built into the app — press `F1`
- [Video tutorial](https://youtu.be/FEXeDI18LMs) and a [module visualisation demo](https://youtu.be/AovrE7nWGss)
- To control the initial window size and position, see
  [this note](https://github.com/abulka/pynsource/issues/49#issuecomment-475069439)

## What does Pynsource mean?

Py = Python, N = and, Source = source code. Longer answer: it was built in Australia, famous for
meat pies with sauce at the football — Pie-and-Sauce.

## Credits

Author: [Andy Bulka](http://www.andypatterns.com)

## License

The Community Edition is open source, GPL3 licensed. The Pro Edition is commercially licensed and
needs a valid licence on macOS and Windows. See [CHANGELOG.md](CHANGELOG.md) for the history.
