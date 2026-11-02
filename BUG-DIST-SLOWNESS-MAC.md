# BUG: CI-built Mac app slow (drag/resize), local build fast

**Status: ROOT CAUSE FOUND AND FIXED (branch `ci/uv-python-drag-fix`).**

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

* `sys._framework` in the build log (the workflow prints `BUILD PYTHON ...`).
* the guard step's `pyi-archive_viewer` output.
* manual: open the sample diagram, drag a class box in a circle — it must track the cursor
  continuously, not snap on release.

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

## 9. Side bug found while testing (unrelated, user-visible)

Importing any `.py` file (File → Import, or passing files on the command line) pops:

```
Error during conversion of python AST into ALSM model: 'Constant' object has no attribute 's'
```

The ALSM converter still uses the `ast.Str` / `node.s` alias that CPython removed; `ast`
gives `ast.Constant` with `.value`. Separate ticket — but it makes File → Import unusable in
current builds and blocks the module-visualisation path. (`../alsm` parser is a fork of
`src/parsing/core_parser_ast.py`; keep the typed_ast/`ast.Constant` handling in sync per
AGENTS.md.)

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
