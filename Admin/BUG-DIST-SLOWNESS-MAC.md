# BUG: CI-built Mac app slow (drag/resize), local build fast

**Status: ROOT CAUSE FOUND, FIXED, VERIFIED AND MERGED INTO `2026-dustoff`.**

Two changes shipped (2026-11-03):
1. build with **python-build-standalone (uv)**, not `setup-python`'s framework Python
   -> the drag freeze is gone (the actual bug);
2. **onedir** bundling instead of onefile -> launch 8.3/1.9 s -> **0.4 s** (sections 12) .

Verified on CI build 11 (`pynsource-macos-2026-dustoff-11`, run 41442554914) and
hand-tested: "the build runs perfectly and starts super fast".

Short version: the CI build baked in a **framework-built Python** (python.org, via
`actions/setup-python`). A framework Python plus **wxasync**'s macOS event loop makes the wx
event pump stop for the entire duration of a mouse drag, so the canvas never repaints until
the mouse pauses or is released. The local build used uv's **python-build-standalone**
(shared `libpython3.13.dylib`) and is unaffected. Fix: build with python-build-standalone
(uv) instead of `setup-python`, plus a CI guard that fails the build if a framework
interpreter sneaks back in.

Environment these measurements were taken on: macOS 27.0.1 (26A434), arm64,
wxPython 4.3.2 (wxWidgets 3.3.4), PyInstaller 6.22.3, Pynsource 1.85 `2026-dustoff`.

---

## 1. Symptom (as originally reported)

CI-built `Pynsource.app` (runs `2026-dustoff-8/9`):

1. ~18 s cold start, ~5 s afterwards (Gatekeeper hashing of a fully-sealed ad-hoc signature;
   not part of this bug).
2. Opens behind other windows — fixed separately (`frame.Raise()` + `osascript activate`).
3. **Dragging boxes / zooming / window resize: jerky, no live feedback; the canvas only
   redraws when the mouse pauses or is released.** Menu zoom (`Cmd+=`) is instant.
   The local PyInstaller build of the same source is smooth.

## 2. Root cause

`src/app/settings.py` has `ASYNC = True`, so the GUI runs on
`wxasync.WxAsyncApp.MainLoop` (`src/pynsource_gui.py::run`). On macOS that loop is:

```python
async def MainLoop(self):                    # wxasync.py
    evtloop = wx.GUIEventLoop()
    with wx.EventLoopActivator(evtloop):
        while not self.exiting:
            if IS_MAC:
                evtloop.DispatchTimeout(0)   # pumps ONE wx event ...
            ...
            await asyncio.sleep(self.sleep_duration)   # ... per 20 ms
```

With a **framework** Python, while a mouse button is held the wx side of that pump stops
delivering timer and paint events. The asyncio side keeps ticking (its selector asks for
20 ms and blocks 21 ms the whole time), so this is *not* a kernel timeout, App Nap or
thread-priority effect — it is the wx event pump going quiet during the drag.

Result: drag/motion events still reach Python and still call `Refresh()`, but the paint
never materialises, so the canvas looks frozen until the drag ends and everything flushes.
That is exactly the reported symptom, including "resize behaves like drag" (both keep the
button/tracking state active) and "menu zoom is instant" (a discrete, no-button interaction).

### Why framework vs shared changes anything at all

Not yet explained at the wxWidgets/AppKit level, and it deserves an upstream report. What we
do know, measured:

* wxPython itself is irrelevant: the two shipped bundles' `wx/_core.so`,
  `libwx_osx_cocoau_core`, `siplib` are byte-identical apart from `LC_UUID` (2 bytes).
* The same wx code under a plain `wx.App.MainLoop` is fast with the *same* framework
  interpreter (§4.3) — so it is the combination, not Python nor wx alone.
* `asyncio.sleep(0.02)` is punctual in all three interpreters tested (47.6/s, max 25 ms),
  so asyncio's own timer resolution is fine.

## 3. Evidence: Pynsource, same code, only the interpreter differs

