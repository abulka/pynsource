# Bug: wxasync's macOS event loop stalls while the mouse button is held — only with a *framework* Python

Minimal reproduction of the defect behind `BUG-DIST-SLOWNESS-MAC.md` (Pynsource's
CI-built Mac app being unresponsive while dragging, while a locally-built app was fine).

Everything here is plain wx + wxasync: **no Pynsource code involved.**

## The finding in one table

Same scripts, same wxPython 4.3.2 (wxWidgets 3.3.4), same machine, macOS 27.0.1 (26A434),
arm64. Only the interpreter build and the event loop differ. Numbers are paints/second
counted by an 8 ms `wx.Timer` while the mouse is dragged in a circle for ~5 s.

| script | event loop | interpreter | paints/s | worst timer gap |
|---|---|---|---|---|
| `wx_control.py` | `wx.App.MainLoop` | framework 3.13.18 (Homebrew) | 119.4 | 31 ms |
| `wx_control.py` | `wx.App.MainLoop` | shared 3.13.16 (python-build-standalone) | 119.6 | 44 ms |
| `wxasync_repro.py` | `wxasync.WxAsyncApp.MainLoop` | shared 3.13.16 | 43.4 | 140 ms |
| `wxasync_repro.py` | `wxasync.WxAsyncApp.MainLoop` | **framework 3.13.18** | **6.2** | **8140 ms** |

The 8140 ms worst gap equals the drag duration: the wx side of the loop delivers no timer
or paint events until the button is released, then everything flushes. Motion/drag events
themselves keep arriving (the counts increase during the stall), so this is not event loss.

`asyncio_control.py` shows `asyncio.sleep(0.02)` is punctual on all of these interpreters
(~47.6 wakes/s, max 25 ms), so asyncio's timer resolution is not the cause.

The same wedge in a real app: Pynsource on wxasync, 8 s scripted drag on a 24-shape diagram.

| interpreter | drag events/s | paints/s | shape travel |
|---|---|---|---|
| shared 3.13.14 (python-build-standalone) | 37 | 53 | ~200 px |
| shared 3.13.16 | 37 | 51 | ~200 px |
| framework 3.13.18 | 44 | 8 | 57 px |

Verified from this exact directory (scripted 5 s drag, numbers vary a little with machine load):

```
framework 3.13.18 : t=2.1 ... t=7.9   <- 5.1 s hole = the 5 s drag, maxgap 5101 ms, 8.5 paints/s
shared    3.13.16 : continuous lines,                        maxgap  144 ms, 41.6 paints/s
```

## Are you on a framework Python?

```
python3 -c "import sys; print(repr(sys._framework))"
```

* `'Python'` → framework build (python.org installer, Homebrew, `actions/setup-python`)
* `None` / `''` → shared library build (`libpython3.x.dylib`, python-build-standalone / uv)

## Reproduce by hand (no tooling needed)

```bash
pip install wxpython wxasync

# affected: framework python.  unaffected: python-build-standalone (uv)
LOG=/tmp/fw.log    /path/to/framework/python    wxasync_repro.py
LOG=/tmp/pbs.log   /path/to/shared/python      wxasync_repro.py

# control: same window, plain wx loop - smooth on both
LOG=/tmp/ctl.log   /path/to/framework/python    wx_control.py
```

Then **drag inside the window in a circle for ~5 seconds**. Watch the per-second lines in
the terminal: on the affected build they stop for the whole drag and `maxgap` jumps to
thousands of ms; the canvas also visibly freezes and snaps on release. On a healthy build
the lines keep coming and `maxgap` stays in the tens of ms.

### Optional: hands-free variant

`auto_drag.swift` posts a synthetic 8 s circular drag (needs Accessibility permission for
the terminal). It is what produced the numbers above.

```bash
swiftc -O auto_drag.swift -o auto_drag
LOG=/tmp/x.log /path/to/python wxasync_repro.py &   # then:
./auto_drag <window-centre-x> <window-centre-y> 100 8   # x y radius seconds
```

It always posts a mouse-up at the end, and it is worth keeping that guarantee if you modify
it: a synthetic mouse-down whose owning process dies can leave the system cursor pinned
until another mouse-up is posted.

## Where the code stands (context for the report)

`wxasync.py` (0.49) drives wx from asyncio on macOS like this:

```python
async def MainLoop(self):
    evtloop = wx.GUIEventLoop()
    with wx.EventLoopActivator(evtloop):
        while not self.exiting:
            if IS_MAC:
                evtloop.DispatchTimeout(0)          # pumps one wx event
            ...
            await asyncio.sleep(self.sleep_duration)  # 20 ms
```

During a held-button drag on the affected interpreter the `DispatchTimeout(0)` side stops
producing timer/paint events while the asyncio side keeps ticking at ~50 Hz (instrumenting
`loop._selector.select` shows `timeout=20ms` asked and ~21 ms blocked throughout, so the
kernel is behaving). Caveat: also one wx event per iteration caps UI throughput at ~50 Hz
even in the good case, which is worth a look independently.

## Which project owns this?

Unknown as yet; that is why the report is drafted to be portable:

* **wxasync** is the most likely owner, since swapping to a plain `wx.App.MainLoop` fixes it
  with the very same framework interpreter (`wx_control.py`).
* It could also be a wxPython/wxWidgets issue in `wxGUIEventLoop::DispatchTimeout` on
  framework Pythons (wx binaries here are identical across the affected/unaffected builds —
  verified byte-for-byte apart from `LC_UUID`), in which case wxasync would be forwarding an
  upstream bug and the report should move there.

See `BUGREPORT-wxasync.md` for the ready-to-file issue text.
