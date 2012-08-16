import sys
sys.path.append("../../src")
from architecture_support import whosdaddy, whosgranddaddy
#from core_parser import ClassEntry, Attribute
from keywords import pythonbuiltinfunctions

class RhsAnalyser:
    """
    Usage:
        is_rhs_reference_to_a_class()
            Returns t/f
            Rsulting reference in .rhs_ref_to_class
            
    Background:
        You get here if
            self.made_assignment OR
            self.made_append_call    ( you can't have these both be true at the same time )
        and if
            self.lhs[0] == 'self' AND
            len(self.rhs) > 0:
        
    Scenarios:
        ... = Blah()                                want name - before first call which is Blah
        ...append(Blah())                           want name - before first call which is Blah (remember the append is on the lhs not the rhs)
        
        ... = blah                                  may be reinterpreted as      = Blah()  if Blah class found - a relaxed rule I admit
        ...append(blah)                             may be reinterpreted as append(Blah()) if Blah class found - a relaxed rule I admit
        
        ... = 10                                    won't get here because no rhs
        ...append(10)                               won't get here because no rhs

        new cases just coming in!
        -------------------------
        * rule seems to be get name or if the name has attributes, the
          name's last attr before the first call (if there is a call)
        
        ... = a.Blah()                              want names's last attr - before first call
        ... = a.blah                                want names's last attr - no call here 
        ..append(a.blah)                            look inside append - want names's last attr - no call here 
        ... = Blah.MaxListSize                      want names's last attr - no call here - no rhs class ref here !!
        ... = a.Blah(b.Fred())                      want names's last attr - before first call
        ... = Blah(b=self)                          want name              - before first call
        
        more new cases just coming in!
        ------------------------------
        * rule seems to be to identify the . call chain before
        the class candidate and ensure they are in the imports
        Also if there are subsequent . calls after the class candidate
        disqualify
        
        ...append(" "*self.curr_width)              skip - want names's last attr - no call here - curr_width has no corresponding class
        ... = self.umlwin.GetDiagram().GetCanvas()  skip - would be too relaxed to interpret GetDiagram as a class.
                                                            especially since there are further . calls
                                                            especially since self.umlwin is not an import
        ... = a.GetDiagram()                        skip - unless a is an import
        ... = a.b.GetDiagram()                      skip - unless a.b is an import
        ... = self.GetDiagram()                     skip - unless self is an import
        ... = self.a.GetDiagram()                   skip - unless self.a is an import

    """

    def __init__(self, visitor):
        self.v = visitor
        
        assert len(self.v.rhs) > 0
        assert not (self.v.made_assignment and self.v.made_append_call) # these both can't be true
        
        self.rhs_ref_to_class = None
        self._calc_rhs_ref_to_class()
    
    @property
    def pos(self):
        return self.v.pos_rhs_call_pre_first_bracket
    @property
    def prefix(self):
        return ".".join(self.v.rhs[0:self.pos])

    def is_prefixed_class_call(self):
        return self.v.made_rhs_call and self.pos > 0

    def is_syntax_after_class_call(self):
        lastpos = len(self.v.rhs) - 1
        return self.v.made_rhs_call and lastpos > self.pos

    def is_prefixed_instance(self):
        return not self.v.made_rhs_call and len(self.v.rhs) > 1
        
    def is_rhs_reference_to_a_class(self):
        
        def rhsbrackets():
            return self.v.made_rhs_call and self.v.pos_rhs_call_pre_first_bracket == 0

        if self.is_prefixed_instance(): #G
            self.rhs_ref_to_class = None
            return False

        if self.v.made_rhs_call and self.is_syntax_after_class_call():  #E, #F, #G
            self.rhs_ref_to_class = None
            return False
            
        if self.is_prefixed_class_call(): #C, #D
            if self.prefix in self.v.imports_encountered: # C1, # D4
                self.rhs_ref_to_class = "%s.%s" % (self.prefix, self.v.rhs[self.pos])
                return True
            else:
                self.rhs_ref_to_class = None
                return False
            
        if self.class_exists() and not self.in_module_methods_etc() and rhsbrackets(): # A1
            return True
        
        if self.class_exists(instance_check=True) and not self.in_module_methods_etc() and not rhsbrackets(): # B1
            self.rhs_ref_to_class = self.upper_just_first_char()
            return True
        
        if not self.class_exists() and self.in_module_methods_etc() and rhsbrackets(): # A2
            self.rhs_ref_to_class = None
            return False
        
        if self.class_exists(instance_check=True) and self.in_module_methods_etc() and not rhsbrackets(): # B2
            self.rhs_ref_to_class = None
            return False

        if self.class_exists() and self.in_module_methods_etc() and rhsbrackets(): # A3
            return True
        
        if not self.class_exists() and not self.in_module_methods_etc() and rhsbrackets(): # A4
            if self.rhs_ref_to_class[0].isupper():  # GUESS yes, if starts with uppercase letter
                return True
            else:
                self.rhs_ref_to_class = None
                return False
                
        self.rhs_ref_to_class = None
        return False
                
    def _calc_rhs_ref_to_class(self):
        """
        IF made_rhs_call then one or more calls () involved on rhs (which would
        have been either function calls or new class instance creations) thus
        want names's last attr - before first call.
        ELSE no calls () involved on rhs at all. Thus if its an append, we want
        the thing inside the append statement - if its an assign, we have the
        whole rhs - in either case just take the names's last attr.
        """
        if self.v.made_rhs_call:
            self.rhs_ref_to_class = self.v.rhs[self.pos]      
        else:
            self.rhs_ref_to_class = self.v.rhs[-1]     # want instance names's last attr - no call here 
        
    def in_module_methods_etc(self):
        return self.rhs_ref_to_class in pythonbuiltinfunctions or \
               self.rhs_ref_to_class in self.v.quick_parse.quick_found_module_defs

    def class_exists(self, instance_check=False):
        if instance_check:
            c = self.upper_just_first_char()
        else:
            c = self.rhs_ref_to_class
        return c in self.v.quick_parse.quick_found_classes
    
    def upper_just_first_char(self):
        return self.rhs_ref_to_class[0].upper() + self.rhs_ref_to_class[1:]

            
