#!/bin/bash

echo "You are running shell" $SHELL
msg="This script was developed in Ubuntu 11.10"
echo $msg


outstandalonezip=pyNsource-1.61-linux-standalone.zip
outsourcezip=pyNsource-1.61-src.zip

do_build_samples=true
do_source=true
do_exe=true
do_exe_zip=true

svn info > version.txt

if $do_build_samples; then
    python buildsamples.py
fi

if $do_exe; then
	# Build standalone exe and zip it up.
	#
	# easy_install bbfreeze  
	# Doco at http://pypi.python.org/pypi/bbfreeze/
	# Needs package "header files and a static library for Python (default)"
	#
	cd src
	rm -f dist/*.* build/*.*
	bb-freeze pyNsourceGui.py pyYumlGui.py pynsource.py
	cd ..
fi

if $do_exe_zip; then
	# Zip up the executable
	rm -f dist/$outstandalonezip
	zip -j dist/$outstandalonezip ./src/dist/* ./Readme.txt ./version.txt
fi

if $do_source; then
	# Zip up the source code
	rm -f dist/$outsourcezip
	zip -r dist/$outsourcezip src tests Readme.txt run* build* version.txt -x \*\.svn/\* -x \*/build/\* -x \*/dist/\* -x \*.pyc -x \*.*~
fi

echo "All done"

