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
        #print 'self.rhs_ref_to_class', self.rhs_ref_to_class
        
    def is_rhs_reference_to_a_class(self):
        
        def rhsbrackets(): return self.v.made_rhs_call and self.v.pos_rhs_call_pre_first_bracket == 0
            
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
                

        
        #res1 = self._relaxed_is_instance_a_known_class()
        #res2 = self._is_class_creation()
        #res = res1 or res2
        #if not res:
        #    self.rhs_ref_to_class = None
        #return res

    def _calc_rhs_ref_to_class(self):
        if self.v.made_rhs_call: # one or more calls () involved on rhs
            # (which would have been either function calls or new class instance creations)
            # want names's last attr - before first call
            
            pos = self.v.pos_rhs_call_pre_first_bracket
            self.rhs_ref_to_class = self.v.rhs[pos]      
            
            # adjust for import syntax   TODO do this later?  TODO do this as part of FULL import chain checking logic
            if pos > 0 and self.v.rhs[pos-1] in self.v.imports_encountered:
                self.rhs_ref_to_class = "%s.%s" % (self.v.rhs[pos-1], self.v.rhs[pos])
                
        else:   # no calls () involved on rhs at all
            # if its an append, we want the thing inside the append statement - THEN just take the names's last attr
            # if its an assign, we want the whole rhs -                         THEN just take the names's last attr
            self.rhs_ref_to_class = self.v.rhs[-1]     # want names's last attr - no call here 
        
    def _relaxed_is_instance_a_known_class(self):
        for c in self.v.quick_parse.quick_found_classes:
            if c.lower() == self.rhs_ref_to_class.lower():
                self.rhs_ref_to_class = c  # transform into proper class name not the instance
                return True
        return False
        
    def _has_subsequent_calls(self):
        """
        TODO
        """
        pass
    
    #def _is_class_creation(self):
    #    if class_exists
    #    # Make sure the rhs is a class creation call NOT a function call.
    #    return self.v.made_rhs_call and not self.in_module_methods_etc()
    #    if self.rhs_ref_to_class

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

    def do(self, rhs, made_rhs_call, call_pos, quick_classes, quick_defs, result_should_be, rhs_ref_to_class_should_be):
        for mode in self.modes:
            v = self.get_visitor(rhs, mode)
            v.made_rhs_call = made_rhs_call
            v.quick_parse.quick_found_classes = quick_classes
            v.quick_parse.quick_found_module_defs = quick_defs
            v.pos_rhs_call_pre_first_bracket = call_pos
            
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
                Blah        3  if Blah class exists and blah is NOT in module methods but Blah IS in module methods (if Blah is a function this is unrelated to blah instance)  ==> (token transmografied)
                None        4  if Blah class doesn't exist
                None        5  if blah class exists - syntax is just plain wrong for class creation.
                            Other cases - see note *3
                
 C  a.Blah()    a.Blah      if Blah class exists and imported a
                None        no import of a exists
 D  a.b.Blah()  a.b.Blah    if Blah class exists and imported a.b
                None        no import of a.b exists
 E  a().Blah()  None        too tricky
 F  a().blah    None        too tricky
 G  a.blah      None        too tricky  *1

    *1  Note we could potentially check for either
            import a.Blah
            from a import Blah
        but its all a bit vague.

    *2  Note we used to be that unless its a module method
        or built in method, then assume its a class.
        Now logic is a bit smarter:
       
    *3  Note if class 'blah' exists instead of class 'Blah'
        then is just classic case A use cases.