Method: identical tree, identical wxPython, identical sample diagram
(`src/samples/multi level inheritance.pyns`, 24 shapes), driven by an identical scripted
drag: press **on a shape**, click to select, then ~830 left-button drag events in a circle
over 8 s (`CGEventPost` via a small Swift helper), then release. Counters come from an
env-gated probe (`PERF_LOG`) that patches the canvas paint/motion handlers and also runs a
`wx.Timer` at 8 ms.

| build | interpreter | drag events/s | paints/s | shape travel |
|---|---|---|---|---|
| onefile (shared libpython) | 3.13.14 PBS | 37 | **53.6** | ~200 px |
| onefile (framework) | 3.13.18 brew | 44 | **6.4** | 57 px |
| onefile (framework) | 3.13.18 brew | 45 | **7.1** | 57 px |
| onedir (shared libpython) | 3.13.14 PBS | 40.6 | 50.8 | — |
| Community edition, onefile | 3.13.14 PBS | 33.6 | 44.6 | — |

From the slow build's probe log — the smoking gun is the timer gap, not the event count:

```
t=14.5  ... ticks=248  paint=203  max_gap_ms=503
t=23.5  ... ticks=276  paint=221  max_gap_ms=8200     <-- 8.2 s with no timer tick
```

During that 8 s the app still processed 359 drag events and called `Refresh()` 387 times
(251 → 638), but only 18 paints happened. Average paint cost stayed ~2.8 ms, so painting
itself is not slow — it just is not being asked to happen.

Note the framework build receives *more* drag events than the shared build (44/s vs 37/s),
which rules out "the events are being lost".

## 4. Evidence: minimal reproducers (no Pynsource code)

### 4.1 Pure asyncio — control

`asyncio.sleep(0.02)` in a bare loop, 300 iterations:

| interpreter | median | max | effective rate |
|---|---|---|---|
| shared 3.13.16 (PBS) | 21.1 ms | 21.3 ms | 47.6/s |
| framework 3.13.18 (brew) | 21.1 ms | 25.1 ms | 47.5/s |
| shared 3.13.16 | 21.1 ms | 23.3 ms | 47.6/s |

⇒ asyncio is punctual everywhere. Not the culprit on its own.

### 4.2 Plain wx main loop — control

60-line app: frame + child window, `wx.Timer(8 ms)` that calls `Refresh()`, counts paints,
EVT_MOTION; identical scripted drag.

| interpreter | loop | paints/s | worst stall |
|---|---|---|---|
| framework 3.13.18 | `wx.App.MainLoop` | **119.4** | 31 ms |
| shared 3.13.16 | `wx.App.MainLoop` | 119.6 | 44 ms |

⇒ plain wx is fine with framework Python.

### 4.3 Same app through wxasync's loop — reproduces the bug

| interpreter | loop | paints/s | worst stall |
|---|---|---|---|
| shared 3.13.16 | `wxasync.WxAsyncApp.MainLoop` | **43.4** | 140 ms |
| framework 3.13.18 | `wxasync.WxAsyncApp.MainLoop` | **6.2** | **8140 ms** (= the drag) |

⇒ minimal reproduction: **wx + wxasync's macOS pump + framework Python**. This is the
test case to send upstream (wxPython? wxasync? cpython-build-macos? TBD).

## 5. What was ruled out (and how)

| Theory | Verdict | Evidence |
|---|---|---|
| wxPython version/build differs | **dead** | extracted both bundles' `wx` binaries: identical but `LC_UUID` |
| onefile vs onedir | **dead** | 40.9 vs 40.6 drag events/s, 50.6 vs 50.8 paints/s |
| Pro (ogl2 canvas) vs Community (classic OGL) | **dead** | 40.9 vs 33.6 events/s; both fine. (Community is lower by design — classic OGL drops sub-tolerance movement.) The shipped CI app logs `PRO=True`, same as local. |
| PyInstaller version / SDK stamp | **dead** | bootloader differs only by build-SDK string (`sdk 26.2` vs `sdk 15.5`) and UUID |
| Quarantine / location / translocation | **dead** | no `com.apple.quarantine`; slowness followed the file, not the folder (as noted originally) |
| Activation | **real bug, separate** | fixed earlier; did not change drag perf |
| App Nap / kernel timer coalescing / QoS | **dead** | instrumented asyncio selector: both builds ask 20 ms and block 21 ms throughout |
| "Only 19 drag events reach Python" | **measurement artefact** | see §6 |

