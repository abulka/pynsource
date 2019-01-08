#!/usr/bin/env bash

# Builds a standalone 64 bit pyNsourceGui for mac

# Need to use a brew python (which is a proper framework installation), not a virtual env
# Not even a pyenv version of python is good enough for building via py2app (pyenv version ok for running
# in development mode).  Virtualenv python no good for either running nor deploying (cos of wxpython)
#PYTHON=/usr/local/bin/python3
PYTHON=/usr/local/Cellar/python/3.7.0/bin/python3
#PYTHON=/usr/local/Cellar/python/3.7.2/bin/python3
PY2APPLET=/usr/local/bin/py2applet
DESTZIP=pyNsource-1.7-macosx.zip

$PYTHON buildsamples.py

# Ensure you install py2app for the version of python you are invoking.
#   pip install py2app
# We have to use env again because we are invoking a script which then invokes some version of python.
# whatever is first in the path will win.  

cd src

# Change to "Y" to regenerate src/setup.py
# Not usually necessary but on first run of a new install you will need to.  And do the
# suggested edits.  Note src/setup.py is not in source control.
REGEN_SETUP_PY="N"
if [ "$REGEN_SETUP_PY" == "Y" ]
then
    echo "regenerating...."
    # Build the setup.py file (note, cannot change the name of the output file, it must be setup.py)
    $PY2APPLET --make-setup pyNsourceGui.py      # pip install py2app

    echo If you have regenerated src/setup.py ensure you edit it as follows:
    echo
    echo DATA_FILES = \[\'dialogs/HelpWindow.html\', \'dialogs/help-images\' \]

    # argv_emulation must be set to False to avoid mac bug where app starts minimised
    # or simply not have that option at all (which is the new default with latest py2app)
    # see https://bitbucket.org/ronaldoussoren/py2app/issues/140/app-starts-minimized
    echo OPTIONS = {\'argv_emulation\': False}   or just
    echo OPTIONS = {}

    echo
    echo hit enter to confirm
    read ok
fi

# Check all references to "import wx.xrc" have been removed
echo Ensure all references to \"import wx.xrc\" have been removed!!
grep "import wx.xrc" dialogs/*.py

# Clean up your build directories
rm -rf build dist

# Now invoke the py2app
$PYTHON setup.py py2app      # deployment - makes a universal with 64 bit favoured.
#$PYTHON setup.py py2app -A     # deployment - makes a universal with 64 bit favoured.

# Hacks cos py2app doesn't copy things into the right directories.
# Also ensure you remove references to "import wx.xrc" from dialog/*.py that wxFormBuilder inserts - see https://github.com/pyinstaller/pyinstaller/issues/2295
FROM=dist/pyNsourceGui.app/Contents/Frameworks
#DEST=dist/pyNsourceGui.app/Contents/Resources/lib/python2.7/lib-dynload/wx
DEST=dist/pyNsourceGui.app/Contents/Resources/lib/python3.7/lib-dynload/wx
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
$CMD $FROM/libgdbm.6.dylib $DEST
$CMD $FROM/liblzma.5.dylib $DEST

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
