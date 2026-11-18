# PlantUML view: quirks, workarounds and evidence

**Status: worked around in 1.87 (2026-11).** Nothing here is a Pynsource rendering bug — every quirk
below is the PlantUML *server* (or macOS's text substitution) misbehaving. Pynsource detects what it
can, retries, clamps and tells the user what happened.

Short version:

1. **PNG text is drawn by the server; SVG text is drawn by your browser.** That single asymmetry
   explains "save as SVG is fine but the PNG view is missing all its text".
2. The public server sometimes returns a PNG with **every label missing** (boxes and lines are drawn,
   glyphs are not), and it **crops anything wider than 4096 px** without warning.
3. `--|>` in the markup is easy to lose to **macOS "smart dashes"**, which turns it into `—|>`;
   every PlantUML version answers that with a Syntax Error.
4. Both are handled in `src/generate_code/gen_plantuml.py`; the user-facing knobs are
   **View → PlantUML Server…** and the status bar / view messages.

---

## 1. How the view renders

```
displaymodel_to_plantuml()            -> markup text (plain ASCII, one class per node)
plant_uml_create_png_and_return_image_url_async(markup, server, scale)
                                      -> PlantUmlRender(image_url, scale, too_wide, attempts)
plantuml.ViewImage(url=...)           -> ImageViewer fetches the PNG bytes
```

* URLs are built by `common/plantuml.py:plant_uml_url(text, fmt, server_url)` — the configured
  server is the `/uml` page endpoint; `png`/`svg` are siblings of it.
* The HiDPI trick: the app prepends `scale 2` to the markup, and the viewer starts zoomed out by
  `1/scale` (`zoom_initial`), so the picture looks the same size but is crisp on Retina.
  `PlantUmlScale` (config, 1–4, default 2) is the requested scale.
* Requests are cached twice: `alru_cache` on the render + SVG helpers in `gen_plantuml.py`, and
  `alru_cache` on `common/url_to_data.py:url_to_data`. Caches are cleared when the server/scale
  setting changes (`MainApp.OnPlantUmlServer`) and on connection errors (`clear_cos_connection_error`,
  `user_aborted`).

## 2. Quirk: PNG renders with no text at all

Symptom: class boxes, arrows and notes are drawn, notes are empty, every label is missing, and the
boxes are *narrow* (they collapse to the width of the class icon). SVG of the same diagram is fine
because the letters are not in the SVG at all.

Evidence (2026-11-18, `X-Powered-By: PlantUML Version 1.2026.9beta4`):

* The same diagram text, requested as 14 *different* URLs (only a comment line differs):
  10 came back with text, 4 without. 20 more samples: ~30 % without text.
* A text-less render is stable per URL: repeat requests return the identical bytes (`Age` header
  increments), because the CDN caches per URL for days. That is why refreshing the view never
  recovered and why the dev-mode demo looked permanently broken.
* The same text on `kroki.io` and on the atug/dokku servers rendered fine every time — so the markup
  and Pynsource's deflate encoding are not the problem.
* The PNG writes the correct diagram source into its own metadata, so the server *decoded* the right
  text; it is the glyph drawing that fails (font metrics measure zero width).

Workaround, in `plant_uml_create_png_and_return_image_url_async`:

1. Ask for the SVG too (it is laid out by the same server and gives us the true layout width).
2. Compare the PNG width against that width (accounting for the scale). A render that lost its text
   is always *narrower*.
3. On a mismatch, re-request with a trailing `' pynsource-retry N` comment line. That changes the
   encoded URL (so a different cache entry, usually a working backend) but not the diagram.
4. Keep the **widest** render seen. Up to `PLANTUML_MAX_RENDER_ATTEMPTS` (3) requests.
5. The SVG itself can occasionally come back degraded (text overflowing its boxes, width too small);
   the loop therefore also *raises* its idea of the layout width when the PNG is wider than the SVG
   (`plantuml svg width N looks short` in the log).

The user sees this in the view while it happens (via `set_progress_callback`):

```
PlantUML picture came back with no text - retrying (2 of 3)...
PlantUML picture came back with no text - keeping the best one we got
```

## 3. Quirk: the server crops at 4096 px

The PlantUML server refuses to draw an image wider or taller than `PLANTUML_LIMIT_SIZE`
(default **4096**) and **crops** the rest instead of scaling it down. There is no warning.

* At `scale 2` the limit is reached at **2048 logical px** of diagram width, so the default HiDPI
  setting halves the usable width. The `filemgmt.py` demo diagram is ~5649 px wide (see its SVG
  `viewBox`), so it is cropped at any scale — the right hand side of the picture is simply gone.
* `clamp_plantuml_scale(requested_scale, diagram_width)` steps the scale down so that
  `width * scale <= 4096`; if even 1× does not fit, it reports `too_wide`.
* `too_wide` is also set when the returned PNG sits exactly on 4096 px (that is what a cropped
  render looks like). The status bar then says to use **File → Save PlantUML Image… (SVG)**.
* The viewer must use the *actual* scale for `zoom_initial`, not the requested one — otherwise wide
  diagrams would be drawn at half apparent size.
* On your own server you can raise the limit with `-DPLANTUML_LIMIT_SIZE=8192` (or the
  `PLANTUML_LIMIT_SIZE` environment variable); Pynsource still assumes 4096.

## 4. Quirk: `/dpng/` is dark mode, not "fresh"

The server accepts `/png/`, `/svg/`, `/txt/`, `/map/`, `/proxy/` and the **`d`-prefixed dark
variants** `/dpng/`, `/dsvg/`. `dpng` returns the same size image with a dark background and light
text (verified: identical pixel dimensions, different palette). It is *not* a "bypass the cache"
endpoint.

Cache-busting is done with the retry comment (section 2), never with `dpng`.

## 5. Quirk: `—|>` (em dash) is a syntax error on every server version

* `MyPrintout --|> wx` (two hyphens) renders on 1.2020.8, 1.2026.9 and on kroki.
* `MyPrintout —|> wx` (one long dash, U+2014) is rejected by **all** of them, with the source echoed
  and the offending token underlined in red, plus "Syntax Error? (Assumed diagram type: class)".

Pynsource's markup is ASCII only (`displaymodel_to_plantuml` emits `"--|>"`), so the app's own
requests are never affected. The dash appears when the text is **copied out of Pynsource and pasted
into another macOS app**: "Smart dashes" (System Settings → Keyboard → Text) rewrites `--` on the
way in. `wx.TextCtrl` itself round-trips `--|>` exactly, and `wx.TheClipboard` + `pbpaste` show the
exact text — verified with a plain `wx.TextCtrl` and with the markup dialog.

Tools in the markup dialog (right-click the PlantUML view → *View PlantUML markup…*):

* **Copy pure markup** — copies the untouched string, reads the clipboard back and reports
  `- clipboard verified`, or `- CLIPBOARD CHANGED IT at char N: sent '-' (U+002D) got '—' (U+2014)`,
  or `- text box differs from markup at char N: ...` if the editable text box no longer matches.
  The button label flips to "Copied!" for 1.5 s as a visible confirmation.
* **Open in browser** — encodes the markup in Python and opens
  `plant_uml_view_url(markup, server)`, i.e. `<server>/uml/<encoded>`, in the default browser.
  No clipboard, no paste, no substitution.

## 6. Choosing the server

**View → PlantUML Server…** (`src/dialogs/DialogPlantUmlServer.py`) offers the official server,
the two ATUG servers and a custom URL, plus the render scale and a **Test** button
(`plant_uml_probe_server`) that renders a probe diagram and reports:

* `Server is working`
* `Cannot reach <url> - ...`
* `Server responded NNN for png`
* `Server responds, but the image came back with no text` (PNG width much narrower than its SVG)

It stores two config keys in `~/Library/Preferences/Pynsource/pynsource.ini` (per-OS paths in
Appdirs; the log prints the exact path):

```ini
PlantUmlServerUrl = https://plantuml.atug.com/uml   # empty/absent = official server
PlantUmlScale = 2                                   # 1-4, HiDPI render scale
```

Editing the ini by hand still works; the dialog just writes the same keys. Changing them clears the
URL caches and refreshes the view.

## 7. Cost

Per *new* diagram: 2 server renders (SVG reference + PNG), plus one more attempt per failed check
(max 3 total). Both are cached per (markup, server, scale), so re-viewing the same diagram costs
nothing. Measured 2026-11: SVG ~0.5 s / 6 KB, PNG ~0.5 s / 11 KB on plantuml.com, ~1.2 s on atug.
On a private server the retry never fires (no text loss observed), so it is simply 2 renders.

## 8. Where the code lives

| Thing | Where |
|---|---|
| `PLANTUML_PNG_LIMIT`, `PLANTUML_MAX_RENDER_ATTEMPTS` | `src/generate_code/gen_plantuml.py` (top) |
| `png_pixel_size`, `svg_pixel_size` | same file — header parsing, no Pillow dependency |
| `clamp_plantuml_scale` | same file |
| `plant_uml_create_png_and_return_image_url_async` | same file — SVG reference, clamp, retry, returns `PlantUmlRender` |
| `plant_uml_fetch_svg_bytes_async` | same file — cached async SVG fetch |
| `plant_uml_probe_server` | same file — used by the settings dialog's Test button |
| `set_progress_callback` | same file — GUI hook for the retry message |
| `plant_uml_view_url` | `src/common/plantuml.py` — interactive page URL for "Open in browser" |
| `PlantUmlRender` consumption, status messages | `src/pynsource_gui.py:_refresh_plantuml_view` |
| `PlantUmlMarkupDialog` (copy / open in browser) | `src/common/gui_imageviewer.py` |
| Server dialog | `src/dialogs/DialogPlantUmlServer.py` |
| Tests | `src/tests/test_plantuml_render.py`, `src/tests/test_plantuml_svg.py` |

## 9. Diagnosing from the log (Help → View Log…)

| Log line | Meaning |
|---|---|
| `plant_uml_server calculated to be <url>` | which server this render used |
| `Response for url <url> from plant_uml_server status_code is 200` | the request itself worked |
| `plantuml render looks like it lost its text (png width X, expected Y) - retrying` | the text-less case, retry is happening |
| `plantuml svg width X looks short, using Y from the png instead` | the SVG was the degraded one |
| `direct diagram image_url of ... (scale N, too_wide True/False, attempts N)` | final choice; `too_wide` means the server cropped it |

## 10. Reproducing the two server bugs

```python
from generate_code.gen_plantuml import png_pixel_size, svg_pixel_size
from common.plantuml import plant_uml_url
import requests, io
from PIL import Image  # dev-only dependency

txt = "class D30 {\n  attribute 1\n  method A()\n}\n"
for i in range(10):
    body = f"' probe {i}\n{txt}"          # a different comment = a different url/cache entry
    png = requests.get(plant_uml_url(body, 'png'), timeout=60).content
    svg = requests.get(plant_uml_url(body, 'svg'), timeout=60).content
    print(i, Image.open(io.BytesIO(png)).size, svg_pixel_size(svg))   # mismatch = text lost
```

A width mismatch like `(107, 139)` vs `(269, 183)` is the text-less render. For the crop, ask for a
very wide diagram at `scale 2` and watch the PNG stop at 4096 px while the SVG `viewBox` is wider.
