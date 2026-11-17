# -*- mode: python -*-
import os
import platform

# To build, from the pynsource/ dir run: 
# pyinstaller bin/pynsource-github-actions.spec
# or bin/buildmac

print(os.getcwd())  # should be 'pynsource' dir
print(platform.system())


def app_version():
    """APP_VERSION from src/gui/settings.py - the single source of truth (tbump patches it).

    Used as CFBundleShortVersionString: without it PyInstaller defaults to "0.0.0", which is
    what Finder's Get Info and the About panel of any macOS utility report.
    """
    import re
    settings = os.path.join(os.getcwd(), 'src', 'gui', 'settings.py')
    try:
        with open(settings, encoding='utf-8') as f:
            match = re.search(r'^APP_VERSION\s*=\s*([0-9.]+)', f.read(), re.MULTILINE)
    except OSError:
        return '0.0.0'
    return match.group(1) if match else '0.0.0'

block_cipher = None

a = Analysis([os.path.join(os.getcwd(), 'src', 'pynsource_gui.py')],
             pathex=[
                 os.getcwd(),
                 '../wxdiagram/',
                 '../pynsource-rego/',
                 '../alsm/',
             ], 
             binaries=[],
             datas=[
                 (os.path.join(os.getcwd(), 'README.md'), '.'),
                 (os.path.join(os.getcwd(), "src/dialogs/HelpWindow.html"), "dialogs"),
                 (os.path.join(os.getcwd(), "src/dialogs/help-images"), "dialogs/help-images"),
                 (os.path.join(os.getcwd(), "src/media/pynsource.ico"), "media/"),
                 (os.path.join(os.getcwd(), "src/media/pynsource.png"), "media/"),
                 ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# Linux: keep the GTK/GLib/display stack on the host, bundle everything else.
#
# The wx wheel hard-links a pile of leaf libs that a minimal desktop may not have
# (libcurl, libSDL2, libsecret, libnotify, libSM, libXtst, libpcre2-32), so those are bundled
# along with their own dependencies. The GTK/GLib/pango/cairo/gdk-pixbuf and X11/wayland stack
# is NOT bundled: that lot has to match the running desktop (themes, gdk-pixbuf loaders, IM
# modules), and PyInstaller only ever resolves part of it anyway - a partial copy fails on
# machines without GTK while still risking a version clash on machines with it.
# Mac/Windows are untouched (the check is platform-gated).
if platform.system() == 'Linux':
    import fnmatch
    HOST_STACK = [
        'libgtk-3*', 'libgdk-3*', 'libgdk_pixbuf*', 'libglib-2.0*', 'libgobject-2.0*',
        'libgio-2.0*', 'libgmodule-2.0*', 'libatk*', 'libpango*', 'libcairo*',
        'libharfbuzz*', 'libgraphite2*', 'libfontconfig*', 'libfreetype*',
        'libpixman*', 'libfribidi*', 'libthai*', 'libdatrie*', 'libepoxy*',
        'libX11*', 'libxcb*', 'libXau*', 'libXdmcp*', 'libxkbcommon*', 'libwayland*',
    ]
    _before = len(a.binaries)
    a.binaries = [b for b in a.binaries
                  if not any(fnmatch.fnmatch(b[0], pattern) for pattern in HOST_STACK)]
    print(f'Linux: dropped {_before - len(a.binaries)} host-provided graphics-stack libs')

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

# ONEDIR build (was onefile). Onefile unpacks the whole archive into a fresh
# $TMPDIR/_MEIxxxxxx on EVERY launch (~2s even when warm, ~8s on first launch while
# macOS verifies a single 34MB fully-sealed executable) and PyInstaller 7 refuses
# onefile + .app outright. Onedir runs straight out of the bundle: measured 0.4s
# launch -> window. See pynsource/BUG-DIST-SLOWNESS-MAC.md section 12.
exe = EXE(pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='Pynsource',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        runtime_tmpdir=None,
        icon=os.path.join(os.getcwd(), "src/media/pynsource.ico"),  # Icon for exe itself
        console=False )

# COLLECT produces dist/Pynsource/ (exe + payload); BUNDLE turns that directory into
# Pynsource.app with the payload in Contents/Frameworks/ (Contents/Resources/ holds
# symlinks so lookups by resource path keep working).
coll = COLLECT(exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name='Pynsource')

app = BUNDLE(coll,
            name='Pynsource.app',
            version=app_version(),   # else CFBundleShortVersionString is 0.0.0
            icon=os.path.join(os.getcwd(), "src/media/pynsource.icns"),  # Icon for Mac .app
            info_plist={
                'NSHighResolutionCapable': 'True',
                'NSRequiresAquaSystemAppearance': 'No'
            },
            bundle_identifier='com.pynsource.pynsource')
