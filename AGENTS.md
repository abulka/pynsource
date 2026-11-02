# AGENTS.md — Pynsource contributor notes (for LLM sessions)

## What this is
Pynsource: reverse-engineers Python source into UML class diagrams (wxPython GUI + CLI).
Community edition in this repo; Pro features (zoom, drag-to-connect, module visualisation)
activate when sibling packages + license are present.

## Layout
- `src/` — all code. Entry points: `src/pynsource_gui.py` (GUI), `src/pynsource_cli.py` (CLI).
- `src/parsing/` — AST parser (`core_parser_ast.py`, visitor builds pmodel). `src/ogl/` — vendored
  copy of classic wx OGL used when `LOCAL_OGL=True` (Community canvas). Do NOT confuse with `../ogl2`.
- `src/gui/settings.py` — `PRO_EDITION` / `ALSM_PARSING` flags, `APP_VERSION` / `PATCH` version source.
- `bin/run` — runs GUI (`cd src && python3 pynsource_gui.py`). `bin/testall` — headless test run.
- `requirements.txt` — install with `uv pip install -r requirements.txt`.
- `setup.py` — legacy; reads `.requirement-extras/requirements-linux-22.txt`. Prefer `uv` + running
  from source over `pip install -e .`.
- Version bookkeeping (keep in sync, see `tbump.toml`): `src/gui/settings.py`, `DOWNLOADS.md`,
  `.requirement-extras/buildwin_github-actions.iss`, `CHANGELOG.md`,
  `Admin/site-atug/pynsource-latest{-devel,}.txt` (devel first, promote to latest after testing).

## Environment (Nov 2026 state)
- Target: **Python 3.13** + **wxPython 4.3.x**, isolated venv: `uv venv --python 3.13 .venv`
  then `uv pip install -r requirements.txt`. Old `pyenv --enable-framework` advice in
  `BUILDING.md` is obsolete — modern/uv Pythons are framework-capable.
