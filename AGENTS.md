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
- `bin/run` — runs GUI (`cd src && python3 pynsource_gui.py`). `bin/testall` — full test suite,
  wx included (needs a display; `xvfb-run -a bin/testall` on a headless box).
- Docs are split deliberately: `README.md` = pitch + install table, `DOWNLOADS.md` = the only
  install/troubleshooting reference (linked from the website), `BUILDING.md` = the only developer
  doc. Do not duplicate build/run/test instructions here — point at BUILDING.md.
- `requirements.txt` — install with `uv pip install -r requirements.txt`.
- `setup.py` — legacy; reads `.requirement-extras/requirements-linux-22.txt`. Prefer `uv` + running
  from source over `pip install -e .`.
- Version bookkeeping (keep in sync, see `tbump.toml`): `src/gui/settings.py`, `DOWNLOADS.md`,
  `.requirement-extras/buildwin_github-actions.iss`, `CHANGELOG.md`,
  `Admin/site-atug/pynsource-latest{-devel,}.txt` (devel first, promote to latest after testing).

## Environment (Nov 2026 state)
- Target: **Python 3.13** + **wxPython 4.3.x** (4.2.5 on Linux), isolated venv: `uv venv
  --python 3.13 .venv` then `uv pip install -r requirements.txt`. uv's python-build-standalone is
  framework-capable, so the old `pyenv --enable-framework` dance is obsolete (it is also what the
  macOS drag-freeze bug came from — see `Admin/BUG-DIST-SLOWNESS-MAC.md`).
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
- **Linux is Pro by platform**, regardless of licences: `sys.platform.startswith("linux")` forces
  `PRO_EDITION = True` in `src/gui/settings.py` (snaps cannot persist a licence file; there is no
  way to buy one that survives the packaging routes). Consequence: every Linux artefact must
  bundle ogl2 + alsm, and Linux CI runs the Pro code paths that macOS/Windows CI never executes.
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
- **`actions/upload-artifact` does not preserve symlinks**, and the `.app` is full of them
  (`Contents/Resources`). The *artifact* copy therefore fails `codesign --verify --deep
  --strict` ("a sealed resource is missing or invalid") even when the build was fine — verify
  from the **release zip** instead, which CI creates before uploading.
- The spec lives in the **ogl2 repo**: a spec change only reaches CI once it is *pushed* to
  ogl2's `2026-dustoff`. Use `gh workflow run build-mac.yml --ref 2026-dustoff` (artifact only,
  no release) to validate a spec change; it is ~1.5 min.

## Deploying (Windows)
- Route: CI `.github/workflows/build-win.yml` (windows-2022) — same triggers as Mac: a `pre-*`
  tag adds `pynsource-win-<tag>-setup.exe` to the draft pre-release, manual dispatch gives an
  artifact only. Both Mac and Windows workflows append to the *same* draft release for a tag;
  Mac finishes first (~1 min vs ~2.5 min), so action-gh-release always finds an existing draft
  and updates it (verified on `pre-2026-dustoff-4`). If the two runs create a draft
  simultaneously, one is removed automatically as a duplicate, so the parallel trigger is safe.
- **Release body caveat:** action-gh-release only writes `body_path` when it *creates* the
  release; an existing draft is never re-bodied. Both workflows therefore share one
  `.deploy-extras/RELEASE-NOTES.md`, and a notes change needs a *new* tag (or delete the draft)
  to show up. Delete-then-re-push the same tag leaves a stale body behind.
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

## Deploying (Linux)
- Route: CI `.github/workflows/build-linux.yml` → `pynsource-linux-<tag>-<arch>.AppImage` on the
  same draft release, artifact on dispatch. Same triggers as the other two. Two matrix legs:
  `ubuntu-22.04` (x86_64) and `ubuntu-22.04-arm` (aarch64) — both standard 4-CPU runners, free
  for public repos. `bin/build-appimage.sh` is arch-aware (`uname -m`) for the tool downloads
  and the output name.
