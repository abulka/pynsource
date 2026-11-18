# Pynsource Change Log

*November 2026*

### 1.87

- New diagram canvas: pynsource now uses **wxdiagram** (MIT) on every platform and edition
  (0.2.1, the first published release since 0.1.0);
  the vendored classic OGL copy and the `ogl2` dependency are gone
- wxdiagram upgraded to **0.2.3**: dragging a multi-selection that includes an edge no longer
  stretches the edge (it now follows its endpoint shapes exactly), dragging an edge on its own
  leaves it attached, and changing diagrams clears the old selection handles immediately
- Zoom, pan, zoom-to-fit, drag-to-connect, resize and layout are **free for everyone**
- wxdiagram now owns zoom, pinch-to-zoom, drag-to-pan and the canvas virtual size; the
  duplicated `CanvasResizer`/zoom code is gone
- Smoother trackpad scrolling and panning (20px per wheel notch, fractional accumulation,
  3px pan threshold)
- Marquee selection (plain drag on empty canvas), Shift/Ctrl add, Esc clear, arrow-key nudge
- Dragging any shape in a multi-selection moves the whole group
- Undo/redo for editing commands and canvas drags
- Duplicate now offsets down and slightly right (deliberately overlapping) and selects the copies
- Explicit z-order commands (Bring to Front / Forward, Send Backward / to Back) in the Edit menu
  and shape context menu; click no longer changes z-order
- Image import is centred, scaled to fit the viewport and sent to the back; the new image is
  selected and shows resize handles, and resizing works via wxdiagram's ResizableBitmapShape
- Image resize keeps its selection handles and no longer prints "no node model attached" warnings
- Image and rectangle resize now track the mouse at any zoom level (wxdiagram no longer snaps
  resize geometry to whole units), corner drags clamp at the opposite corner, and resizing is
  proportional by default (hold Shift for free aspect)
- Shapes show eight resize handles (four corners plus four edge midpoints); edge handles resize
  one axis, and the resize completes wherever the mouse is released
- Alt resizes a shape from its centre, and drags/resizes ignore movement below 3px so a click
  with a small hand tremor no longer nudges a shape
- Dragging snaps to other shapes' edges and centres with alignment guides (wxdiagram's
  `alignmentGuides`, on by default); an optional background grid and snap-to-grid are available
  through the same canvas flags
