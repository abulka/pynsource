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
        print 'self.rhs_ref_to_class', self.rhs_ref_to_class
        
    def is_rhs_reference_to_a_class(self):
        res1 = self._relaxed_is_instance_a_known_class()
        res2 = self._is_class_creation()
        print res1, res2
        return res1 or res2

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
    
    def _is_class_creation(self):            
        # Make sure the rhs is a class creation call NOT a function call.
        t = self.rhs_ref_to_class
        return self.v.made_rhs_call and \
            t not in pythonbuiltinfunctions and \
            t not in self.v.model.modulemethods


            
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

    def do(self, rhs, made_rhs_call, call_pos, quick_found_classes, result_should_be, rhs_ref_to_class_should_be):
        for mode in self.modes:
            v = self.get_visitor(rhs, mode)
            v.made_rhs_call = made_rhs_call
            v.quick_parse.quick_found_classes = quick_found_classes
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
 A  Blah()      Blah        if Blah class exists    
                None        if Blah class doesn't exist     
 B  blah        Blah        if Blah class exists  (token transmografied)
                None        if Blah class doesn't exist     
 C  a.Blah()    a.Blah      if Blah class exists and imported a     
                None        no import of a exists   
 D  a.b.Blah()  a.b.Blah    if Blah class exists and imported a.b   
                None        no import of a.b exists 
 E  a().Blah()  None        too tricky      
 F  a().blah    None        too tricky      
 G  a.blah      None        too tricky  *1
    
    *1 Note we could potentially check for either 
        import a.Blah
        from a import Blah
    but its all a bit vague.
"""


class TestCase_A_Classic(TestCaseBase):
    #self.w = Blah()
    #self.w.append(Blah())

    """
    If Blah class exists ==> True, Blah
    """
    def test_1_BlahClassExists(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_found_classes=['Blah'],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')

    """
    else ==> False, None
    """
    def test_2_NoClassesExist(self):
        self.do(rhs=['Blah'], made_rhs_call=True, call_pos=0, quick_found_classes=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)


class TestCase_B_RhsIsInstance(TestCaseBase):
    # self.w = blah
    # self.w.append(blah)
        
    def test_1_no_classes_defined(self):
        """
        Whether or not 'blah' class exists,
            # syntax is just plain wrong for class creation.
            is_rhs_reference_to_a_class ==> False
            ra.rhs_ref_to_class ==> None
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_found_classes=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    def test_2_blah_class_defined(self):
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_found_classes=['blah'],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    def test_3_Blah_class_defined_transmogrify(self):
        """
        If class 'Blah' exists
            # If 'Blah' class exists, relaxed instance to class translation allowed.
            is_rhs_reference_to_a_class ==> True
            ra.rhs_ref_to_class ==> Blah            # TRANSMOGRIFIED!
        """
        self.do(rhs=['blah'], made_rhs_call=False, call_pos=0, quick_found_classes=['Blah'],
                result_should_be=True, rhs_ref_to_class_should_be='Blah')


class TestCase_C_AttrBeforeClassic(TestCaseBase):
    # self.w = a.Blah()
    # self.w.append(a.Blah())

    def test_1_class_Blah_exists(self):
        """
        If class 'Blah' exists  ==> thus is class creation of a.Blah
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=1, quick_found_classes=['Blah'],
                result_should_be=True, rhs_ref_to_class_should_be='a.Blah')

    def test_2_class_Blah_doesnt_exist(self):
        """
        Else ==> Mere function call. No relaxed instance to class translation allowed cos its a call not an instance.
        """
        self.do(rhs=['a', 'Blah'], made_rhs_call=True, call_pos=1, quick_found_classes=[],
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
        self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_found_classes=[],
                result_should_be=False, rhs_ref_to_class_should_be=None)
        
    def test_2_blah_class_defined(self):
        self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_found_classes=['blah'],
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
        
        #self.do(rhs=['a', 'blah'], made_rhs_call=False, call_pos=0, quick_found_classes=['Blah'],
        #        result_should_be=True, rhs_ref_to_class_should_be='Blah')

    
def suite():
    suite1 = unittest.makeSuite(TestCase_A_Classic, 'test')
    suite2 = unittest.makeSuite(TestCase_B_RhsIsInstance, 'test')
    suite3 = unittest.makeSuite(TestCase_C_AttrBeforeClassic, 'test')
    suite4 = unittest.makeSuite(TestCase_D_MultipleAttrBeforeClassic, 'test')
    suite5 = unittest.makeSuite(TestCase_E_DoubleCall, 'test')
    suite6 = unittest.makeSuite(TestCase_F_CallThenTrailingInstance, 'test')
    suite7 = unittest.makeSuite(TestCase_G_AttrBeforeRhsInstance, 'test')
    alltests = unittest.TestSuite((suite1, suite2, suite3, suite4, suite5, suite6, suite7))
    return alltests

def main():
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()

            