## 6. Why the original `sample` forensics misled

The earlier analysis concluded that in the CI build "~19 drag events reach Python" and
"paints draw almost nothing (~3 `DrawText`)", from `sample` symbol counts.

That method does not measure what it appears to. A build that provably receives ~325 drag
events in 8 s still reports:

```
_handleMouseDraggedEvent=1   DoDrawText=0   drawRect=6   PyEval_EvalFrameDefault=49
```

So those counts are sampling noise (wx/Python handlers are sub-millisecond, and `sample`
rarely catches them), and comparisons based on them are meaningless. The *real* signal in
the same situation is the **wx.Timer cadence** and the paint count, which is what the probe
used instead.

Related trap: `ps -o %cpu` / CPU-seconds during a drag differ only ~20% between the fast and
slow builds, so they are not a usable discriminator either.

## 7. Fix applied

`.github/workflows/build-mac.yml`:

* Replaced `actions/setup-python@v5` (python.org **framework** build) with
  `astral-sh/setup-uv@v5` and:

  ```yaml
  uv python install 3.13
  uv venv --python 3.13 --python-preference only-managed .venv
  echo "$PWD/.venv/bin" >> "$GITHUB_PATH"
  uv pip install --python .venv/bin/python wheel wxpython pyinstaller
  uv pip install --python .venv/bin/python -r pynsource/requirements.txt
  uv pip install --python .venv/bin/python alsm/
  ```

  `UV_PYTHON_PREFERENCE=only-managed` is deliberate: it stops uv from falling back to a
  framework interpreter that happens to be on the runner.

* Added a **guard step** that fails the build if the bundle contains a framework
  interpreter, so this cannot silently regress:

  ```
  Guard - the bundled interpreter must not be a framework build
  # greps pyi-archive_viewer output: fails on Python.framework, requires libpython3
  ```

### How to tell which kind of Python a build has

* Interpreter: `python3 -c "import sys; print(sys._framework)"` → `'Python'` = framework,
  `None`/`''` = shared (python-build-standalone).
* A built bundle: `pyi-archive_viewer -l Pynsource.app/Contents/MacOS/Pynsource | grep -E "libpython3|Python.framework"`
  * shared build → `libpython3.13.dylib` (~17 MB)
  * framework build → `Python.framework/Versions/3.13/Python` (~6.7 MB) + `libssl.3.dylib`,
    `libcrypto.3.dylib`, `python3.13/lib-dynload/*.so`

### Verification of the new CI artefact

First build with the fix: run `41438646072` on branch `ci/uv-python-drag-fix`. The log shows
`BUILD PYTHON 3.13.18 framework= ''`, PyInstaller reports
`Using Python shared library: .../cpython-3.13.18-macos-aarch64-none/lib/libpython3.13.dylib`,
and the guard step lists `libpython3.13.dylib` (17.6 MB) with no `Python.framework`.

Handy side effect: the new CI build runs CPython **3.13.18 shared**, i.e. the same version as
the framework build that froze — so the framework/shared comparison is now version-for-version
and not confounded by the patch level.

* `sys._framework` in the build log (the workflow prints `BUILD PYTHON ...`).
* the guard step's `pyi-archive_viewer` output.
* manual: open the sample diagram, drag a class box in a circle — it must track the cursor
  continuously, not snap on release. **Done on build 10: passes** (smooth drag, live resize,
  responsive zoom).

## 8. Alternative fixes (if framework Python must be kept)

1. **Drop wxasync's macOS pump** — `ASYNC = False` uses plain `App.MainLoop`, which is
   measured fast (119 paints/s) under the very same framework interpreter. Not yet validated
   end-to-end in Pynsource (my instrumented `ASYNC=False` run failed to load a diagram before
   the probe measured anything), but the equivalent minimal app is unaffected.
2. **Fix the pump** in wxasync: drive wx from a `wx.Timer` (or `evtloop.Dispatch()` in a
   tight loop) instead of `DispatchTimeout(0)` + `asyncio.sleep(0.02)`, so a held mouse
   button cannot starve the wx timer/paint path.