- Canvas repaints use buffered painting, and macOS trackpad scrolling/panning is no longer
  over-sensitive (wxdiagram now uses wxOSX's precise deltas instead of scaling them by 20)
- wxdiagram connectors gained edge labels, label hit-testing and hybrid routing
  (`autoRoute = "curved"`: free bezier, obstacle detour, orthogonal fallback, parallel lanes);
  UML edges now use the curved style
- UML edges default to "Straight or curved" (wxdiagram `auto`): straight unless a box blocks the
  path, then a curve - never an orthogonal detour while routing is experimental.  Right-click a
  line for Edge style: Straight / Curved / Straight or curved / Avoid boxes (orth fallback) /
  Orthogonal (the menu ticks the current style).  Arrowheads follow routed curves
- Zoom-to-fit and the canvas scroll range now include imported images, so a resized image can
  always be scrolled to (previously its far edges were outside the scrollable area)
- wxdiagram composites are resizable (children scale with the frame) and polygons are clickable
  anywhere inside, not just on their outline
- Content at negative diagram coordinates is now scrollable and framed by zoom-to-fit, so a
  shape dragged or resized past the top-left origin is no longer stranded off-canvas
- Quieter startup: the debug `cwd_info` line is no longer printed to the console
- Layout menu has an "Auto Remove Overlaps" toggle, persisted in the user config
- Removed the last `*OglTwo` class names (`UmlDividedShape`, `UmlCommentShape`,
  `UmlLineShape`, `UmlBitmapShape`, `UmlShapeHandler`) and the `ogl` import alias
- Plain drag on empty canvas now marquees; use Alt/Space/middle-drag or the trackpad to pan
- **Pro is now module visualisation only** (ALSM), still free on Linux
- Simplified settings and canvas code: one canvas path, one coordinate convention, and the
  `Move2` monkeypatch replaced by `Shape.MoveTo`
- Build assets (PyInstaller spec, mac/win build scripts, `.icns`) moved into this repo
- Single-instance guard: a second launch shows "Pynsource is already running" instead of
  opening another window (`PYNSOURCE_ALLOW_MULTIPLE=1` opts out)
- Fixed: on macOS, a source run no longer launches the separately installed Pynsource app
  through the window-activation `osascript` (that is now frozen-app only)
- CI now checks out the public `wxdiagram` repo; the branch can be selected when dispatching
- PlantUML markup/save and ASCII-art zoom are free (previously Pro)
- PlantUML view: new **View / PlantUML Server...** dialog to choose the server (official, your own,
  or a custom url) with a Test button, instead of editing the config file by hand
- PlantUML view: wide diagrams are no longer silently cropped. The server caps images at 4096 px,
  so the HiDPI scale now steps down automatically and the status bar says when a diagram is too big
  for PNG at all (use SVG export)
- PlantUML view: recovers from the public server's "boxes but no text" renders by re-requesting a
  fresh url, and never shows the narrower text-less version when a good one is available
- PlantUML markup dialog: the copy button verifies what actually reached the clipboard (macOS
  "smart dashes" can turn `--|>` into an em dash), and a new "Open in browser" button sends the
  diagram to the chosen server without copy/paste at all

### 1.86

- First stable release since 1.84 (2022) - supersedes the 1.85 beta series, which is no longer
  the current version
- macOS builds are **Apple silicon only**; 1.84 was the last Intel release
- Revived with Python 3.13 and wxPython 4.3, isolated `uv` venv (`uv venv --python 3.13`, `uv pip install -r requirements.txt`)
- Dropped Python 2 parsing (typed_ast is end-of-life, no builds for Python 3.11+)
- Removed redundant File/Python 3 mode menu - always Python 3 now
- Fixed Mac print preview page range showing 1..9999 (now correctly 1..1)
- Fixed blurry UML text on Retina/HiDPI displays (HiDPI-aware canvas buffer, rounded text positioning in OGL and OGL2)
- alsm and ogl2 updated for Python 3.13
- **Pro features are free on Linux** (zoom, drag-to-connect, module visualisation) - no licence needed
- Linux ships as a single-file AppImage for x86_64 **and** arm64 (no install, no root)
- Windows installer rebuilt on Inno Setup 6 and an onedir bundle; macOS ships an ad-hoc signed
  onedir `.app`, installable prompt-free via `brew install --cask abulka/pynsource/pynsource`
- Ubuntu snap modernised: core24, Python 3.12, strict confinement
- Every platform is now built by CI from a `pre-*` tag and attached to one release

*February 2023*

### 1.85 beta

- Fixed: Pynsource can now parse Python 3.10 syntax
- Apple Silicon Arm build available for Mac
- Ubuntu 22.04 / Mint 21 / Debian builds available.
- Limitation: Ubuntu Snap still uses Python 3.6 so cannot parse Python 3.10 syntax. 

*February 2022*

### 1.84

- fixed: more robust handling of type annotations on function and method arguments e.g. def foo(a: Optional[str]):

### 1.83

- fixed: Adapt (again, 2022) to new PlantUML server API which broke PlantUML diagram rendering
- fixed: UML ascii art formatting on Mac using OSXEnableAutomaticDashSubstitution(False)

*Late 2021*

### 1.81

- Adapt to new PlantUML server API which broke PlantUML diagram rendering
- Matrix Multiplication operator @ now parsed correctly (fixes issue 102)
- Handle any type of nested string parameter annotation e.g. "A" or "A.B" or "A.B.C" etc. (fixes issue 103)

### 1.80

- Fix missing app icon on Mac and Ubuntu builds
- Fix executable +x flag on Ubuntu builds
- Export diagram to XML for importing into tools like Cytoscape https://cytoscape.org/ which have advanced layouts and visualisations. See Pynsource built in help for instructions.

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
