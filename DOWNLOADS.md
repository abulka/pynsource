# Download Pynsource

The latest version is `1.88`. Every install path below is linked from
**[the releases page](https://github.com/abulka/pynsource/releases)** — pre-releases (`pre-*` tags)
are built by CI and are safe to try; stable releases use `version-*` tags.

Viewing, editing, zooming and connecting diagram shapes is free. Module visualisation is the
only Pro feature: it needs a [licence](https://pynsource.com/pricing.html) on macOS and Windows
and is **free on Linux**.

## macOS (Apple silicon) — Homebrew

```bash
brew install --cask abulka/pynsource/pynsource
```

Installs to `/Applications`, no unzipping and no Gatekeeper prompt — the cask clears the
quarantine flag for you. Tap: [abulka/homebrew-pynsource](https://github.com/abulka/homebrew-pynsource).

Upgrade with plain `brew upgrade`, or `brew upgrade --cask abulka/pynsource/pynsource` —

> **Use the full cask name.** `brew info pynsource` and `brew upgrade --cask pynsource` (no
> `abulka/pynsource/` prefix) refer to Homebrew's own long-abandoned 1.84 cask: an old Intel build,
> *disabled* since 2026-09-01 because it fails the macOS Gatekeeper check. That is why those
> commands show a red `disabled` and a Rosetta caveat that have nothing to do with this app.

This build is **Apple silicon only** — Intel Macs stop at 1.84, which was the last Intel release. Rosetta does not help: it translates x86 on Apple silicon, not the other way round.

## macOS — zip download

Download `pynsource-macos-<version>.zip`, unzip and drag `Pynsource.app` into `/Applications`.

macOS will block it the first time, because the app is ad-hoc signed (no paid Apple Developer ID):

1. Double-click **Pynsource**, then click **Done** — *not* "Move to Bin".
2. Open **System Settings → Privacy & Security**, scroll to the bottom, find *"Pynsource" was
   blocked to protect your Mac* and click **Open Anyway**. A second dialog asks the same thing —
   click **Open Anyway** again, then authenticate.
3. Double-click **Pynsource** again. It opens normally from then on.

Terminal alternative, no dialogs: `xattr -dr com.apple.quarantine /Applications/Pynsource.app`

The same steps are in `IMPORTANT-README-BEFORE-RUNNING.txt` inside the zip.

## Windows 10 / 11 (64-bit)

Download `pynsource-win-<version>-setup.exe` and run it. It installs to
`C:\Program Files\Pynsource`, adds a Start Menu entry, and can be removed again from
*Apps & features*.

The installer is unsigned (no code-signing certificate), so SmartScreen warns once:

1. On the blue **"Windows protected your PC"** box click **More info**.
2. Click **Run anyway**.

## Linux — AppImage (no install, no root)

Download the AppImage that matches your CPU — `uname -m` tells you which:

- `pynsource-linux-<version>-x86_64.AppImage` — Intel/AMD desktops and VMs
- `pynsource-linux-<version>-aarch64.AppImage` — ARM64: Apple-silicon VMs (UTM, Parallels),
  Asahi Linux, Raspberry Pi 4/5 on a 64-bit OS, ARM servers

```bash
chmod +x pynsource-linux-*.AppImage
./pynsource-linux-*.AppImage
```

One file — nothing to install, no root, nothing to unpack. Needs Ubuntu 22.04+ / Mint 21+ /
Debian 12+ (it is built against glibc 2.35) and any normal GTK3 desktop.

If your file manager will not run it, use the two commands above; most desktops just need
*Properties → Permissions → Allow executing*.

## Ubuntu / Debian — Snap

```bash
sudo snap install pynsource
```

Built on **core24** (Ubuntu 24.04, Python 3.12) and strictly confined, so it runs on any current
Ubuntu without extra packages — the `gnome` extension supplies GTK3.

> `stable` carries 1.87 for both amd64 and arm64. New builds are published to `edge` first and
> promoted to `stable` by hand after a test install, so `--channel=edge` is where to look for
> the next version.

## Troubleshooting

**macOS: "Pynsource is damaged and can't be opened"** — that is Gatekeeper, not a damaged file.
Use the *Open Anyway* steps above, or the `xattr` command.

**Windows: SmartScreen will not offer "Run anyway"** — right-click the `.exe` → *Properties* →
tick *Unblock*, then run it again.

**Linux: `Exec format error`** — you downloaded the AppImage for the wrong CPU. `uname -m` prints
`x86_64` or `aarch64`; download the matching one. (Running the x86_64 build on ARM via
`qemu-user-static` works but is slow.)

**Linux: `libgtk-3.so.0: cannot open shared object file`** — no GTK3 desktop present. On a
headless/minimal system install it first: `sudo apt install libgtk-3-0` (Fedora:
`gtk3`). Everything else is bundled in the AppImage.

**Linux: the AppImage will not mount** — systems without FUSE (some containers) can extract
instead: `./pynsource-linux-*.AppImage --appimage-extract` then run
`squashfs-root/AppRun`.

**PlantUML view is blank** — it renders server-side and needs an internet connection. To run your
own PlantUML server, see the app's built-in help (`F1`).

**PlantUML view draws the boxes but no text** — that comes from the server, not Pynsource. The
public plantuml.com server sometimes returns a picture with every label missing (the boxes and lines
are drawn, the glyphs are not). Pynsource detects the narrow result, re-requests and says
"retrying" in the view; if it persists, switch server with **View → PlantUML Server…** (your own
server, or a custom url), or save with `File → Save PlantUML Image…` choosing SVG, which keeps the
text because SVG text is drawn by your machine. The same menu sets the render scale (2 = crisp on
Retina).

Full technical write-up of every PlantUML quirk (text-less renders, the 4096 px crop, scale
clamping, `/dpng` dark mode, macOS smart dashes) and where each is handled in the code:
`Admin/PLANTUML-QUIRKS.md`.

**PlantUML says "Syntax Error" when you paste its markup somewhere else** — macOS "Smart dashes"
(System Settings → Keyboard → Text) rewrites `--|>` as a long dash `—|>` as the text enters another
app, and PlantUML rejects that character. The markup Pynsource sends itself is plain ASCII, so this
only bites manual copy/paste. The markup dialog's copy button verifies what really reached the
clipboard, and its **Open in browser** button sends the diagram to the chosen server without
touching the clipboard at all.

**The PlantUML picture is cut off on the right** — the PlantUML server refuses to draw wider than
4096 px and crops the rest. Pynsource steps the HiDPI scale down for wide diagrams (and says so in
the status bar when even 1x is too wide); use SVG export for the whole diagram, or raise
`PLANTUML_LIMIT_SIZE` on your own server.

**Where are my settings and logs?** Per-user app data (`appdirs`): macOS
`~/Library/Application Support/PyNsource`, Windows `%APPDATA%\PyNsource`, Linux
`~/.local/share/PyNsource` and `~/.cache/pynsource/log`.

## Pro Edition

An affordable, commercial [Pro Edition](http://pynsource.com/pricing.html) adds module
visualisation (modules as UML boxes, with their variables and functions). Download the regular
build and enter the licence key via **Help → Enter License…** (macOS and Windows; on Linux module
visualisation is already enabled).

## Changelog

See [CHANGELOG.md](CHANGELOG.md). Building from source: [BUILDING.md](BUILDING.md).
