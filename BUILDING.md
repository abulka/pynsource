# Building and running Pynsource

Pynsource runs on **Python 3.13** with **wxPython 4.3.x** (4.2.5 on Linux — see
[why](#linux-and-wxpython)). Everything below is for the Community build; the Pro-only packages
(see [sibling repos](#sibling-repos-pro-only)) are already checked out next to this repo on this
machine and are only needed for packaging.

## Run from source

```bash
uv venv --python 3.13 .venv
uv pip install -r requirements.txt
.venv/bin/python src/pynsource_gui.py       # or: bin/run
```

`bin/run` just does `cd src && python3 pynsource_gui.py`. On Windows use
`bin\run-win10.bat`, substituting the path to your venv's `python.exe`.

No system Python is required: `uv` fetches a python-build-standalone interpreter, which is also
what CI (and therefore every shipped binary) uses.

### Optional: the CLI

`src/pynsource_cli.py` parses files and dumps the parse model — handy for debugging the parser, it
does not draw anything:

```bash
.venv/bin/python src/pynsource_cli.py --methods-list src/common/*.py
.venv/bin/python src/pynsource_cli.py --version
```

## Run the tests

```bash
mkdir -p src/tests/logs
.venv/bin/python -m unittest discover -s src     # expect: Ran 158 tests ... OK (skipped=8)
```

The suite runs **with** wx installed — most tests build a real `wx.App`, so it needs a display. On
a headless machine run it under a virtual one: `xvfb-run -a python -m unittest discover -s src`
(that is exactly what the Linux CI does). `TRAVIS=1` still works as a legacy escape hatch that
skips every wx-dependent test, but it hides most of the suite; don't use it to validate a release.

`bin/testall` is a thin wrapper around the above; `bin/testone` runs a single test by name.

## Linux and wxPython

There are **no Linux wxPython wheels on PyPI** — only macOS and Windows. Linux wheels live on
wxPython's extras server, built per Ubuntu release and CPython version:

<https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04/>

That is why `uv pip install wxpython` on Linux tries to *compile* wxWidgets (30+ minutes). Install
the matching wheel first, then the rest of the requirements (the unpinned `wxpython` line is then
already satisfied):

```bash
uv pip install "https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04/wxpython-4.2.5-cp313-cp313-linux_x86_64.whl"
uv pip install -r requirements.txt
```

4.2.5 is the newest cp313 build for ubuntu-22.04, so Linux runs 4.2.5 while macOS and Windows run
4.3.x. On aarch64 nothing is prebuilt — CI compiles 4.2.5 from source (see
[releasing](#releasing)). To build it yourself you need the GTK/SDL development headers:

```bash
sudo apt install build-essential pkg-config libgtk-3-dev libsdl2-dev libnotify-dev \
  libjpeg-dev libtiff-dev libpng-dev freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev \
  libsm-dev libxtst-dev libsecret-1-dev libpcre2-dev
MAX_JOBS=$(nproc) pip wheel wxpython==4.2.5 --no-binary wxpython -w ~/wx-wheels
```

## Sibling repos (Pro only)

All live next to this repo and install editable. Without them you get the Community edition:
no zoom, no drag-to-connect, no module visualisation.

```bash
uv pip install -e ../ogl2 -e ../pynsource-rego -e ../alsm
```

- `../ogl2` — the next-generation canvas. `ShapeCanvas` paints directly via `PaintDC` and supports
  `scalex/scaley`, which is what zoom and drag-between-shapes need.
- `../pynsource-rego` — licensing. `PRO_EDITION = rego.are_registered(APP_VERSION)`.
  Self-sign a key: `cd ../pynsource-rego && ../pynsource/.venv/bin/python rego_gen.py gen Andy --version 1 --save`.
- `../alsm` — module visualisation (`ALSM_PARSING`).

See [AGENTS.md](AGENTS.md) for the edition switches and the sibling-repo coordination rules.

## Building Pynsource as a package

```bash
uv build                      # or: python setup.py sdist
uv pip install dist/pynsource-*.tar.gz
```

That gives two entry points: `pynsource` (the GUI) and `pynsource-cli`. Dev install instead:

```bash
uv pip install -e .
```

(Heads-up: `setup.py` turns `.requirement-extras/requirements-linux-22.txt` into `install_requires`,
so this pulls the whole Linux dev set — pytest, black, py2app and friends. Fine, just slow.)

## Releasing

Every artefact is built by CI from a **`pre-*` tag** (draft → published by hand) or from a manual
dispatch (artifact only). `.deploy-extras/RELEASE-NOTES.md` is the shared release body, so it does
not matter which job finishes last.

| workflow | runner | artefact |
|---|---|---|
| `build-mac.yml` | macos-14 | `pynsource-macos-<tag>.zip` (onedir `.app`, ad-hoc signed) |
| `build-win.yml` | windows-2022 | `pynsource-win-<tag>-setup.exe` (Inno Setup) |
| `build-linux.yml` | ubuntu-22.04 + ubuntu-22.04-arm | `pynsource-linux-<tag>-{x86_64,aarch64}.AppImage` |
| `build-snap.yml` | ubuntu-24.04 | `.snap` artifact, plus `snapcraft upload --release edge` on tags |

Things that bite, in order of how much time they cost when forgotten:

- **Bundle onedir, never onefile.** The spec is `../ogl2/bin/pynsource-github-actions.spec`
  (`EXE(exclude_binaries=True)` + `COLLECT` + `BUNDLE`): onefile unpacks itself into `%TEMP%` /
  `$TMPDIR` on every launch (~2 s vs 0.4 s) and PyInstaller 7 rejects onefile + `.app` outright.
- **The macOS build interpreter must be uv's python-build-standalone.** A framework Python plus
  wxasync's macOS event loop freezes the canvas for the whole duration of a mouse drag — full
  write-up in `Admin/BUG-DIST-SLOWNESS-MAC.md`, and CI fails the build if a framework interpreter
  reappears. The macOS zip must be made with `zip -r -y`, otherwise the `Contents/Resources`
  symlinks are followed and the payload is stored twice (83 MB instead of 35 MB).
- **Set the macOS bundle version in the spec** (`version=APP_VERSION` on `BUNDLE`) — without it
  Finder's *Get Info* shows `0.0.0`.
- **Homebrew tap** `abulka/homebrew-pynsource`: bump `version` and `sha256` in
  `Casks/pynsource.rb` per release, and move its `url` to the `version-#{version}` pattern at the
  next stable tag. Verify with a real `brew upgrade` — that also checks the sha.
- **The snap store credential expires.** `SNAPCRAFT_STORE_CREDENTIALS` is an exported login; when
  it lapses only the upload step fails. Re-export with
  `snapcraft export-login --snaps pynsource --channels edge,candidate,stable -` and
  `gh secret set SNAPCRAFT_STORE_CREDENTIALS`.
- Version bookkeeping (`tbump`, see `tbump.toml`): `src/gui/settings.py`,
  `.requirement-extras/buildwin_github-actions.iss`, `DOWNLOADS.md`, `CHANGELOG.md`,
  `Admin/site-atug/pynsource-latest{-devel,}.txt`.

Local builds (`bin/buildmac`, `bin/buildwin.bat`, `bin/build-appimage.sh`) work but pick up
whatever `python`/`pyinstaller` is on `PATH`, which is exactly how the macOS framework-Python bug
got in. Prefer CI.
