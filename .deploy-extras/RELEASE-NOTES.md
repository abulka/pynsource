Pynsource 1.86 — reverse-engineer Python source into UML class diagrams.
Python 3.13, wxPython 4.3.2 (4.2.5 on Linux), 64-bit builds for Windows, macOS and Linux.

First stable release since 1.84 (2022). Everything below is built by CI from this tag:

| Platform | Download |
|---|---|
| Windows 10/11 | `pynsource-win-version-1.86-setup.exe` |
| macOS (Apple silicon) | `pynsource-macos-version-1.86.zip` (or Homebrew, below) |
| Linux x86_64 | `pynsource-linux-version-1.86-x86_64.AppImage` |
| Linux aarch64 | `pynsource-linux-version-1.86-aarch64.AppImage` |
| Ubuntu/Debian | `sudo snap install pynsource` |

## What's new

- Python 3.13 and wxPython 4.3 support; Python 2 parsing dropped (it depended on the
  end-of-life `typed_ast`)
- Blurry text fixed on Retina/HiDPI displays
- Mac print preview page range corrected (was showing 1..9999)
- **Pro features are free on Linux** — zoom, drag-to-connect and module visualisation need no
  licence there
- Rebuilt packaging on every platform: onedir macOS `.app`, Inno Setup 6 installer on Windows,
  single-file AppImages for both architectures, and a core24 snap
- macOS app installs prompt-free via Homebrew, and opens ~5x faster than the old onefile build

## Windows 10/11 (64-bit)

Download `pynsource-win-version-1.86-setup.exe` and run it. Installs to
`C:\Program Files\Pynsource`, adds a Start Menu entry, uninstalls from *Apps & features*.

**First run:** Windows SmartScreen warns because the installer is unsigned (no paid
code-signing certificate) — on the blue *"Windows protected your PC"* box click
**More info**, then **Run anyway**. The installer then runs normally.

## macOS (Apple silicon)

Homebrew, no Gatekeeper prompt:

```
brew install --cask abulka/pynsource/pynsource
```

Or download the zip below, unzip, and drag `Pynsource.app` into `/Applications`.

**First run:** macOS blocks the app because it is ad-hoc signed (no paid Apple
Developer ID):

1. Double-click **Pynsource**, then click **Done** — *not* "Move to Bin".
2. Open **System Settings → Privacy & Security**, scroll to the bottom, find
   *"Pynsource" was blocked to protect your Mac* and click **Open Anyway**.
   A second dialog asks the same thing — click **Open Anyway** again, then authenticate.
3. Double-click **Pynsource** again. It opens normally from then on.

Terminal alternative: `xattr -dr com.apple.quarantine /Applications/Pynsource.app`

The same steps are in `IMPORTANT-README-BEFORE-RUNNING.txt` inside the zip.

## Linux (AppImage, 64-bit)

Download the AppImage for your CPU — `uname -m` tells you which:

- `pynsource-linux-version-1.86-x86_64.AppImage` — Intel/AMD desktops and VMs
- `pynsource-linux-version-1.86-aarch64.AppImage` — ARM64 (Apple-silicon VMs such as UTM, Asahi
  Linux, Raspberry Pi 4/5 with a 64-bit OS, ARM servers)

```
chmod +x pynsource-linux-*.AppImage
./pynsource-linux-*.AppImage
```

One file, no install and no root. Works on Ubuntu 22.04+/Mint 21+/Debian 12+ (it is built on
glibc 2.35) with any normal GTK3 desktop. If your file manager will not run it, use the two
commands above from a terminal — most simply need *Properties → Permissions → Allow executing*.

All Pro features (zoom, drag-to-connect, module visualisation) are **free on Linux** — no
licence needed.

## Ubuntu / Debian (snap)

```
sudo snap install pynsource
```

Built for both amd64 and arm64. If `pynsource` is already installed, `sudo snap refresh
pynsource` moves it to this version.

## Notes

- Apple silicon only on Mac (Intel Macs are not supported).
- Editing diagrams is free; the Pro features (zoom, drag-to-connect, module
  visualisation) need a licence — https://www.pynsource.com/pricing.html
