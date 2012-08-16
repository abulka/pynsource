"""
Compare old and new parsing

"""

import ast
import difflib
import os

import sys
sys.path.append("../../src")

from logwriter import LogWriter
from parsing.core_parser_ast import convert_ast_to_old_parser
from parsing.dump_pmodel import dump_old_structure

global log

DEBUGINFO = 1
LOG_TO_CONSOLE = 0

def old_parser(filename):
    import sys
    sys.path.append("../../src")
    from generate_code.gen_asciiart import PySourceAsText
    
    p = PySourceAsText()
    p.Parse(filename)
    return p

def ast_parser(filename):
    with open(filename,'r') as f:
        source = f.read()
    
    node = ast.parse(source)
    #print ast.dump(node)
    return node


#####

last_diff_s = ""

def parse_and_convert(in_filename, print_diffs=True):
    global log
    log = LogWriter(in_filename, print_to_console=LOG_TO_CONSOLE)
    
    def oldparse():
        model = old_parser(in_filename)
        d1 = dump_old_structure(model)
        log.out_wrap_in_html(d1, style_class='dump1')
        return d1
        
    def newparse():
        node = ast_parser(in_filename)
        model, debuginfo = convert_ast_to_old_parser(node, in_filename, log)
        d2 = dump_old_structure(model)
        log.out_wrap_in_html(d2, style_class='dump1')
        return d2, debuginfo

    def dodiff(d1, d2):
        diff = difflib.ndiff(d1.splitlines(1),d2.splitlines(1))
        diff_s = ''.join(diff)
        return diff_s
            
    try:
        log.out_html_header()
        log.out("PARSING: %s *****\n" % in_filename)
        
        d1 = oldparse()
        log.out_divider()
        d2, debuginfo = newparse()
        
        comparedok = (d1 == d2)
        log.out("** old vs new method comparison = %s" % comparedok)

        diff_s = dodiff(d1, d2)
        log.out_wrap_in_html(diff_s, style_class='dumpdiff')
        if not comparedok and print_diffs:
            print diff_s

        #dd = difflib.HtmlDiff()
        #diff_table = dd.make_table(d1.splitlines(1),d2.splitlines(1))
        #log.out(diff_table)

        if not comparedok:
            global last_diff_s
            
            log.out("<hr>")
            delta = difflib.unified_diff(d1.splitlines(1),d2.splitlines(1), n=0,
                                fromfile='before.py', tofile='after.py')
            last_diff_s = "".join(delta)
            log.out_wrap_in_html(last_diff_s, style_class='dumpdiff')

        if DEBUGINFO:
            log.out(debuginfo)
    
        log.out_html_footer()
    finally:
        log.finish()
        
    return comparedok


############        

results = []
def reset_tests():
    global results
    results = []
def test(filename):
    results.append(parse_and_convert(filename))
def test_not(filename, expected_diffs=None):
    # expect parse to slightly fail, with a diff matching expected_diff
    result = parse_and_convert(filename, print_diffs=False)
    if not result:
        # good, we expected this
        successful_test = True
        if expected_diffs and last_diff_s.strip() != expected_diffs[os.path.basename(filename)].strip():
            successful_test = False
    else:
        # we didn't expect this to parse and match - unbelievable.  Good but not what we expected.
        successful_test = False
    results.append(successful_test)
def report(msg):
    if all(results):
        print "%s OK" % msg
    else:
        print "oooops %s broken" % msg, results

###########

expected_diffs = {}

# ast is better, base classes with . handled
expected_diffs['testmodule08_multiple_inheritance.py'] = """
--- before.py
+++ after.py
@@ -1 +1 @@
-Fred (is module=0) inherits from ['Mary', 'MarySam'] class dependencies []
+Fred (is module=0) inherits from ['Mary', 'Mary.Sam'] class dependencies []
"""

# ast is better, (1) nested module functions ignored. (2) class actually checked
# for when relaxed attr ref to instance. (3) extra properties picked up (though
# they should be normal not static)
expected_diffs['command_pattern.py'] = """
--- before.py
+++ after.py
@@ -5,2 +5 @@
-CommandManager (is module=0) inherits from ['object'] class dependencies [('_list', 'Item')]
-('_list', 'Item')
+CommandManager (is module=0) inherits from ['object'] class dependencies []
@@ -10,0 +10,3 @@
+    currentItem          (attrtype ['static'])
+    currentRedoItem      (attrtype ['static'])
+    maxItems             (attrtype ['static'])
@@ -45 +47 @@
-    modulemethods ['suite', 'numbersuffix', 'main']
+    modulemethods ['suite', 'main']
"""

