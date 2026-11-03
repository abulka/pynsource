Windows, macOS and Linux builds of Pynsource — Python 3.13, wxPython 4.3.2 (4.2.5 on Linux).

## Windows 10/11 (64-bit)

Download `pynsource-win-<tag>-setup.exe` and run it. Installs to
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

- `pynsource-linux-<tag>-x86_64.AppImage` — Intel/AMD desktops and VMs
- `pynsource-linux-<tag>-aarch64.AppImage` — ARM64 (Apple-silicon VMs such as UTM, Asahi
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

## Notes

- Apple silicon only on Mac (Intel Macs are not supported).
- Editing diagrams is free; the Pro features (zoom, drag-to-connect, module
  visualisation) need a licence — https://www.pynsource.com/pricing.html
