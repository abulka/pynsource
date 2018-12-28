#!/usr/bin/env bash

# Builds a standalone 64 bit pyNsourceGui for mac

# Need to use a brew python (which is a proper framework installation), not a virtual env
# Not even a pyenv version of python is good enough for building via py2app (pyenv version ok for running
# in development mode).  Virtualenv python no good for either running nor deploying (cos of wxpython)
PYTHON=/usr/local/bin/python2
PY2APPLET=/usr/local/bin/py2applet
DESTZIP=pyNsource-1.63-macosx.zip

$PYTHON buildsamples.py

# Ensure you install py2app for the version of python you are invoking.
#   pip install py2app
# We have to use env again because we are invoking a script which then invokes some version of python.
# whatever is first in the path will win.  

cd src

# Build the setup.py file (note, cannot change the name of the output file, it must be setup.py)
$PY2APPLET --make-setup pyNsourceGui.py      # pip install py2app

# Clean up your build directories
rm -rf build dist

# Now invoke the py2app
/usr/local/bin/python2 setup.py py2app      # deployment - makes a universal with 64 bit favoured.
#/usr/local/bin/python2 setup.py py2app -A     # deployment - makes a universal with 64 bit favoured.

# Hacks cos py2app doesn't copy things into the right directories.
# Also ensure you remove references to "import wx.xrc" from dialog/*.py that wxFormBuilder inserts - see https://github.com/pyinstaller/pyinstaller/issues/2295
FROM=dist/pyNsourceGui.app/Contents/Frameworks
DEST=dist/pyNsourceGui.app/Contents/Resources/lib/python2.7/lib-dynload/wx
#CMD=ln -s
#CMD=echo
CMD=cp
$CMD $FROM/libcrypto.1.0.0.dylib $DEST
$CMD $FROM/libssl.1.0.0.dylib $DEST
$CMD $FROM/libwx_baseu_net-3.0.0.4.0.dylib       $DEST
$CMD $FROM/libwx_baseu-3.0.0.4.0.dylib       $DEST
$CMD $FROM/libwx_osx_cocoau_core-3.0.0.4.0.dylib $DEST
$CMD $FROM/libwx_osx_cocoau_html-3.0.0.4.0.dylib $DEST
$CMD $FROM/libwx_osx_cocoau_stc-3.0.0.4.0.dylib $DEST

# The resulting .app is a directory structure and is only
# treated as a single file on a Mac.  So we need to zip it.  Mac users simply unzip
# and they have their app.  Note we use -r for recursion since the .app is a dir structure.
cd dist
cp ../../Readme.txt .
zip -r $DESTZIP pyNsourceGui.app/ Readme.txt
mkdir ../../dist
mv $DESTZIP ../../dist/

cd ../..
echo 'done, please upload the following file to github releases (or whatever)'
ls -l dist/$DESTZIP