"""

class TestCase_A_Classic(TestCaseBase):
    #self.w = Blah()
    #self.w.append(Blah())

    """
    if Blah class exists and its NOT in module methods
    Blah() where: class Blah - T
    """
    def test_1(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_classes=['Blah'], quick_defs=[],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')

    """
    if Blah class does NOT exist and it IS in module methods
    Blah() where: def Blah() - F
    """
    def test_2(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_classes=[], quick_defs=['Blah'],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    """
    if Blah class exists and it IS in module methods - CONTRADICATION, assume Blah is class
    Blah() where: class Blah, def Blah() - T
    """
    def test_3(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_classes=['Blah'], quick_defs=['Blah'],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')
        
    """
    if Blah class does NOT exist and its NOT in module methods - GUESS yes, if starts with uppercase letter
    Blah() where: - T
    blah() where: - F
    """
    def test_4(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_classes=[], quick_defs=[],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')

    def test_5(self):
        self.do(rhs=['blah'], made_rhs_call=True, call_pos=0, quick_classes=[], quick_defs=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)


class TestCase_B_RhsIsInstance(TestCaseBase):
    # self.w = blah
    # self.w.append(blah)
        
    def test_1(self):
        """
        if Blah class exists and blah is NOT in module methods ==> (token transmografied)
        blah where: class Blah - T
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['Blah'], quick_defs=[],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')

    def test_2(self):
        """
        if Blah class exists and blah IS in module methods (clear intent that blah is a function ref)
        blah where: class Blah, def blah() - F
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['Blah'], quick_defs=['blah'],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    def test_3(self):
        """
        if Blah class exists and blah is NOT in module methods but Blah IS in module methods (if Blah is a function this is unrelated to blah instance)  ==> (token transmografied)
        blah where: class Blah, def Blah() - T
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['Blah'], quick_defs=['Blah'],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')

    def test_4(self):
        """
        if Blah class doesn't exist
        blah where: - F
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=[], quick_defs=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)

        # the state of module methods doesn't matter:
        # blah where: def Blah() - F
        # blah where: def blah() - F
        
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=[], quick_defs=['Blah'],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=[], quick_defs=['blah'],
                result_should_be=False, rhs_ref_to_class_should_be=None)


    def test_5(self):
        """
        if blah class exists - syntax is just plain wrong for class creation.
        blah where: class blah - F
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['blah'], quick_defs=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)

        # the state of module methods doesn't matter:
        # blah where: class blah, def Blah() - F

        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_classes=['blah'], quick_defs=['Blah'],
                result_should_be=False, rhs_ref_to_class_should_be=None)


class TestCase_C_AttrBeforeClassic(TestCaseBase):
    # self.w = a.Blah()
    # self.w.append(a.Blah())

    def test_1_class_Blah_exists(self):
        """
        If class 'Blah' exists  ==> thus is class creation of a.Blah
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=1, quick_classes=['Blah'], quick_defs=[],
                result_should_be=True, rhs_ref_to_class_should_be='a.Blah')

    def test_2_class_Blah_doesnt_exist(self):
        """
        Else ==> Mere function call. No relaxed instance to class translation allowed cos its a call not an instance.
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=1, quick_classes=[], quick_defs=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        


class TestCase_D_MultipleAttrBeforeClassic(TestCaseBase):
    # self.w = a.b.Blah()
    # self.w.append(a.b.Blah())
    pass


class TestCase_E_DoubleCall(TestCaseBase):
    # self.w = a().Blah()
    # self.w.append(a().Blah())
    pass


class TestCase_F_CallThenTrailingInstance(TestCaseBase):
    # self.w = a().blah
    # self.w.append(a().blah)
    pass


class TestCase_G_AttrBeforeRhsInstance(TestCaseBase):
    # self.w = a.blah
    # self.w.append(a.blah)

    def test_1_no_classes_defined(self):
        """
        Whether or not 'blah' class exists, syntax is just plain wrong for class creation.
        Presence of preceding a. doesn't make a difference.
        """
        self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_classes=[], quick_defs=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    def test_2_blah_class_defined(self):
        self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_classes=['blah'], quick_defs=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    def test_3_Blah_class_defined_transmogrify(self):
        """
        If class 'Blah' exists, do we transmogrify from a.blah into a reference
        to an instance of a class a.Blah? Yes but only if have imported those references e.g.
            import a.Blah
            from a import Blah
        but this is all getting too tricky and vague guesswork.  
        """
        pass
        #Difficult !!
        
        #self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_classes=['Blah'], quick_defs=[],
        #        result_should_be=True, rhs_ref_to_class_should_be='Blah')

    
def suite():
    #suite1 = unittest.makeSuite(TestCase_A_Classic, 'test')
    suite2 = unittest.makeSuite(TestCase_B_RhsIsInstance, 'test')
    #suite3 = unittest.makeSuite(TestCase_C_AttrBeforeClassic, 'test')
    #suite4 = unittest.makeSuite(TestCase_D_MultipleAttrBeforeClassic, 'test')
    #suite5 = unittest.makeSuite(TestCase_E_DoubleCall, 'test')
    #suite6 = unittest.makeSuite(TestCase_F_CallThenTrailingInstance, 'test')
    #suite7 = unittest.makeSuite(TestCase_G_AttrBeforeRhsInstance, 'test')
    #alltests = unittest.TestSuite((suite1, suite2, suite3, suite4, suite5, suite6, suite7))
    #alltests = unittest.TestSuite((suite1, ))
    alltests = unittest.TestSuite((suite2, ))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()

            