- **The aarch64 leg compiles wxPython from source** (~15 min on the 4-CPU arm runner; there are
  no Linux wheels on PyPI at all, and extras.wxpython.org is x86_64 only). A wheel cache exists
  (`~/wx-wheel-cache`, key `wxpython-4.2.5-cp313-ubuntu-22.04-arm64`) but do not count on it:
  GitHub cache scope is per-branch, and **tag builds can only restore caches created on the
  default branch**, so a cache made on a scratch branch never helps a release build. Budget the
  15 minutes. Build deps exclude gstreamer/webkit
  dev packages — they only enable wx.media/wx.html2 (unused) and `libgstreamer1.0-dev` drags in
  `libunwind-dev`, which is unsatisfiable on the arm runner image.
- **ubuntu-22.04 is the glibc floor**, not `ubuntu-latest`: 22.04 = glibc 2.35, i.e. Ubuntu
  22.04+/Mint 21+/Debian 12+. Bumping the runner silently drops older distros.
- **wxPython has no Linux wheels on PyPI** — only mac/win. It comes from
  `https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04/`, built per Ubuntu
  release/CPython. 4.2.5 is the newest cp313 build there, so **Linux runs 4.2.5 while mac/win
  run 4.3.2**. Install that wheel *before* `requirements.txt`, otherwise the unpinned `wxpython`
  line makes uv build from source.
- **Linux is Pro-free by platform** (`src/gui/settings.py`), so `ogl2` and `alsm` are imported
  unconditionally: the venv must have them (`uv pip install -e ogl2/ -e pynsource-rego/ alsm/`),
  and the bundle must contain them. Mac/Windows CI never notices this, it runs Community.
- Packaging chain (`bin/build-appimage.sh`): PyInstaller onedir → AppDir → `strip` → linuxdeploy
  + `linuxdeploy-plugin-gtk` (`DEPLOY_GTK_VERSION=3`) → appimagetool. Keep that order.
  * The wx `.so` files ship with debug symbols (`_core` alone is 179 MB of a 349 MB tree);
    stripping takes the AppImage from 136 MB to ~80 MB.
  * `--library` bundles the wx leaf libs PyInstaller does not resolve (libnotify, libSM, libXtst,
    libXxf86vm, libSDL2, libsecret, libpcre2-32, libcurl + fontconfig/freetype). Without them a
    stock GTK desktop still lacks eight packages.
  * The GTK plugin sets an rpath on the binaries it deploys, but `AppRun` is our shell wrapper,
    so `usr/bin/pynsource` must export `LD_LIBRARY_PATH=$APPDIR/usr/lib` itself. Forgetting that
    is a clean-room `libgtk-3.so.0: cannot open shared object file`.
  * The spec (`../ogl2/bin/pynsource-github-actions.spec`) drops the partial GTK stack it would
    otherwise bundle; the plugin's copy is then the only one. Platform-gated, mac/win untouched.
- Guard: `xvfb-run` (a headless runner cannot create a `wx.App`), 158 tests, then extract the
  AppImage (`--appimage-extract`, no FUSE on runners) and assert `AppRun` is still alive after
  25 s **and** that the log has no "Running Community Edition" line.
- Target requirement is "a GTK3 desktop" and nothing else: verified in clean `ubuntu:22.04` and
  `ubuntu:24.04` containers with only `libgtk-3-0` installed (plus xvfb for the display). A
  container with *no* GUI libs at all fails on fontconfig/fribidi — that is expected, not a bug.
- Testing from an Apple-silicon Mac: use an **arm64** Linux VM/container (UTM, OrbStack) with
  the aarch64 AppImage. The x86_64 one gives `Exec format error` there; `qemu-user-static`
  works but is slow. Local arm64 container test: `docker run --platform linux/arm64
  ubuntu:22.04`, install `libgtk-3-0 xvfb xauth`, then `./AppImage --appimage-extract` and run
  `squashfs-root/AppRun` under xvfb.