3. Report upstream with the §4.3 reproducer. This looks like a genuine
   "framework CPython build + wxasync" defect on macOS, not project-specific.

## 9. `ast.Constant` handled through the removed `.s` alias (fixed)

Both copies of the ALSM visitor had this:

```python
def visit_Constant(self, node):
    self.write(repr(node.s))        # ast.Constant has .value; .s belonged to ast.Str
```

* `../alsm/alsm/python/python_ast.py` (fixed in alsm `59bd0a1`)
* `src/parsing/core_parser_ast.py` (its fork - fixed in pynsource `617a2e6`)

**How it manifested:** it did *not* fail on Python 3.13. `ast.Constant` kept `.s` as a
deprecated compatibility property, so every import worked. Python **3.14 removed those
aliases**, so the first string/number literal the visitor reaches raises
`AttributeError: 'Constant' object has no attribute 's'`. alsm catches it in
`_convert_ast_to_alsm` and records "Error during conversion of python AST into ALSM model",
which the app shows as a dialog, leaving the module model incomplete (module visualisation
silently degraded). That is the popup seen while evaluating Python 3.14 - nothing to do with
the drag bug, and invisible on 3.13, which is why it went unnoticed.

Proven before/after on a 6-line file containing `X = "abc"`, `Y = 42` and a docstring:

```
3.13 before/after : error = None
3.14 before       : error = "Error during conversion of python AST into ALSM model: 'Constant' object has no attribute 's'"
3.14 after        : error = None
```

Fix is `node.value`; the old `visit_Str`/`visit_Bytes`/`visit_Num` branches remain for
pre-3.8 nodes. 158 unit tests OK (8 skipped) after the change.

## 10. Measurement harness (how to repeat any of this)

Input side, per run:

1. Launch the app; wait for its window.
2. `raise` the window through the Accessibility API and **verify** with a hit-test that the
   point actually belongs to the app — otherwise the drag goes to whatever is on top (a
   notification banner or a modal dialog will silently invalidate a run; both happened).
3. Click once on a **known shape position** (the probe reports hit-points) so a shape is
   selected, then post `mouseDown` + ~120 Hz `mouseDragged` in a circle + `mouseUp`.
   Always run a watchdog that posts `mouseUp`, and never kill the app while a button is down
   (a synthetic button-left-down after the owning process dies pins the system cursor).

Measurement side, in-app (env-gated `PERF_LOG`, removed from the shipped branch):

* counts `EVT_MOTION`, `Dragging()`, paint entries, paint wall time, and the shape position
  per second (proves a shape really moved);
* runs an 8 ms `wx.Timer` and records gaps > 50 ms → the event-pump starvation signal;
* logs the canvas screen rect and shape hit-points so the input side can aim precisely.

Guard rails learned the hard way: a probe holding a `wx.Timer` can segfault on interpreter
teardown (`wxPyCallback::~wxPyCallback`); stop and drop the timer on exit.

## 11. Open questions

* Why does a framework Python change AppKit/wx event dispatch at all? Worth an upstream
  report with the §4.3 reproducer.
* Does the freeze also affect the `resize` path in the same way (it should — same pump), and
  does `X`/`Y` matrix of `ASYNC` × interpreter show `ASYNC=False` as a complete workaround?
* Should `ASYNC` be revisited on macOS in any case? `DispatchTimeout(0)` caps UI throughput
  at one wx event per 20 ms (≈50 Hz) even in the best case.

## 12. Follow-up: onefile -> onedir (startup, and PyInstaller 7)

Not a drag-perf issue at all: onedir vs onefile measured the same while running
(40.6 vs 40.9 drag events/s - i.e. noise, no claim either way).

The real difference is **launch time**, measured as launch -> window appears:

| build | rep 1 | rep 2 | rep 3 |
|---|---|---|---|
| onefile (CI build 10) | 8.3 s | 1.9 s | 1.9 s |
| onefile (local rebuild) | 8.9 s | 2.2 s | 1.9 s |
| **onedir (local rebuild)** | **0.5 s** | **0.4 s** | **0.4 s** |

