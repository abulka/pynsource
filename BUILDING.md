# Building and running Pynsource

Pynsource runs on **Python 3.13** with **wxPython 4.3.x** (4.2.5 on Linux — see
[why](#linux-and-wxpython)). The diagram canvas is the `wxdiagram` library; module
visualisation (the one remaining Pro feature) additionally needs `alsm`.

## Run from source

```bash
bin/boot        # one-time (and after any requirements.txt change): creates .venv, installs all
bin/run         # launch the GUI; equivalent to: cd src && ../.venv/bin/python pynsource_gui.py
```

`bin/boot` is idempotent and is the script to run in a fresh worktree: `uv venv --python 3.13
.venv`, then the sibling repos editable *if* they are checked out next door (`../wxdiagram`,
`../pynsource-rego`, `../alsm`), then `uv pip install -r requirements.txt`. It refuses to run on
Linux — install the wxPython wheel first, see [Linux and wxPython](#linux-and-wxpython). The
manual equivalent on any platform is those two `uv` lines.

On Windows use `bin\runwin.bat` after creating the venv and installing the requirements
yourself; the batch files just prefer `.venv\Scripts\python.exe`. [bin/README.md](bin/README.md)
indexes every script.

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
.venv/bin/python -m unittest discover -s src     # expect: Ran 184 tests ... OK (skipped=8)
```

The suite runs **with** wx installed — most tests build a real `wx.App`, so it needs a display. On
a headless machine run it under a virtual one: `xvfb-run -a python -m unittest discover -s src`
(that is exactly what the Linux CI does). `TRAVIS=1` still works as a legacy escape hatch that
skips every wx-dependent test, but it hides most of the suite; don't use it to validate a release.

`bin/testall` is a thin wrapper around the above (`PYTHON=... bin/testall` to use another
interpreter). `bin/testone` runs a subset by pattern, e.g.
`bin/testone TestTypeHintsOnFunctionArguments` or `bin/testone test_parse_bugs test_parse_type_annotations`.

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

## Sibling repos

All live next to this repo and install editable.

```bash
uv pip install -e ../wxdiagram -e ../pynsource-rego -e ../alsm
```

- `../wxdiagram` — the canvas library (shapes, connectors, zoom/pan, selection,
  JSON persistence). MIT, also on PyPI as `wxdiagram`.
- `../pynsource-rego` — licensing for module visualisation.
  `PRO_EDITION = rego.are_registered(APP_VERSION)`.
  Self-sign a key: `cd ../pynsource-rego && ../pynsource/.venv/bin/python rego_gen.py gen Andy --version 1 --save`.
- `../alsm` — module visualisation (`ALSM_PARSING`). Pro; free on Linux builds.

See [AGENTS.md](AGENTS.md) for the edition switches and the sibling-repo coordination rules.

## Building Pynsource as a package

```bash
uv build                      # or: bin/build-package  -> dist/pynsource-<version>.tar.gz + .whl
uv pip install dist/pynsource-*.tar.gz
```

That gives two entry points: `pynsource` (the GUI) and `pynsource-cli`. Dev install instead:

```bash
uv pip install -e .
```

`setup.py` is legacy but still the source of that metadata (the snap does `pip install .`). It
scrapes the version from `src/gui/settings.py` and uses `requirements.txt` verbatim as
`install_requires`, so the sdist also declares the test deps (pytest, coverage). Nothing is
published to PyPI — the shipped artefacts are the CI-built app, installer, AppImage and snap.

## Releasing

Release status, the promotion checklist and future milestones live in `Admin/ROADMAP.md`.

Every artefact is built by CI from a **`pre-*` or `version-*` tag** — the tag creates (or adds to)
one draft release, which is published by hand — or from a manual dispatch (artifact only).
`.deploy-extras/RELEASE-NOTES.md` is the shared release body, so it does not matter which job
finishes last.

| workflow | runner | artefact |
|---|---|---|
| `build-mac.yml` | macos-15 | `pynsource-macos-<tag>.zip` (onedir `.app`, ad-hoc signed) |
| `build-win.yml` | windows-2022 | `pynsource-win-<tag>-setup.exe` (Inno Setup) |
| `build-linux.yml` | ubuntu-22.04 + ubuntu-22.04-arm | `pynsource-linux-<tag>-{x86_64,aarch64}.AppImage` |
| `build-snap.yml` | ubuntu-24.04 | `.snap` artifact, plus `snapcraft upload --release edge` on tags |

Things that bite, in order of how much time they cost when forgotten:

- **Bundle onedir, never onefile.** The spec is `buildtools/pynsource.spec`
  (`EXE(exclude_binaries=True)` + `COLLECT` + `BUNDLE`): onefile unpacks itself into `%TEMP%` /
  `$TMPDIR` on every launch (~2 s vs 0.4 s) and PyInstaller 7 rejects onefile + `.app` outright.
- **The macOS build interpreter must be uv's python-build-standalone.** A framework Python plus
  wxasync's macOS event loop freezes the canvas for the whole duration of a mouse drag — full
  write-up in `Admin/BUG-DIST-SLOWNESS-MAC.md`, and CI fails the build if a framework interpreter
  reappears. The macOS zip must be made with `zip -r -y`, otherwise the `Contents/Resources`
  symlinks are followed and the payload is stored twice (83 MB instead of 35 MB).
- **Set the macOS bundle version in the spec** (`version=APP_VERSION` on `BUNDLE`) — without it
  Finder's *Get Info* shows `0.0.0`.
- **macOS window activation is frozen-only on purpose.** `MainApp.OnInit` raises the frame and,
  in a frozen build only, activates its own `.app` with `open -a <path>`. Do not replace this
  with `osascript -e 'tell application "Pynsource" to activate'`: AppleScript resolves the app by
  name and launches an installed copy (it started 1.86 during a source run of 1.87). See the
  macOS section of [AGENTS.md](AGENTS.md) for the full note.
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