import unittest
import sys


class MockQuickParse:
    def __init__(self):
        self.quick_found_classes = []
        self.quick_found_module_defs = []
        self.quick_found_module_attrs = []


class MockOldParseModel:
    def __init__(self):
        self.classlist = {}
        self.modulemethods = []

            
class MockVisitor:
    def __init__(self, quick_parse):
        self.model = MockOldParseModel()
        self.stack_classes = []
        self.stack_module_functions = [False]
        self.quick_parse = quick_parse
        self.init_lhs_rhs()
        self.imports_encountered = []

    def init_lhs_rhs(self):
        self.lhs = []
        self.rhs = []
        self.lhs_recording = True
        self.made_rhs_call = False
        self.made_assignment = False
        self.made_append_call = False
        self.made_import = False
        self.pos_rhs_call_pre_first_bracket = None


class TestCaseBase(unittest.TestCase):

    def setUp(self):
        self.qp = MockQuickParse()
        self.v = MockVisitor(self.qp)
        self.v.imports_encountered = ['a']
        self.v.model.modulemethods = []
        
        self.modes = ['assign', 'append']

    def get_visitor(self, rhs, assign_or_append):
        self.v.rhs = rhs
        if assign_or_append == 'assign':
            self.v.made_append_call = False
            self.v.made_assignment = True
        else:
            self.v.made_append_call = True
            self.v.made_assignment = False
        return self.v

    def do(self, rhs, made_rhs_call, call_pos, quick_classes, quick_defs, result_should_be, rhs_ref_to_class_should_be, imports):
        for mode in self.modes:
            v = self.get_visitor(rhs, mode)
            v.made_rhs_call = made_rhs_call
            v.quick_parse.quick_found_classes = quick_classes
            v.quick_parse.quick_found_module_defs = quick_defs
            v.pos_rhs_call_pre_first_bracket = call_pos
            v.imports_encountered = imports
            
            ra = RhsAnalyser(v)
            self.assertEqual(ra.is_rhs_reference_to_a_class(), result_should_be)
            self.assertEqual(ra.rhs_ref_to_class,              rhs_ref_to_class_should_be)

"""
    RhsAnalyser Summary of Logic
    ----------------------------
    
    INPUT:
    rhs call
    or append   OUTPUT
    expression  token       Logic and notes
    ==========|===========|=======================
 A  Blah()      Blah        1  if Blah class exists and its NOT in module methods  *2
                None        2  if Blah class does NOT exist and it IS in module methods
                Blah        3  if Blah class exists and it IS in module methods - CONTRADICATION, assume Blah is class
                Blah        4  if Blah class does NOT exist and its NOT in module methods - GUESS yes, if starts with uppercase letter
                
 B  blah        Blah        1  if Blah class exists and blah is NOT in module methods ==> (token transmografied)
                None        2  if Blah class exists and blah IS in module methods (clear intent that blah is a function ref)
                Blah        3  if Blah class exists and blah is NOT in module methods but Blah IS in module methods
                                (if Blah is a function this is unrelated to blah instance)  ==> (token transmografied)
                None        4  if Blah class doesn't exist
                None        5  if blah class exists - syntax is just plain wrong for class creation.
                            *  Other cases - see note *3
                
 C  a.Blah()    a.Blah      1 where: class Blah, import a - T a.Blah
                a.Blah      2 where: import a - T a.Blah   Most common case, e.g. self.popupmenu = wx.Menu() where all you know about is that you imported wx.
                None        3 where: class Blah - F
                None        4 where: - F
        
                
 D  a.b.Blah()  a.b.Blah    if Blah class exists and imported a.b
                a.b.Blah    if NO Blah class exists and imported a.b   Most common case, see above #C2
                None        no import of a.b exists
                
 E  a().Blah()  None        too tricky
 F  a().blah    None        too tricky
 G  a.blah      None        too tricky  *1

    *1 First of all, whether or not 'blah' class exists, syntax is just plain
        wrong for class creation. Presence of preceding a. doesn't make a
        difference.
        
       Secondly, sure we could potentially check for either
            import a.Blah
            from a import Blah
        and transmogrify, but its all a bit vague, safer to just return F/None.

    *2 Note we used to be that unless its a module method
       or built in method, then assume its a class. Now logic is a bit smarter:
       
    *3 Note if class 'blah' exists instead of class 'Blah'
        then is just classic case A use cases.
"""

