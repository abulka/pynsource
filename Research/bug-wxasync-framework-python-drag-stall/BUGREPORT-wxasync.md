# wxasync: `WxAsyncApp.MainLoop` stalls (no wx timer/paint events) while the mouse button is held, when Python is a framework build (macOS)

Ready-to-file issue text. Target: <https://github.com/sirk390/wxasync/issues> — see the last
section if it turns out to belong to wxPython instead.

---

**Environment**

* macOS 27.0.1 (26A434), arm64 (Apple silicon)
* wxPython 4.3.2 / wxWidgets 3.3.4 (same wheel for every interpreter tested — verified
  byte-identical except `LC_UUID`)
* wxasync 0.49
* CPython 3.13.18 *framework* build (Homebrew; `sys._framework == 'Python'`) — **affected**
* CPython 3.13.16 / 3.13.18 *shared-library* build (python-build-standalone / uv,
  `sys._framework` empty) — **not affected**

**Summary**

With a framework-built CPython on macOS, `WxAsyncApp.MainLoop` stops delivering wx timer and
paint events for as long as a mouse button is held down. Drag a window's contents and the
canvas freezes; on release everything catches up in one go. Replacing the wxasync loop with a
plain `wx.App.MainLoop` in the same process/interpreter removes the problem entirely, so the
interpreter and wxPython are individually fine — it is the combination with wxasync's loop.

**Reproducer** (attached: `wxasync_repro.py`, plus `wx_control.py` control,
`asyncio_control.py` control, `auto_drag.swift` optional input helper)

A window repaints itself from an 8 ms `wx.Timer`, counts paints, logs once per second.

```bash
pip install wxpython wxasync
LOG=/tmp/fw.log /path/to/framework/python wxasync_repro.py   # affected
# drag inside the window in a circle for ~5 seconds, then read /tmp/fw.log
```

**Actual**

On the framework interpreter, the per-second lines stop for the whole duration of the drag
and the worst timer gap equals the drag length:

```
t= 14.5 paints/s=  47.9 motion=  1 drag=  0 down=1 maxgap=   503ms
t= 23.5 paints/s=   9.2 motion=381 drag=377 down=2 maxgap=  8140ms   <-- 8.2 s hole
```

paints/second during a 5 s drag: **6.2** (worst gap 8140 ms).

**Expected**

Continuous repainting while dragging; `wx_control.py` (plain `wx.App.MainLoop`) in the same
framework interpreter gives **119.4 paints/s**, worst gap 31 ms. The same `wxasync_repro.py`
on a shared-library CPython gives **43.4 paints/s**, worst gap 140 ms.

**What it is not**

* Not event loss: motion/drag counts keep rising during the stall (`drag=377`), and the app's
  own `Refresh()` calls keep being made; only timer/paint delivery stops.
* Not asyncio's timer resolution: `asyncio.sleep(0.02)` in a bare loop wakes at ~47.6/s with
  a 25 ms worst case on the same interpreter (`asyncio_control.py`).
* Not App Nap / kernel coalescing: instrumenting the running loop's selector shows
  `select(timeout=20ms)` asked for and ~21 ms actually blocked for the whole stall, i.e. the
  asyncio side of the loop keeps ticking normally. The wx side is what goes quiet.
* Not wx itself: identical wxPython binaries, and the plain loop is smooth.

**Notes on `MainLoop`**

```python
async def MainLoop(self):
    evtloop = wx.GUIEventLoop()
    with wx.EventLoopActivator(evtloop):
        while not self.exiting:
            if IS_MAC:
                evtloop.DispatchTimeout(0)              # one wx event per iteration
            else:
                while evtloop.Pending():
                    evtloop.Dispatch()
                    await asyncio.sleep(0)
            await asyncio.sleep(self.sleep_duration)    # default 20 ms
```

Two observations that may be related:

1. On macOS only a single event is pumped per iteration (`DispatchTimeout(0)`), so UI
   throughput is capped at ~50 Hz even when everything works; on a framework interpreter that
   same call appears to stop returning wx timer/paint events while a button is held.
2. If the pump were driven by a `wx.Timer` (or `evtloop.Dispatch()` in a tight loop) instead
   of `DispatchTimeout(0)` + `asyncio.sleep(0.02)`, a held mouse button presumably could not
   starve the timer/paint path. I have not verified a patch — happy to test one.

**Related real-app report**

Same wedge in Pynsource (UML editor on wxasync): 8 s scripted drag on a 24-shape diagram,
shared interpreter 53 paints/s vs framework interpreter 8 paints/s; the canvas visibly only
updates when the mouse pauses. Fixed for now by building with python-build-standalone.

---

## If this belongs to wxPython instead

Please move/close-as-upstream and file at <https://github.com/wxWidgets/Phoenix/issues> with
this text; the claim to test there is narrower:

> On macOS, `wx.GUIEventLoop.DispatchTimeout(0)` (inside an `EventLoopActivator`) stops
> dispatching `wx.Timer` events and stops servicing pending paints while a mouse button is
> held, but only when the process runs a framework-built CPython (`sys._framework ==
> 'Python'`). Same wxPython wheel, same code: a plain `App.MainLoop` is unaffected, and a
> shared-library CPython is unaffected.