- `.venv/` is git-ignored (global ignore). Test logs go to `src/tests/logs/` (ignored).
- **typed_ast is GONE** (EOL, no wheels for 3.11+, doesn't build on 3.13). Python 2 parsing
  (`mode=2`, `typed_ast.ast27`) was dropped: `mode(2)` raises friendly `RuntimeError`, default
  parse mode is 3, `mode(3)` always uses stdlib `ast`. Same fix applied in `../alsm`.
- `pydbg` import is commented out everywhere; `appdirs` still used (logs/config paths).

## Sibling repos (separate git repos — commit in each repo, not here)
All live in `/Users/andy/Devel/pynsource-project/` and install editable into `.venv`:
- `../ogl2` (`ogl2` package, v1.0.5) — next-gen OGL canvas. Used ONLY when `PRO_EDITION=True`.
  `ShapeCanvas` (`ogl2/ogl_like.py:1019`) paints direct via `PaintDC` (no backing buffer).
  Install: `uv pip install -e ../ogl2`.
- `../pynsource-rego` (`rego` package) — licensing. `PRO_EDITION = rego.are_registered(APP_VERSION)`
  (`int(APP_VERSION)` + 5-version forward window, so 1.x bumps keep old licenses; never jump to 2.x
  lightly). Self-sign: `cd ../pynsource-rego && ../pynsource/.venv/bin/python rego_gen.py gen <Name> --version 1 --save`.
  Install: `uv pip install -e ../pynsource-rego`. Needed NO changes for 3.13 (pure stdlib:
  hashlib/json/click/appdirs) — verified clean.
- `../alsm` (`alsm` package) — module visualisation (`ALSM_PARSING`). Parser is a fork of ours;
  keep `alsm/python/python_ast.py` in sync with `src/parsing/core_parser_ast.py` re typed_ast handling.
  Install: `uv pip install -e ../alsm`. (Its `typed-ast` pin was removed 2026-11.)

## Community vs Pro
Same codebase, behaviour switches on `PRO_EDITION` in `src/gui/settings.py`:
- **Community** (no `rego` installed, or no valid license file): canvas = vendored classic OGL
  (`src/ogl/`, `LOCAL_OGL=True`, `ogl.ShapeCanvas` with HiDPI backing buffer). No zoom
  (View/Zoom menu items disabled via `OnPro_update`), no drag-to-connect (`NATIVE_LINES_OGL_LIKE=False`
  path), no module visualisation. Free, fully working UML editor — this is what CI/tests exercise.
- **Pro** (rego installed + valid license in `~/Library/Application Support/PyNsource/` on Mac):
  canvas = `../ogl2` (`ShapeCanvas` in `ogl2/ogl_like.py:1019`, direct `PaintDC`, supports
  `scalex/scaley` zoom, zoom-to-fit, drag-between-shapes line creation). Module visualisation
  additionally needs `../alsm` (`ALSM_PARSING=True`); without alsm, Pro canvas works but module
  viz warns and disables.
- Switching: install siblings editable + save a license (see above), relaunch — no code change.
  `print("Running Community Edition")` at startup tells you which you got.
- Artefacts differ by edition: binary builds (`bin/buildmac`, `bin/buildwin.bat`, snap) ship
  Community (no license embedded); the atug download page sells Pro.

## Deploying (Mac)
- Only supported route: CI `.github/workflows/build-mac.yml` — a `pre-*` tag builds a draft
  pre-release (+ artifact), manual dispatch gives an artifact only.
- The build **must** use uv's python-build-standalone, never `actions/setup-python`: a
  framework Python plus wxasync's macOS loop freezes the canvas for the whole duration of a
  mouse drag. Full write-up: `Admin/BUG-DIST-SLOWNESS-MAC.md`. The workflow prints
  `BUILD PYTHON ... framework=''` and a guard step fails the build if a framework interpreter
  or a onefile layout reappears.
- Bundling is **onedir** (`../ogl2/bin/pynsource-github-actions.spec`): launch 0.4s vs 1.9s
  for onefile, and PyInstaller 7 rejects onefile + `.app`. `dist/` then contains both
  `dist/Pynsource/` (COLLECT output — delete it, it is duplicated inside the app) and
  `dist/Pynsource.app` (what ships).
- Zip with `-y` (`zip -r -y`, or `ditto -c -k --keepParent`); without it the
  `Contents/Resources` symlinks are followed and the payload is stored twice (83MB vs 35MB).
- Ad-hoc signed only (no Apple Developer account) — users still run `fix-permissions.command`.
- Local `bin/buildmac.sh` works but picks up whatever `python3`/`pyinstaller` is on PATH,
  which is exactly how the framework-Python bug got in. Prefer CI.

## Tests
- `mkdir -p src/tests/logs && .venv/bin/python -m unittest discover -s src` — expect `158 tests OK`
  (a handful skip without wx / are pre-existing skips). Runs WITH wx installed too.
- `TRAVIS=1` prefix = legacy headless flag (skips wx-dependent tests); kept for compat, not required.
- `../ogl2`: `.venv/bin/python -m pytest ../ogl2/tests/ -x -q`.

## Gotchas / recent fixes (don't regress)
- **Print preview range**: `FilePrint` must build `wx.PrintDialogData(self.printData)` with
  Min/Max/From/To=1 + `EnablePageNumbers(False)` and pass THAT to `wx.PrintPreview`
  (passing bare `wx.PrintData` falls back to 1..9999 on Mac). `HasPage(page<=1)` +
  `GetPageInfo(1,1,1,1)` in `src/common/printframework.py` stay as belt-and-braces
  (wxPython has no `GetPagesInfo` binding).
- **Blurry UML text**: `src/ogl/canvas.py` backing buffer is HiDPI-aware (physical pixels ×
  `GetContentScaleFactor()`, rebuilt on `EVT_DPI_CHANGED`). ogl2 path has no buffer — its
  sharpness fix is `int(round(...))` (not `int(...)`) in `DrawFormattedText` in BOTH
  `src/ogl/oglmisc.py` and `ogl2/ogl2/oglmisc.py` (vendored mirrors, fix both).
- Fonts: UML regions use `wx.MODERN` 10/14pt (`src/gui/uml_canvas.py`); ogl2 defaults are
  `FONTFAMILY_SWISS` 14pt (`ogl2/ogl_like.py`). Don't change families without a screenshot check.
- No `timeout(1)` on macOS — use `cmd & sleep; kill` pattern for GUI smoke tests.
