# bin/ — developer convenience scripts

Nothing here ships in a release. The supported build route is always CI (`.github/workflows/`);
these scripts exist because typing the same three commands in a fresh worktree gets old. The
canonical instructions live in [../BUILDING.md](../BUILDING.md); this file is just an index.

Everything assumes a `.venv` in the repo root created by `boot` (uv, Python 3.13) and
works from any directory, not just the repo root.

## Daily loop

| script | what it does |
|---|---|
| `boot` | First-time setup for a clone or worktree. Idempotent — re-run it after pulling a `requirements.txt` change. Creates `.venv`, installs the sibling repos editable *if* they are checked out next door (`../wxdiagram`, `../pynsource-rego`, `../alsm`), installs `requirements.txt`, creates `src/tests/logs`. Refuses to run on Linux (no wxPython wheels there — see BUILDING.md) and on Windows/Git Bash (use `uv venv` + `uv pip install -r requirements.txt` by hand). |
| `run` | GUI from source (`src/pynsource_gui.py`), from any cwd. Passes arguments through, e.g. `bin/run --community` to force Community Edition. |
| `run-community` | `bin/run --community` — forces Community Edition regardless of licence or platform (same as `PYNSOURCE_FORCE_COMMUNITY=1 bin/run`). |
| `testall` | Full suite via `unittest discover -s src`. Needs a display; on a headless box `xvfb-run -a bin/testall`. Expect `184 tests OK (skipped=8)`. |
| `testone` | One test or a `-k` pattern: `bin/testone TestTypeHintsOnFunctionArguments`, or `bin/testone test_parse_bugs test_parse_type_annotations` for several. |

`testall` and `testone` honour `PYTHON=/path/to/python` if you want a different interpreter.

## Building

| script | what it does |
|---|---|
| `build-package` | `uv build` — sdist + wheel. Replaces the deprecated `python setup.py sdist`. Version comes from `src/gui/settings.py`, `install_requires` from `requirements.txt`. |
| `buildmac` | Local macOS build with `.venv/bin/pyinstaller`, zipped into `dist/pynsource-<version>-macos.zip`. `bin/buildmac 22.04` makes a Linux zip instead. **Prefer CI**: this only works on the platform you run it on, and it is the script whose framework-Python mistake caused the macOS drag freeze (`Admin/BUG-DIST-SLOWNESS-MAC.md`) — which is why it now refuses to use anything but the venv's PyInstaller. |
| `buildwin.bat` | Local Windows build: samples → PyInstaller (onedir) → Inno Setup. Needs Inno 6 and a booted venv. **Prefer CI**. |
| `build-appimage.sh` | Turns an existing `dist/Pynsource/` PyInstaller onedir tree into an AppImage. This one *is* used by `.github/workflows/build-linux.yml`; see the header comment for the linuxdeploy/GTK reasoning. |
| `runwin.bat`, `testallwin.bat` | Windows equivalents of `run` and `testall` (they use `.venv\Scripts\python.exe` when it exists). |

Build inputs — the PyInstaller spec and the sample-resource generator — live in
[../buildtools/](../buildtools/), not here.
