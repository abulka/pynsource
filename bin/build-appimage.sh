#!/bin/bash
#
# Build a single-file Pynsource AppImage from an existing PyInstaller onedir build.
#
#   cd pynsource                                   # repo root
#   pyinstaller --noconfirm ../ogl2/bin/pynsource-github-actions.spec
#   bin/build-appimage.sh pre-2026-dustoff-5       # -> dist/pynsource-linux-<tag>-x86_64.AppImage
#
# Used by .github/workflows/build-linux.yml. Run it on x86_64 Linux (the CI runner is
# ubuntu-22.04, which is what decides the glibc floor: 2.35, so Ubuntu 22.04+/Mint 21+).
#
# Why no linuxdeploy:
#   The PyInstaller tree is already relocatable (Pynsource + _internal/, $ORIGIN rpath), so the
#   AppDir just wraps it as-is. linuxdeploy would patchelf the bundled .so files in place, which
#   is a well-known way to break a PyInstaller bundle, and its only real gain here would be
#   shipping a private copy of GTK3 (~30MB). Every desktop distro already has GTK3, so we use
#   the system one. If a user ever reports a missing libgtk, add linuxdeploy-plugin-gtk then.
#
# Set APPIMAGETOOL to a pre-downloaded appimagetool binary to skip the download.
set -euo pipefail

TAG="${1:-local}"
PYTHON="${PYTHON:-python3}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APPDIR="$ROOT/dist/appimage/Pynsource.AppDir"
OUT="$ROOT/dist/pynsource-linux-$TAG-x86_64.AppImage"

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

cat > "$APPDIR/AppRun" <<'SH'
#!/bin/sh
# AppImage entry point: resolve the mount point and run the bundled PyInstaller binary.
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/Pynsource/Pynsource" "$@"
SH
chmod +x "$APPDIR/AppRun"

if [ -z "${APPIMAGETOOL:-}" ]; then
  APPIMAGETOOL="$(mktemp -d)/appimagetool"
  echo "=== downloading appimagetool"
  curl -fsSL --retry 3 -o "$APPIMAGETOOL" \
    https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
  chmod +x "$APPIMAGETOOL"
fi

echo "=== appimagetool -> $OUT"
rm -f "$OUT"
# extract-and-run: no FUSE on CI runners (and no libfuse2 on a bare runner either)
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL" --no-appstream "$APPDIR" "$OUT"

echo "=== built:"
ls -l "$OUT"