# ast is better, less module methods found - more correct
expected_diffs['pynsource.py'] = """
--- before.py
+++ after.py
@@ -1 +1 @@
-    modulemethods ['test', 'ParseArgsAndRun', 'EnsurePathExists']
+    modulemethods ['test', 'ParseArgsAndRun']
"""

# ast is better for python-in/testmodule09_intense.py
"""
SHOULD GET THE FOLLOWING RESULTS:
('a', 'UmlCanvas'),         OK
('b', 'UmlCanvas'),         OK
('log', 'Log'),             OK
('frame', 'Frame'),         MORE should be wx.Frame ** fixed **
????                        MISSING - should have ('notebook', 'wx.Notebook')
('umlwin', 'UmlCanvas'),    OK
('app', 'App'),             OK
('config', 'ConfigObj'),    OK
('popupmenu', 'Menu'),      MORE should be wx.Menu** fixed **
('next_menu_id', 'NewId'),  MORE should be wx.NewId -> but not a class I don't think....** fixed **
('printData', 'PrintData'), MORE should be wx.PrintData** fixed **
('box', 'BoxSizer'),        MORE should be wx.BoxSizer** fixed **
('canvas', 'GetDiagram')    WRONG should be skipped

latest is ok
------
('a', 'UmlCanvas')
('b', 'UmlCanvas')
('log', 'Log')
('frame', 'wx.Frame')
('notebook', 'wx.Notebook')
('umlwin', 'UmlCanvas')
('app', 'App')
('config', 'ConfigObj')
('popupmenu', 'wx.Menu')
('next_menu_id', 'wx.NewId')
('printData', 'wx.PrintData')
('box', 'wx.BoxSizer')

"""

expected_diffs['testmodule09_intense.py'] = """
--- before.py
+++ after.py
@@ -1 +1 @@
-Torture1 (is module=0) inherits from [] class dependencies [('a', 'UmlCanvas'), ('b', 'UmlCanvas'), ('log', 'Log'), ('umlwin', 'UmlCanvas'), ('umlwin', 'UmlCanvas'), ('umlwin', 'UmlCanvas'), ('umlwin', 'UmlCanvas'), ('umlwin', 'UmlCanvas'), ('umlwin', 'UmlCanvas'), ('app', 'App'), ('config', 'ConfigObj')]
+Torture1 (is module=0) inherits from [] class dependencies [('a', 'UmlCanvas'), ('b', 'UmlCanvas'), ('log', 'Log'), ('frame', 'wx.Frame'), ('notebook', 'wx.Notebook'), ('umlwin', 'UmlCanvas'), ('app', 'App'), ('config', 'ConfigObj'), ('popupmenu', 'wx.Menu'), ('next_menu_id', 'wx.NewId'), ('printData', 'wx.PrintData'), ('box', 'wx.BoxSizer')]
@@ -5,5 +5,2 @@
-('umlwin', 'UmlCanvas')
-('umlwin', 'UmlCanvas')
-('umlwin', 'UmlCanvas')
-('umlwin', 'UmlCanvas')
-('umlwin', 'UmlCanvas')
+('frame', 'wx.Frame')
+('notebook', 'wx.Notebook')
@@ -12,0 +10,4 @@
+('popupmenu', 'wx.Menu')
+('next_menu_id', 'wx.NewId')
+('printData', 'wx.PrintData')
+('box', 'wx.BoxSizer')
"""

###########

RUN_TEST_SUITE = 1

if RUN_TEST_SUITE:
    reset_tests()    
    test('../../tests/python-in/testmodule01.py')
    test('../../tests/python-in/testmodule02.py')
    test('../../tests/python-in/testmodule03.py')
    test('../../tests/python-in/testmodule04.py')
    test('../../tests/python-in/testmodule05.py') # (inner classes)
    test('../../tests/python-in/testmodule06.py')
    test('../../tests/python-in/testmodule07.py')
    test('../../tests/python-in/testmodule66.py')
    report("official parsing tests")
    
    reset_tests()    
    test('../../src/printframework.py')
    test('../../src/asciiworkspace.py')
    report("subsidiary parsing tests")
    
    # Expect these to fail cos ast parsing is genuinely better
    reset_tests()    
    test_not('../../tests/python-in/testmodule08_multiple_inheritance.py', expected_diffs)
    test_not('../../src/command_pattern.py', expected_diffs)
    test_not('../../src/pynsource.py', expected_diffs)
    test_not('../../tests/python-in/testmodule09_intense.py', expected_diffs)
    report("ast parsing is genuinely better")

    # Extras
    print

