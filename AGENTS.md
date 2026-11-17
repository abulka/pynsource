# AGENTS.md — Pynsource contributor notes (for LLM sessions)

## What this is
Pynsource: reverse-engineers Python source into UML class diagrams (wxPython GUI + CLI).
The diagram canvas is `wxdiagram` and is free for everyone. `PRO_EDITION` now gates
only module visualisation (ALSM) on macOS/Windows; it is free on Linux builds.

## Layout
- `src/` — all code. Entry points: `src/pynsource_gui.py` (GUI), `src/pynsource_cli.py` (CLI).
- `src/parsing/` — AST parser (`core_parser_ast.py`, visitor builds pmodel).
- `src/gui/uml_canvas.py` — the application canvas, built on `wxdiagram`.
- `src/gui/settings.py` — `PRO_EDITION` / `ALSM_PARSING` flags, `APP_VERSION` / `PATCH` version source.
- `bin/run` — runs GUI (`cd src && python3 pynsource_gui.py`). `bin/testall` — full test suite,
  wx included (needs a display; `xvfb-run -a bin/testall` on a headless box).
- Docs are split deliberately: `README.md` = pitch + install table, `DOWNLOADS.md` = the only
  install/troubleshooting reference (linked from the website), `BUILDING.md` = the only developer
  doc. Do not duplicate build/run/test instructions here — point at BUILDING.md.
  `Admin/ROADMAP.md` = release status + future milestones; working plans for a session stay
  outside the repo.
- `requirements.txt` — install with `uv pip install -r requirements.txt`.
- `setup.py` — legacy; reads `.requirement-extras/requirements-linux-22.txt`. Prefer `uv` + running
  from source over `pip install -e .`.
- No URL shortener anywhere: the update check reads raw.githubusercontent, the website links
  at release assets, and `Admin/release-links/release_links.py <tag>` prints the links. bit.ly is
  retired (paid now, and its links rotted).
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
- `../wxdiagram` (`wxdiagram` package, 0.2.x) — the canvas library (shapes, connectors,
  selection, zoom/pan, JSON persistence). Pynsource uses it on every platform and edition.
  Install: `uv pip install -e ../wxdiagram`. PyPI: `wxdiagram>=0.2,<0.3`.
- `../pynsource-rego` (`rego` package) — licensing. `PRO_EDITION = rego.are_registered(APP_VERSION)`
  (`int(APP_VERSION)` + 5-version forward window, so 1.x bumps keep old licenses; never jump to 2.x
  lightly). Self-sign: `cd ../pynsource-rego && ../pynsource/.venv/bin/python rego_gen.py gen <Name> --version 1 --save`.
  Install: `uv pip install -e ../pynsource-rego`. Needed NO changes for 3.13 (pure stdlib:
  hashlib/json/click/appdirs) — verified clean.
- `../alsm` (`alsm` package) — module visualisation (`ALSM_PARSING`). Parser is a fork of ours;
  keep `alsm/python/python_ast.py` in sync with `src/parsing/core_parser_ast.py` re typed_ast handling.
  Install: `uv pip install -e ../alsm`. (Its `typed-ast` pin was removed 2026-11.)

## Free canvas vs Pro module visualisation
There is one canvas on every platform and edition: `wxdiagram` via `src/gui/uml_canvas.py`.
Zoom, pan, drag-to-connect, resize and layout are free.
- **Community** (no `rego` installed, or no valid licence): everything except module
  visualisation. `PRO_EDITION=False`, `ALSM_PARSING=False`.
- **Pro** (rego installed + valid licence, or Linux): module visualisation is enabled when
  `alsm` is importable (`ALSM_PARSING=True`). The licence check is `rego.are_registered(APP_VERSION)`;
  it uses `int(APP_VERSION)` with a 5-version forward window, so 1.x bumps keep old licences.
  Never jump to 2.x without re-issuing keys.
