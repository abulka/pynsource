#!/bin/bash
#
# Build a single-file Pynsource AppImage from an existing PyInstaller onedir build.
#
#   cd pynsource                                   # repo root
#   pyinstaller --noconfirm ../ogl2/bin/pynsource-github-actions.spec
#   bin/build-appimage.sh pre-2026-dustoff-5       # -> dist/pynsource-linux-<tag>-x86_64.AppImage
#
# Used by .github/workflows/build-linux.yml. Run it on x86_64 Linux (the CI runner is
# ubuntu-22.04, which decides the glibc floor: 2.35, so Ubuntu 22.04+/Mint 21+).
#
# How the payload is assembled:
#   1. the PyInstaller onedir tree goes to usr/bin/Pynsource/ (exe + _internal, already
#      relocatable via $ORIGIN, so it is copied as-is and never patchelf'd);
#   2. linuxdeploy + linuxdeploy-plugin-gtk bundle GTK3, its dependencies, the gdk-pixbuf
#      loaders and the GTK input-method modules into usr/lib, and generate AppRun;
#   3. appimagetool packs the AppDir.
#
# Why step 2 is needed: the wx wheel hard-links a spread of leaf libraries (libnotify,
# libSM, libXtst, libSDL2, libsecret, libpcre2-32, libcurl) and GTK itself, and PyInstaller
# only ever resolves part of that graph - hand-rolled exclusion lists ended up demanding eight
# packages on the target machine. linuxdeploy's GTK plugin is the purpose-built answer, so the
# resulting AppImage runs on a bare system (verified in a clean ubuntu container with no GTK).
#
# The spec still drops the partial GTK stack it would otherwise bundle (see
# ../ogl2/bin/pynsource-github-actions.spec), so the plugin's copy is the only one present.
#
# Set APPIMAGETOOL / LINUXDEPLOY to pre-downloaded binaries to skip the downloads.
set -euo pipefail

TAG="${1:-local}"
PYTHON="${PYTHON:-python3}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APPDIR="$ROOT/dist/appimage/Pynsource.AppDir"
OUT="$ROOT/dist/pynsource-linux-$TAG-x86_64.AppImage"
TOOLS="$(mktemp -d)"

[ -x dist/Pynsource/Pynsource ] || {
  echo "error: dist/Pynsource/Pynsource not found - run pyinstaller first (see header)" >&2
  exit 1
}

echo "=== AppDir: $APPDIR"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/128x128/apps"

# The whole onedir tree goes in as one directory: the exe finds _internal/ next to itself.
cp -a dist/Pynsource "$APPDIR/usr/bin/Pynsource"

# The Linux wxPython wheels are built with debug symbols: _core.cpython-313-*.so alone is
# ~179MB and the tree totals ~350MB. Stripping the bundled shared objects takes the AppImage
# from ~136MB to ~45MB. Done here rather than with strip=True in the shared spec, so the
# (verified) mac and windows bundles are untouched.
if command -v strip >/dev/null 2>&1; then
  echo "=== stripping debug symbols"
  find "$APPDIR/usr/bin/Pynsource" -type f \( -name '*.so' -o -name '*.so.*' \) -print0 |
    xargs -0 -r -n 20 strip --strip-unneeded 2>/dev/null || true
fi

# Icon: the .ico holds a single 150x150 frame, so downscale it to 128x128 rather than shipping a
# 32x32 upscale (src/media/pynsource.png is only 32x32).
"$PYTHON" - "$APPDIR" <<'PY'
import sys
from PIL import Image

appdir = sys.argv[1]
ico = Image.open("src/media/pynsource.ico").convert("RGBA")
ico = ico.resize((128, 128), Image.LANCZOS)
ico.save(f"{appdir}/usr/share/icons/hicolor/128x128/apps/pynsource.png")
ico.save(f"{appdir}/pynsource.png")  # top-level png: used for .DirIcon / integration
PY

cp .deploy-extras/linux/pynsource.desktop "$APPDIR/pynsource.desktop"
cp .deploy-extras/linux/pynsource.desktop "$APPDIR/usr/share/applications/pynsource.desktop"
ln -sf pynsource.png "$APPDIR/.DirIcon"

# usr/bin/pynsource is what the desktop file's Exec refers to, and what linuxdeploy treats as
# "the app". It is only a wrapper, so linuxdeploy leaves the PyInstaller tree alone.
# It must put usr/lib on the loader path itself: linuxdeploy's GTK plugin normally does that by
# setting an rpath on the binaries it deploys, which a shell wrapper cannot carry.
cat > "$APPDIR/usr/bin/pynsource" <<'SH'
#!/bin/sh
# Wrapper: the PyInstaller tree lives next to this script so _internal/ stays with the exe,
# and linuxdeploy's GTK copy lives in usr/lib (three levels up from the real binary).
HERE="$(dirname "$(readlink -f "$0")")"
APPDIR="$(dirname "$(dirname "$HERE")")"
if [ -d "$APPDIR/usr/lib" ]; then
  export LD_LIBRARY_PATH="$APPDIR/usr/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
exec "$HERE/Pynsource/Pynsource" "$@"
SH
chmod +x "$APPDIR/usr/bin/pynsource"

fetch() {  # fetch <url> <dest>
  curl -fsSL --retry 3 -o "$2" "$1" && chmod +x "$2"
}

if [ -z "${LINUXDEPLOY:-}" ]; then
  LINUXDEPLOY="$TOOLS/linuxdeploy"
  echo "=== downloading linuxdeploy"
  fetch https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage "$LINUXDEPLOY"
fi
if ! command -v linuxdeploy-plugin-gtk >/dev/null 2>&1; then
  echo "=== downloading linuxdeploy-plugin-gtk"
  fetch https://raw.githubusercontent.com/linuxdeploy/linuxdeploy-plugin-gtk/master/linuxdeploy-plugin-gtk.sh \
        "$TOOLS/linuxdeploy-plugin-gtk"
  export PATH="$TOOLS:$PATH"
fi

echo "=== linuxdeploy + gtk plugin"
# extract-and-run: no FUSE on CI runners. DEPLOY_GTK_VERSION=3 because wxWidgets 3.2 is GTK3.
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 DEPLOY_GTK_VERSION=3 \
  "$LINUXDEPLOY" --appdir "$APPDIR" --plugin gtk \
  --desktop-file "$APPDIR/pynsource.desktop" \
  --icon-file "$APPDIR/pynsource.png"

echo "=== AppRun (generated by linuxdeploy)"
cat "$APPDIR/AppRun" | head -30
echo "bundled in usr/lib: $(ls "$APPDIR/usr/lib" 2>/dev/null | wc -l) files"

if [ -z "${APPIMAGETOOL:-}" ]; then
  APPIMAGETOOL="$TOOLS/appimagetool"
  echo "=== downloading appimagetool"
  fetch https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage "$APPIMAGETOOL"
fi

echo "=== appimagetool -> $OUT"
rm -f "$OUT"
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL" --no-appstream "$APPDIR" "$OUT"

echo "=== built:"
ls -l "$OUT"
