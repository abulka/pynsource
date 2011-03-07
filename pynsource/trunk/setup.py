"""
 Make sure you delete the Build directory if you are
 reconfiguring which files are being distributed
 as there may be old relics in there that get installed.
"""

from distutils.core import setup
setup (name = "PyNsource",
       version = "1.51",
       author = "Andy Bulka",
       author_email = "abulka@gmail.com",
       url='http://www.andypatterns.com/index.php/products/pynsource/',
       description = "A python reverse engineering code scanner that generates - UML pictures (as text or UML diagrams) - Java or Delphi code (which can be imported into advanced UML modelling tools.)",
       keywords = "UML modelling python reverse engineering",
       license = "GPL v3 Free as long as author is acknowledged and derivitave source is also open source.",
       packages=['pynsource'],
       data_files=[('myextras', ['Readme.txt', 'rungui.bat'])]   
       )