- **Linux is Pro by platform**: `sys.platform.startswith("linux")` forces `PRO_EDITION=True`
  (snaps cannot persist a licence file). Every Linux artefact must bundle `wxdiagram` + `alsm`.
- `print("Running Community Edition")` at startup tells you which you got.

## Deploying (Mac)
- Only supported route: CI `.github/workflows/build-mac.yml` — a `pre-*` or `version-*` tag builds
  a draft release (+ artifact), manual dispatch gives an artifact only. `macos-14` is retired:
  the runner is `macos-15`.
- The build **must** use uv's python-build-standalone, never `actions/setup-python`: a
  framework Python plus wxasync's macOS loop freezes the canvas for the whole duration of a
  mouse drag. Full write-up: `Admin/BUG-DIST-SLOWNESS-MAC.md`. The workflow prints
  `BUILD PYTHON ... framework=''` and a guard step fails the build if a framework interpreter
  or a onefile layout reappears.
- Bundling is **onedir** (`bin/pynsource-github-actions.spec`): launch 0.4s vs 1.9s
  for onefile, and PyInstaller 7 rejects onefile + `.app`. `dist/` then contains both
  `dist/Pynsource/` (COLLECT output — delete it, it is duplicated inside the app) and
  `dist/Pynsource.app` (what ships).
- Zip with `-y` (`zip -r -y`, or `ditto -c -k --keepParent`); without it the
  `Contents/Resources` symlinks are followed and the payload is stored twice (83MB vs 35MB).
- Builds are **arm64 only, by decision** (macos-15 runner; macos-14 was retired by GitHub on
  2026-11-02, which cancels the job in 1s with "configuration ... is not supported"). Intel Macs
  stop at 1.84 — an Intel job is possible (`macos-15-intel`, x86_64 wxPython wheels exist) but
  GitHub retires those runners in Aug 2027 and universal2 is not a one-liner (per-arch wheels).
- Ad-hoc signed only (no Apple Developer account). Users must clear the Gatekeeper block
  once: `Done` on the block dialog, then System Settings > Privacy & Security > Open Anyway
  (twice) — see `.deploy-extras/macos/IMPORTANT-README-BEFORE-RUNNING.txt`, which is also the
  draft release body. No helper script ships any more (an unsigned `.command` just added a
  second identical block).
- **macOS window activation is a deliberate frozen-only workaround.** An ad-hoc-signed `.app`
  launched from Finder can open behind Terminal/Finder, and `wx.Frame.Raise()` only raises the
  window *inside* the app. `MainApp.OnInit` therefore always calls `self.frame.Raise()`, and in a
  frozen build only runs `open -a <this .app>` to activate the bundle **by path**.
  Do **not** replace it with
  `osascript -e 'tell application "Pynsource" to activate'`: AppleScript resolves the app by
  name through LaunchServices and launches it if it is not running. That is what made a source
  run of 1.87 start the separately installed 1.86 app alongside it. Source runs must skip the
  native activation entirely. Original workaround: commit `37ee7da` (1.86). If a future macOS
  stops opening the bundle behind other windows, test from Finder and then remove the
  frozen-only block.
- **macOS app-name trivia.** The top-left application menu is macOS's name for the running
  executable: the Python interpreter's bundle in a source run ("python"), `Pynsource` in the
  frozen `.app` (from `CFBundleName`). It is not reliably settable from inside an unbundled
  process. The auto-generated "Hide …"/"Quit …" items *are* settable, via
  `self.SetAppName(ABOUT_APPNAME)` / `SetAppDisplayName(...)` at the **start of `OnInit`**
  before any frame/menu exists; otherwise they say "Hide Pynsource_gui".
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
- Local `bin/buildmac` works but picks up whatever `python3`/`pyinstaller` is on PATH,
  which is exactly how the framework-Python bug got in. Prefer CI.