- FUSE is absent in CI and in most containers, so `appimagetool`/`linuxdeploy` run with
  `APPIMAGE_EXTRACT_AND_RUN=1` and the guard uses `--appimage-extract`.

## Deploying (Snap)
- Route: CI `.github/workflows/build-snap.yml` → `.snap` artifact; on `pre-*` tags it also
  `snapcraft upload ... --release edge`. **Stable is promoted by hand in the store UI** after a
  snap has actually been installed and run.
- The workflow was dead for two years: `actions/upload-artifact@v3` is retired, and GitHub
  rejects the whole run before any step executes ("automatically failed because it uses a
  deprecated version"), so it produced nothing at all. Use `actions/*@v4` (and `@v5` for
  setup-uv) — v3 anywhere kills the run outright.
- Build with `snapcraft pack --destructive-mode` on **ubuntu-24.04** (the runner must match
  `base: core24`): no LXD, no build action, one less thing to go stale.
- **Do not use `plugin: python` here.** core24's python_v2 plugin rejects `/usr/bin/python3`
  and takes pip from `$PATH`, which the `gnome` extension points at the `gnome-46-2404-sdk`
  snap — and *that* pip is broken (`cannot import name 'cli' from 'pip._internal.cli.main'`).
  `plugin: nil` + `pip install --target` against `/usr/bin/python3` is dull but predictable.
- Use `--target`, not `--prefix`: Debian's python uses the `posix_local` sysconfig scheme, so
  `--prefix` silently lands scripts in `usr/local/bin` and modules in `usr/local/lib`, and the
  pack then fails with `usr/bin/pynsource does not exist`.
- The app declares `PYTHONPATH: $SNAP/usr/lib/python3.12/site-packages` because core24's python
  does not search our prefix by itself. Entry points are two-line shell wrappers calling
  `run()` / `reverse_engineer()` — the `__main__` blocks in those modules are debug scaffolding.
- **Linux is Pro-free, so the snap must bundle ogl2 + alsm** (checked out as siblings by the
  workflow, installed *with* their dependencies — `--no-deps` leaves `import alsm` failing at
  runtime, which `settings.py` then reports as "alsm not installed" because it only catches
  `ModuleNotFoundError`).
- Strip the bundled `.so` files: the wx wheel ships unstripped and turns a 154 MB snap into
  49 MB.
- `version: git` is wrong for CI: `git describe` reports the nearest *older* tag
  (`pre-2026-dustoff-6+git13…`) and `0+git.<sha>` on a shallow clone. The workflow rewrites the
  line to the tag (or `dev-<sha>` on a branch) before packing.
- The edge upload needs the `SNAPCRAFT_STORE_CREDENTIALS` secret, an exported store login with
  an expiry date. When it lapses only that step fails ("Exported credentials are no longer
  valid for the Snap Store"); re-export with
  `snapcraft export-login --snaps pynsource --channels edge,candidate,stable -` and
  `gh secret set SNAPCRAFT_STORE_CREDENTIALS`.
- The smoke test installs the snap (`--dangerous`) and runs `snap run pynsource.pynsource-cli
  --version` (qualified app name), asserting the version line and that alsm loaded.

## Tests
- Expect `158 tests OK (skipped=8)`: `mkdir -p src/tests/logs && .venv/bin/python -m unittest
  discover -s src`. Most tests build a real `wx.App`, so a headless machine needs `xvfb-run` (the
  Linux CI does this); `TRAVIS=1` is a legacy flag that skips them all — never use it to validate.
- `../ogl2`: `.venv/bin/python -m pytest ../ogl2/tests/ -x -q`.
- Parsing invariants live in `src/tests/` — if you touch the AST visitor, `test_parse_bugs*` and
  `test_parse_type_annotations` are the ones that fail first.

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
