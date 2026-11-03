macOS build of Pynsource — Apple silicon (arm64), Python 3.13, wxPython 4.3.2.

## Install

Homebrew, no Gatekeeper prompt:

```
brew install --cask abulka/pynsource/pynsource
```

Or download the zip below, unzip, and drag `Pynsource.app` into `/Applications`.

## Installation tips (first run)

macOS blocks the app the first time you open it, because it is ad-hoc signed
(no paid Apple Developer ID):

1. Double-click **Pynsource**, then click **Done** — *not* "Move to Bin".
2. Open **System Settings → Privacy & Security**, scroll to the bottom, find
   *"Pynsource" was blocked to protect your Mac* and click **Open Anyway**.
   A second dialog asks the same thing — click **Open Anyway** again, then authenticate.
3. Double-click **Pynsource** again. It opens normally from then on.

Terminal alternative: `xattr -dr com.apple.quarantine /Applications/Pynsource.app`

The same steps are in `IMPORTANT-README-BEFORE-RUNNING.txt` inside the zip.

## Notes

- Apple silicon only (Intel Macs are not supported).
- Editing diagrams is free; the Pro features (zoom, drag-to-connect, module
  visualisation) need a licence — https://www.pynsource.com/pricing.html