- **`actions/upload-artifact` does not preserve symlinks**, and the `.app` is full of them
  (`Contents/Resources`). The *artifact* copy therefore fails `codesign --verify --deep
  --strict` ("a sealed resource is missing or invalid") even when the build was fine — verify
  from the **release zip** instead, which CI creates before uploading.
- The spec and mac/win build scripts are now in this repo (`bin/`, `src/media/pynsource.icns`),
  so a spec change no longer needs a push to another repo. Use
  `gh workflow run build-mac.yml --ref wxdiagram-canvas` (artifact only) to validate it.

## Deploying (Windows)
- Route: CI `.github/workflows/build-win.yml` (windows-2022) — same triggers as Mac: a
  `pre-*`/`version-*` tag adds `pynsource-win-<tag>-setup.exe` to the draft pre-release, manual dispatch gives an
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
- **Linux is Pro-free by platform** (`src/gui/settings.py`), so `wxdiagram` and `alsm` are
  installed unconditionally: the venv must have them (`uv pip install -e wxdiagram/ -e pynsource-rego/ -e alsm/`),
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
  * The spec (`bin/pynsource-github-actions.spec`) drops the partial GTK stack it would
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
- Route: CI `.github/workflows/build-snap.yml` → `.snap` artifact; on `pre-*` and `version-*`
  tags it also `snapcraft upload ... --release edge`. **Stable is promoted by hand in the store UI** after a
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
- **Linux is Pro-free, so the snap must bundle wxdiagram + alsm** (checked out as siblings by the
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
- **Both arches are built natively** (`ubuntu-24.04` + `ubuntu-24.04-arm`): snapcraft cannot
  cross-compile wxPython, and the store then has amd64 *and* arm64 on edge. Getting arm64 to
  build took two fixes worth remembering (inside the part, `dpkg --print-architecture` came back
  empty — use `CRAFT_ARCH_BUILD_FOR`):
  * wx 4.2.5 does not compile with gcc 13 (core24): its bundled nanosvg uses unqualified
    `isnan()` — build with `CXXFLAGS="-include cmath"`.
  * `pip install --target` is invisible to a later pip run, so the bare `wxpython` line in
    `requirements-linux-common.txt` re-triggered a source build; the wheel must go in the *same*
    `pip install` command as the requirements file.

## Tests
- Expect `158 tests OK (skipped=8)`: `mkdir -p src/tests/logs && .venv/bin/python -m unittest
  discover -s src`. Most tests build a real `wx.App`, so a headless machine needs `xvfb-run` (the
  Linux CI does this); `TRAVIS=1` is a legacy flag that skips them all — never use it to validate.
- `../wxdiagram`: `.venv/bin/python -m pytest ../wxdiagram/tests/ -x -q`.
- Parsing invariants live in `src/tests/` — if you touch the AST visitor, `test_parse_bugs*` and
  `test_parse_type_annotations` are the ones that fail first.

## Gotchas / recent fixes (don't regress)
- **Print preview range**: `FilePrint` must build `wx.PrintDialogData(self.printData)` with
  Min/Max/From/To=1 + `EnablePageNumbers(False)` and pass THAT to `wx.PrintPreview`
  (passing bare `wx.PrintData` falls back to 1..9999 on Mac). `HasPage(page<=1)` +
  `GetPageInfo(1,1,1,1)` in `src/common/printframework.py` stay as belt-and-braces
  (wxPython has no `GetPagesInfo` binding).
- **Blurry UML text**: wxdiagram paints directly on `PaintDC`; pynsource sets
  `frame.SetDoubleBuffered(True)` to keep dragging smooth.
  sharpness fix is `int(round(...))` (not `int(...)`) in `DrawFormattedText` in BOTH
- Fonts: UML regions use `wx.MODERN` 10/14pt (`src/gui/uml_canvas.py`). Don't change
  families without a screenshot check.
- No `timeout(1)` on macOS — use `cmd & sleep; kill` pattern for GUI smoke tests.