Why: onefile unpacks the whole archive into a fresh `_MEIxxxx` temp directory on **every**
launch (hence ~2 s even when warm), and the single 33 MB executable carries a whole-file
ad-hoc seal (thousands of hashes) that macOS must verify on first launch (hence ~8-9 s cold,
the "18 s" in the original report was the same effect on older, more heavily sealed builds).
A onedir bundle runs straight out of the bundle and signs each file separately.

Why it mattered at all (independent of performance): PyInstaller 6.22 already printed

> Onefile mode in combination with macOS .app bundles (windowed mode) don't make sense
> (a .app bundle can not be a single file) and clashes with macOS's security.
> Please migrate to onedir mode. This will become an error in v7.0.

Migration done (`../ogl2/bin/pynsource-github-actions.spec`, commit `cd7e737`): keep
`Analysis`/`PYZ`, use `EXE(pyz, a.scripts, [], exclude_binaries=True)` + `COLLECT(...)`, and
wrap the collected directory in `BUNDLE(coll, ...)`.

Resulting bundle layout (verified on a local build of `2026-dustoff`):

```
Contents/MacOS/Pynsource        9.4 MB   bootloader + PYZ
Contents/Frameworks/*          78.0 MB   114 files: libpython3.13.dylib, wx, numpy, datas
Contents/Resources/*                     symlinks -> ../Frameworks/... (+ pynsource.icns)
Contents/Info.plist                      unchanged (same bundle id, NSHighResolutionCapable)
Contents/_CodeSignature                  571 hashes (was 8031)
```

Measured after the change:

| check | result |
|---|---|
| launch -> window | 0.9 s first run, then **0.4 s** (was 8.3 / 1.9 s) |
| download zip | **32.5 MB** with `ditto -c -k`, 35.0 MB with `zip -r -y` (onefile was 33.7 MB) |
| zip without `-y` | 83 MB - `zip -r` follows the `Contents/Resources` symlinks and stores the payload twice |
| `codesign --verify --deep --strict` | OK, ad-hoc, bundle id `com.pynsource.pynsource` |
| ditto round-trip (zip -> unzip -> launch) | symlinks preserved, signature valid, 0.5 s launch |
| icon / Info.plist | `pynsource.icns` in Resources, `CFBundleIconFile` set |

Also updated: `.github/workflows/build-mac.yml` (guard now checks the onedir layout +
`libpython3*.dylib` and runs `codesign --verify`; zip uses `-y`; the redundant
`dist/Pynsource/` COLLECT directory is deleted so the artifact isn't doubled) and
`../ogl2/bin/buildmac.sh` (dist now holds both the payload dir and the `.app`; only the
`.app` ships).

## 13. Current deployment recipe (mac)

* **CI**: `.github/workflows/build-mac.yml`. Builds on `pre-*` tags (draft pre-release) and
  on manual dispatch (artifact only). This is the only supported way to produce a mac app.
* **Interpreter**: `astral-sh/setup-uv` + `uv python install 3.13` +
  `UV_PYTHON_PREFERENCE=only-managed`. Never `actions/setup-python` (framework Python).
  The workflow prints `BUILD PYTHON ... framework=''` and a guard step fails the build if a
  framework interpreter or a onefile layout appears.
* **Bundling**: onedir (`EXE(exclude_binaries=True)` + `COLLECT` + `BUNDLE`) in
  `../ogl2/bin/pynsource-github-actions.spec`. `dist/` then holds both `dist/Pynsource/`
  (COLLECT output) and `dist/Pynsource.app`; only the `.app` ships, and the COLLECT dir is
  deleted so the artifact is not doubled.
* **Zip**: `zip -r -y` (or `ditto -c -k --keepParent`). Without `-y` zip follows the
  `Contents/Resources` symlinks and stores the payload twice (83 MB vs 35 MB).
* **Signing**: ad-hoc only (no Apple Developer account), so users still run
  `fix-permissions.command` after unzipping. `codesign --verify --deep --strict` is part of
  the guard step.
* **Local build** (occasional): `bin/buildmac.sh`, which needs `pyinstaller` on PATH; it
  ships the `.app` and zips with `-y` too. Prefer CI - a local build silently depends on
  whichever Python is on PATH, which is exactly how this bug was born.
