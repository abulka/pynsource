Windows and macOS builds of Pynsource — Python 3.13, wxPython 4.3.2.

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

## Notes

- Apple silicon only on Mac (Intel Macs are not supported).
- Editing diagrams is free; the Pro features (zoom, drag-to-connect, module
  visualisation) need a licence — https://www.pynsource.com/pricing.html
