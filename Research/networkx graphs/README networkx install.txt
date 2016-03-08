For installing and playing with   http://networkx.lanl.gov/
Andy.

easy_install itself
--------------------
Get easyinstall from
  http://pypi.python.org/pypi/setuptools#downloads

Add 
  c:\python26\Scripts
to your path 
then you can run
  easy_install networkx-1.4-py2.6.egg

networkX egg 
--------------
Get the networkX egg from
  http://networkx.lanl.gov/
though you can probably pull the egg down dynamically 
over the web without downloading using
  easy_install networkx

NumPy 
--------
Download NumPy and install
  https://sourceforge.net/projects/numpy/files/NumPy/


matplotlib    for visualisation
-----------
Info  http://matplotlib.sourceforge.net/users/installing.html
Download  https://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.0.1/

Graphviz / PyGraphviz   for more visualisation
----------------------
First Download and INSTALL Graphviz - Graph Visualization Software from    http://graphviz.org/Download_windows.php
  graphvis-2.26.3.msi
then
  easy_install pygraphviz      FAILS UNDER WINDOWS COS 

   You are using Windows
   There are no PyGraphviz binary packages for Windows but you might be
   able to build it from this source.  See
   http://networkx.lanl.gov/pygraphviz/reference/faq.html

CRAP - dead end. See   http://stackoverflow.com/questions/4571067/installing-pygraphviz-on-windows

possibly could compile something with MinGW 
  http://stackoverflow.com/questions/101061/building-python-c-extension-modules-for-windows

