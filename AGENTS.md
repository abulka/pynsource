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
- Builds are **arm64 only** (macos-14 runner); Intel Macs are not supported until someone
  builds x86_64/universal (wxPython wheels are per-arch, so universal2 is not a one-liner).
- Ad-hoc signed only (no Apple Developer account). Users must clear the Gatekeeper block
  once: `Done` on the block dialog, then System Settings > Privacy & Security > Open Anyway
  (twice) — see `.deploy-extras/macos/IMPORTANT-README-BEFORE-RUNNING.txt`, which is also the
  draft release body. No helper script ships any more (an unsigned `.command` just added a
  second identical block).
- Users who use Homebrew get a prompt-free install via the separate tap
  `abulka/homebrew-pynsource` (`brew install --cask abulka/pynsource/pynsource`). Homebrew
  quarantines every cask download and Homebrew 7 has no `--no-quarantine`, so the cask does
  `xattr -dr com.apple.quarantine` in `postflight`. Bump its `version`/`sha256` per release.
  Caveat: Homebrew's *own* `pynsource` cask (v1.84, Intel) still exists and is `disabled`
  since 2026-09-01 for failing Gatekeeper, so the unqualified token points at that dead cask.
  Correct commands (keep these in README/DOWNLOADS too):
  `brew info --cask abulka/pynsource/pynsource`, `brew upgrade` (no args), or
  `brew upgrade --cask abulka/pynsource/pynsource`. Never document bare
  `brew info pynsource` / `brew upgrade --cask pynsource`.
- Local `bin/buildmac.sh` works but picks up whatever `python3`/`pyinstaller` is on PATH,
  which is exactly how the framework-Python bug got in. Prefer CI.

## Deploying (Windows)
- Route: CI `.github/workflows/build-win.yml` (windows-2022) — same triggers as Mac: a `pre-*`
  tag adds `pynsource-win-<tag>-setup.exe` to the draft pre-release, manual dispatch gives an
  artifact only. Both Mac and Windows workflows append to the *same* draft release for a tag;
  Mac finishes first (~1 min vs ~2.5 min), so action-gh-release always finds an existing draft
  and updates it (verified on `pre-2026-dustoff-4`).
- Same uv python-build-standalone approach as Mac (`UV_PYTHON_PREFERENCE=only-managed`); the
  framework-Python drag bug is Mac-only, but keeping one interpreter story avoids surprises.
  Use `.venv/Scripts/python.exe` explicitly — `$GITHUB_PATH` wants native Windows paths, so
  the Mac workflow's `echo $PWD/.venv/bin >> $GITHUB_PATH` idiom does not carry over.
- Windows is **onedir** like Mac (shared spec, so no divergence; `BUNDLE` is a no-op off
  macOS). The installer therefore ships `dist\Pynsource\*` (exe + `_internal\`), not a single
  onefile exe — `.requirement-extras/buildwin_github-actions.iss` `[Files]` expects that.
  Inno output goes to `dist-inno\`; CI renames it to `pynsource-win-<tag>-setup.exe`.
- Inno Setup is **not preinstalled** (choco installs it, ISCC.exe in `Program Files (x86)`),
  and the `.iss` needs Inno **6.3+** because it uses `ArchitecturesInstallIn64BitMode=x64compatible`
  (the old `x64` is deprecated and excludes ARM64 Windows, where the x64 build runs emulated).
- The `.iss` AppVersion/VersionInfoVersion/OutputBaseFilename are still tbump-managed; CI only
  renames the output, so nothing needs bumping per tag.
- Guards (Mac guard is mac-specific, don't copy it): onedir payload present
  (`_internal/python313.dll`), `Pynsource.exe` stays alive 20 s, and a silent install
  (`/VERYSILENT /DIR=<temp>`) produces a working exe that also stays alive. That is the whole
  Windows verification - the installer cannot be tested on macOS; `innoextract` 1.9 cannot read
  Inno 6.5 either.
- Unsigned (no code-signing cert): users get "Windows protected your PC" → **More info > Run
  anyway**. Documented in the shared `.deploy-extras/RELEASE-NOTES.md` (also the release body).
- Local `bin/buildwin.bat` still works, same `.iss`, but needs Inno 6 and picks up whatever
  python/pyinstaller is on PATH. Prefer CI.

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