class TestCase_A_Classic(TestCaseBase):
    #self.w = Blah()
    #self.w.append(Blah())

    """
    if Blah class exists and its NOT in module methods
    Blah() where: class Blah - T Blah
    """
    def test_1(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_classes=['Blah'], quick_defs=[], imports = [],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')

    """
    if Blah class does NOT exist and it IS in module methods
    Blah() where: def Blah() - F
    """
    def test_2(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_classes=[], quick_defs=['Blah'], imports = [],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    """
    if Blah class exists and it IS in module methods - CONTRADICATION, assume Blah is class
    Blah() where: class Blah, def Blah() - T Blah
    """
    def test_3(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_classes=['Blah'], quick_defs=['Blah'], imports = [],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')
        
    """
    if Blah class does NOT exist and its NOT in module methods - GUESS yes, if starts with uppercase letter
    Blah() where: - T Blah
    blah() where: - F
    """
    def test_4(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_classes=[], quick_defs=[], imports = [],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')

    def test_5(self):
        self.do(rhs=['blah'], made_rhs_call=True, call_pos=0, quick_classes=[], quick_defs=[], imports = [],
                result_should_be=False, rhs_ref_to_class_should_be=None)


class TestCase_B_RhsIsInstance(TestCaseBase):
    # self.w = blah
    # self.w.append(blah)
        
    def test_1(self):
        """
        if Blah class exists and blah is NOT in module methods ==> (token transmografied)
        blah where: class Blah - T Blah
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['Blah'], quick_defs=[], imports = [],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')

    def test_2(self):
        """
        if Blah class exists and blah IS in module methods (clear intent that blah is a function ref)
        blah where: class Blah, def blah() - F
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['Blah'], quick_defs=['blah'], imports = [],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    def test_3(self):
        """
        if Blah class exists and blah is NOT in module methods but Blah IS in module methods
            (if Blah is a function this is unrelated to blah instance)  ==> (token transmografied)
        blah where: class Blah, def Blah() - T Blah
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['Blah'], quick_defs=['Blah'], imports = [],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')

    def test_4(self):
        """
        if Blah class doesn't exist
        blah where: - F
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=[], quick_defs=[], imports = [],
                result_should_be=False, rhs_ref_to_class_should_be=None)

        # the state of module methods doesn't matter:
        # blah where: def Blah() - F
        # blah where: def blah() - F
        
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=[], quick_defs=['Blah'], imports = [],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=[], quick_defs=['blah'], imports = [],
                result_should_be=False, rhs_ref_to_class_should_be=None)


    def test_5(self):
        """
        if blah class exists - syntax is just plain wrong for class creation.
        blah where: class blah - F
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['blah'], quick_defs=[], imports = [],
                result_should_be=False, rhs_ref_to_class_should_be=None)

        # the state of module methods doesn't matter:
        # blah where: class blah, def Blah() - F

        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['blah'], quick_defs=['Blah'], imports = [],
                result_should_be=False, rhs_ref_to_class_should_be=None)


class TestCase_C_AttrBeforeClassic(TestCaseBase):
    # self.w = a.Blah()
    # self.w.append(a.Blah())

    def test_1(self):
        """
        a.Blah() where: class Blah, import a - T a.Blah
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=1, quick_classes=['Blah'], quick_defs=[], imports=['a'],
                result_should_be=True, rhs_ref_to_class_should_be='a.Blah')

    def test_2(self):
        """
        Most common case, e.g. self.popupmenu = wx.Menu() where all you know about is that you imported wx.
        a.Blah() where: import a - T a.Blah
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=1, quick_classes=[], quick_defs=[], imports=['a'],
                result_should_be=True, rhs_ref_to_class_should_be='a.Blah')

    def test_3(self):
        """
        a.Blah() where: class Blah - F
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=1, quick_classes=['Blah'], quick_defs=[], imports=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)

    def test_4(self):
        """
        a.Blah() where: - F
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=1, quick_classes=[], quick_defs=[], imports=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)



class TestCase_D_MultipleAttrBeforeClassic(TestCaseBase):
    # self.w = a.b.Blah()
    # self.w.append(a.b.Blah())

    def test_1(self):
        """
        a.b.Blah() where: class Blah, import a.b - T a.b.Blah
        """
        self.do(rhs=['a', 'b', 'Blah'], made_rhs_call=True, call_pos=2, quick_classes=['Blah'], quick_defs=[], imports=['a.b'],
                result_should_be=True, rhs_ref_to_class_should_be='a.b.Blah')

    def test_2(self):
        """
        a.b.Blah() where: import a.b - T a.b.Blah()
        """
        self.do(rhs=['a', 'b', 'Blah'], made_rhs_call=True, call_pos=2, quick_classes=[], quick_defs=[], imports=['a.b'],
                result_should_be=True, rhs_ref_to_class_should_be='a.b.Blah')

    def test_3(self):
        """
        a.b.Blah() where: class Blah, import b - F
        """
        self.do(rhs=['a', 'b', 'Blah'], made_rhs_call=True, call_pos=2, quick_classes=['Blah'], quick_defs=[], imports=['b'],
                result_should_be=False, rhs_ref_to_class_should_be=None)

    def test_4(self):
        """
        a.b.Blah() where: class Blah, import a - F
        """
        self.do(rhs=['a', 'b', 'Blah'], made_rhs_call=True, call_pos=2, quick_classes=['Blah'], quick_defs=[], imports=['a'],
                result_should_be=False, rhs_ref_to_class_should_be=None)


class TestCase_E_DoubleCall(TestCaseBase):
    # self.w = a().Blah()
    # self.w.append(a().Blah())

    def test_1(self):
        """
        a().Blah() where: class Blah - F
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=0, quick_classes=['Blah'], quick_defs=[], imports=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)

    def test_2(self):
        """
        a().Blah() where: class a - F
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=0, quick_classes=['a'], quick_defs=[], imports=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)

class TestCase_F_CallThenTrailingInstance(TestCaseBase):
    # self.w = a().blah
    # self.w.append(a().blah)

    def test_1(self):
        """
        a().blah where: class Blah - F
        """
        self.do(rhs=['a', 'blah'], made_rhs_call=True, call_pos=0, quick_classes=['Blah'], quick_defs=[], imports=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)


class TestCase_G_AttrBeforeRhsInstance(TestCaseBase):
    # self.w = a.blah
    # self.w.append(a.blah)

    def test_1(self):
        """
        a.blah where: - F
        """
        self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_classes=[], quick_defs=[], imports=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    def test_2(self):
        """
        a.blah where: class a - F
        """
        self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_classes=['a'], quick_defs=[], imports=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)

    def test_3(self):
        """
        a.blah where: class blah - F
        """
        self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_classes=['blah'], quick_defs=[], imports=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    def test_4(self):
        """
        a.blah where: class Blah - F
        """
        self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_classes=['Blah'], quick_defs=[], imports=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)

    def test_5(self):
        """
        a.blah where: class Blah, imports a - F
        """
        self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_classes=['Blah'], quick_defs=[], imports=['a'],
                result_should_be=False, rhs_ref_to_class_should_be=None)

class TestCase_AddHoc(TestCaseBase):

    def test_1(self):
        """
        self.flageditor = FlagEditor(gamestatusstate=self)
        a.blah where: class Blah, imports a - F
        """
        self.do(rhs=['FlagEditor'], made_rhs_call=True, call_pos=0, quick_classes=[], quick_defs=[], imports=[],
                result_should_be=True, rhs_ref_to_class_should_be='FlagEditor')
    
def suite():
    #suite1 = unittest.makeSuite(TestCase_A_Classic, 'test')
    #suite2 = unittest.makeSuite(TestCase_B_RhsIsInstance, 'test')
    #suite3 = unittest.makeSuite(TestCase_C_AttrBeforeClassic, 'test')
    #suite4 = unittest.makeSuite(TestCase_D_MultipleAttrBeforeClassic, 'test')
    #suite5 = unittest.makeSuite(TestCase_E_DoubleCall, 'test')
    #suite6 = unittest.makeSuite(TestCase_F_CallThenTrailingInstance, 'test')
    #suite7 = unittest.makeSuite(TestCase_G_AttrBeforeRhsInstance, 'test')
    suite8 = unittest.makeSuite(TestCase_AddHoc, 'test')
    #alltests = unittest.TestSuite((suite1, suite2, suite3, suite4, suite5, suite6, suite7))
    alltests = unittest.TestSuite((suite8, ))
    #alltests = unittest.TestSuite((suite3, suite4))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()

            