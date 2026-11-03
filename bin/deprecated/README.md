# Deprecated scripts

Unmaintained, kept only for reference until the Linux packaging phase is finished.

| script | why it is dead |
|---|---|
| `install-linux-18.04` | Ubuntu 18.04 is EOL; the script pins a wxPython wheel for that distro |
| `install-linux-20.04` | Ubuntu 20.04 is EOL; same |
| `install-linux-fedora-33` | Fedora 33 + Python 3.8 are long gone |

Modern Linux install will be documented in `BUILDING.md` (from source, using the current
Python 3.13 + wxPython 4.3.x wheels) and shipped as an AppImage/snap.

**Delete this directory once the Linux phase (AppImage + snap) lands.**