#print parse_and_convert('../../src/pyNsourceGui.py') # different - to investigate
#print parse_and_convert('../../tests/python-in/testmodule09_intense.py')

"""
pyNsourceGui.py

OLD PARSING
[('log', 'Log'),            OK      self.log = Log()
-                           MISSES  from self.frame = wx.Frame    ?
-                           MISSES  self.notebook = wx.Notebook
('umlwin', 'UmlCanvas'),    OK      self.umlwin = UmlCanvas
('umlwin', 'UmlCanvas'),    x2 ?
('umlwin', 'UmlCanvas'),    x3 ?
-                           MISSES  self.multiText = wx.TextCtrl(self.asciiart, -1, ASCII_UML_HELP_MSG, style=wx.TE_MULTILINE|wx.HSCROLL)
('app', 'App'),             OK      self.app = App(context)
('config', 'ConfigObj')]    OK      self.config = ConfigObj(self.user_config_file) # doco at 
-
- lots of others missed
- ...

NEW PARSING
Latest
------
('log', 'Log')
('frame', 'wx.Frame')
('notebook', 'wx.Notebook')
('umlwin', 'UmlCanvas')
('asciiart', 'wx.Panel')
('multiText', 'wx.TextCtrl')
('app', 'App')
('config', 'ConfigObj')
('popupmenu', 'wx.Menu')
('next_menu_id', 'wx.NewId')
('printData', 'wx.PrintData')
('box', 'wx.BoxSizer')
('canvas', 'GetDiagram')    STILL WRONG should be skipped
('preview', 'wx.PrintPreview')

Previous
--------
[('log', 'Log'),            OK      self.log = Log()
('frame', 'wx'),            MORE    from self.frame = wx.Frame    ? should pick up more? **FIXED**
-                           MISSES  self.notebook = wx.Notebook(self.frame, -1)   **FIXED**
('umlwin', 'panel'),        WRONG   self.umlwin = UmlCanvas(panel, Log(), self.frame)   **FIXED**
('umlwin', 'notebook'),     WRONG   self.umlwin = UmlCanvas(self.notebook, Log(), self.frame)   **FIXED**
('umlwin', 'frame'),        WRONG   self.umlwin = UmlCanvas(self.frame, Log(), self.frame)   **FIXED**
('multiText', 'wx'),        MORE    self.multiText = wx.TextCtrl(self.asciiart, -1, ASCII_UML_HELP_MSG, style=wx.TE_MULTILINE|wx.HSCROLL)   **FIXED**
('app', 'App'),             OK      self.app = App(context)
('user_config_file',
      'config_dir'),        SHOULDSKIP   self.user_config_file = os.path.join(config_dir, PYNSOURCE_CONFIG_FILE)   **FIXED**
-                           MISSES  self.config = ConfigObj(self.user_config_file) # doco at   **FIXED**

('popupmenu', 'wx'),        MORE    self.popupmenu = wx.Menu()     # Create a menu   **FIXED**
('next_menu_id', 'wx'),     SKIP    self.next_menu_id = wx.NewId() ---- yike how to tell if LIBRARY call is class or function !!

-                           MISSES  self.printData = wx.PrintData()   **FIXED**
('printData', 'wx'),        MORE    self.printData = wx.PrintData()   **FIXED**

('box', 'wx'),              MORE    self.box = wx.BoxSizer(wx.VERTICAL)   **FIXED**
('canvas', 'umlwin')]       MORE2   self.canvas = self.umlwin.GetDiagram().GetCanvas()  STILL WRONG

notes:
with WRONG obviously its the postion of the call before bracket that is wrong.
perhaps need different number for append calls vs. assignment calls?




"""



"""
TODO

handle properties
    currentItem = property(_get_current_item)
    currentRedoItem = property(_get_current_redo_item)
    maxItems = property(_get_max_items, _set_max_items)
currently appearing as static attrs - which is ok.  Should be normal attra.


"""
