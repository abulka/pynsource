"""
Compare old and new parsing

"""

import os
import difflib

import sys
sys.path.append("../src")
from common.logwriter import LogWriter, LogWriterNull
from parsing.dump_pmodel import dump_old_structure
from parsing.api import old_parser, new_parser

global log

DEBUGINFO = 1
LOG_TO_CONSOLE = 0

last_diff_s = ""

def parse_old_and_new(in_filename, print_diffs=True):
    global log
    if DEBUGINFO:
        log = LogWriter(in_filename, print_to_console=LOG_TO_CONSOLE)
    else:
        log = LogWriterNull()
    
    def oldparse():
        model, debuginfo = old_parser(in_filename)
        d1 = dump_old_structure(model)
        log.out_wrap_in_html(d1, style_class='dump1')
        return d1
        
    def newparse():
        model, debuginfo = new_parser(in_filename, log)
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
    results.append(parse_old_and_new(filename))
def test_not(filename, expected_diffs=None):
    # expect parse to slightly fail, with a diff matching expected_diff
    result = parse_old_and_new(filename, print_diffs=False)
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
        #print "%s OK" % msg
        return True
    else:
        print "oooops %s broken" % msg, results
        return False
        

###########

expected_diffs = {}

# ast is better, base classes with . handled
expected_diffs['testmodule08_multiple_inheritance.py'] = """
--- before.py
+++ after.py
@@ -1 +1 @@
-Fred (is module=0) inherits from ['Mary', 'MarySam'] class dependencies []
+Fred (is module=0) inherits from ['Mary', 'Sam'] class dependencies []
"""

# ast is better, (1) nested module functions ignored. (2) class actually checked
# for when relaxed attr ref to instance. (3) extra properties picked up (though
# they should be normal not static)
expected_diffs['testmodule_command_pattern.py'] = """
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
expected_diffs['testmodule_pynsource.py'] = """
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

import unittest

class TestCase_A(unittest.TestCase):
    def test_1_official_parsing(self):
        reset_tests()    
        test('python-in/testmodule01.py')
        test('python-in/testmodule02.py')
        test('python-in/testmodule03.py')
        test('python-in/testmodule04.py')
        test('python-in/testmodule05.py') # (inner classes)
        test('python-in/testmodule06.py')
        test('python-in/testmodule07.py')
        test('python-in/testmodule66.py')
        self.assertTrue(report("official parsing tests"))

    def test_2_subsidiary_parsing(self):
        reset_tests()    
        test('python-in/testmodule_printframework.py')
        test('python-in/testmodule_asciiworkspace.py')
        self.assertTrue(report("subsidiary parsing tests"))

    def test_3_ast_parsing_is_genuinely_better(self):
        # Expect these to fail cos ast parsing is genuinely better
        reset_tests()    
        test_not('python-in/testmodule08_multiple_inheritance.py', expected_diffs)
        test_not('python-in/testmodule_command_pattern.py', expected_diffs)
        test_not('python-in/testmodule_pynsource.py', expected_diffs)
        test_not('python-in/testmodule09_intense.py', expected_diffs)
        self.assertTrue(report("ast parsing is genuinely better"))
    
def suite():
    suite1 = unittest.makeSuite(TestCase_A, 'test')
    #suite2 = unittest.makeSuite(test_2_subsidiary_parsing, 'test')
    #suite3 = unittest.makeSuite(test_3_ast_parsing_is_genuinely_better, 'test')
    #suite4 = unittest.makeSuite(TestCase_D_MultipleAttrBeforeClassic, 'test')
    #suite5 = unittest.makeSuite(TestCase_E_DoubleCall, 'test')
    #suite6 = unittest.makeSuite(TestCase_F_CallThenTrailingInstance, 'test')
    #suite7 = unittest.makeSuite(TestCase_G_AttrBeforeRhsInstance, 'test')
    #suite8 = unittest.makeSuite(TestCase_AddHoc, 'test')
    #alltests = unittest.TestSuite((suite1, suite2, suite3, suite4, suite5, suite6, suite7))
    alltests = unittest.TestSuite((suite1, ))
    #alltests = unittest.TestSuite((suite1, suite2, suite3))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()
    #print parse_old_and_new('../../src/pyNsourceGui.py') # different - ok
    #print parse_old_and_new('python-in/testmodule08_multiple_inheritance.py')

