# Download Pynsource

The latest version is `1.85`. Every install path below is linked from
**[the releases page](https://github.com/abulka/pynsource/releases)** — pre-releases (`pre-*` tags)
are built by CI and are safe to try; stable releases use `version-*` tags.

Viewing and editing diagrams is free. The Pro features (zoom, drag-to-connect, module
visualisation) need a [licence](https://pynsource.com/pricing.html) on macOS and Windows, and are
**free on Linux**.

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

This build is **Apple silicon only** — Intel Macs are not supported.

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

> The snap is currently published to the **edge** channel while it is being tested:
> `sudo snap install pynsource --edge`. The `stable` channel still has an old 2023 build
> (Python 3.6, cannot parse Python 3.10 syntax); stable is promoted by hand once the edge build
> has been in use for a while.

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

**Where are my settings and logs?** Per-user app data (`appdirs`): macOS
`~/Library/Application Support/PyNsource`, Windows `%APPDATA%\PyNsource`, Linux
`~/.local/share/PyNsource` and `~/.cache/pynsource/log`.

## Pro Edition

An affordable, commercial [Pro Edition](http://pynsource.com/pricing.html) adds zoom,
drag-to-connect and module visualisation. Download the regular build and enter the licence key
via **Help → Enter License…** (macOS and Windows; on Linux the Pro features are already enabled).

## Changelog

See [CHANGELOG.md](CHANGELOG.md). Building from source: [BUILDING.md](BUILDING.md).
