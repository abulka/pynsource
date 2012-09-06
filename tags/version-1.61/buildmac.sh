# Builds a standalone 32 bit pyNsourceGui for mac

python buildsamples.py

# Either run this with default python or user installed python
# by setting the correct path first e.g.
# export PATH=/usr/local/bin:$PATH

# Running in 64 bit 32bit doesn't matter since we are not invoking wxPython itself
# thus NO NEED to set VERSIONER_PYTHON_PREFER_32_BIT or run python-32

# Some useful reference instructions on py2app and the 'ditto' app at
# http://svn.pythonmac.org/py2app/py2app/trunk/doc/index.html#abstract
# and
# http://stackoverflow.com/questions/7472301/how-to-force-py2app-to-run-app-in-32-bit-mode

# Ensure you install py2app for the version of python you are invoking.  
#   sudo env easy_install py2app
# We have to use env again because we are invoking a script which then invokes some version of python.
# whatever is first in the path will win.  

cd src

# Build the setup.py file (note, cannot change the name of the output file, it must be setup.py)
# Proof: /System/Library//Frameworks/Python.framework/Versions/2.7//Extras/lib/python/py2app/script_py2applet.py
# 
# Use env so that the correct version of python is invoked by this script - whatever is first in the path.  
# 64 bit 32bit doesn't matter here
env py2applet --make-setup pyNsourceGui.py      # sudo env easy_install py2app

# Clean up your build directories
rm -rf build dist

# Now invoke the py2app - we don't use env here because python is already the first thing on the command line
# 64 bit 32bit doesn't matter here.  Though py2app builds a universal 32 and 64 app.
# Presumably the version of python that gets packaged is the python that is invoked here :-)
#
#python setup.py py2app -A  # testing - doesn't actually build much, standalone application not built
python setup.py py2app      # deployment - makes a universal with 64 bit favoured.

# Strip out the 64bit binaries which are run by default, and fail since wxPython 2.8 is 32bit
ditto -rsrc --arch i386 dist/pyNsourceGui.app/ dist/pyNsourceGui32.app

# The resulting .app is a directory structure and is only
# treated as a single file on a Mac.  So we need to zip it.  Mac users simply unzip
# and they have their app.  Note we use -r for recursion since the .app is a dir structure.
cd dist
cp ../../Readme.txt .
zip -r pyNsource-1.61-macosx.zip pyNsourceGui32.app/ Readme.txt
mkdir ../../dist
mv pyNsource-1.61-macosx.zip ../../dist/

cd ../..
echo 'done, please upload the following file to sourceforge'
ls -l dist/pyNsource-1.61-macosx.zip
