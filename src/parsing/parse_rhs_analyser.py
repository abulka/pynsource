from common.architecture_support import whosdaddy, whosgranddaddy
from parsing.keywords import pythonbuiltinfunctions


class RhsAnalyser:
    """
    Usage:
        ra.is_rhs_reference_to_a_class()

        Returns t/f
        Resulting probably reference to class is in ra.rhs_ref_to_class
            
    Example:
        ra = RhsAnalyser(v)
        result = ra.is_rhs_reference_to_a_class()
        print ra.rhs_ref_to_class
            
    Background:
        You get here if
            self.made_assignment OR
            self.made_append_call    ( you can't have these both be true at the same time )
        and if
            self.lhs[0] == 'self' AND
            len(self.rhs) > 0:
        
    Scenarios:
        Note there are use cases A-G with sub tests 1...5 and I use the syntax
        e.g. #B2 to refer to Test Class B test method 2.
        
        The shorthand / domain specific language syntax "where: class Blah,
        import a - T a.Blah" means assuming there exists a class 'Blah' found in
        the quick find list (supplied by visitor object), and 'a' is found in
        the lists of imports (supplied by visitor object) the result should be
        True with a ra.rhs_ref_to_class of a.Blah

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

    def __init__(self, visitor):
        self.v = visitor

        assert len(self.v.rhs) > 0
        assert not (self.v.made_assignment and self.v.made_append_call)  # these both can't be true

        self.rhs_ref_to_class = None
        self.calc_rhs_ref_to_class()

    def calc_rhs_ref_to_class(self):
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
            self.rhs_ref_to_class = self.v.rhs[-1]  # want instance names's last attr - no call here

    def in_module_methods_etc(self):
        return (
            self.rhs_ref_to_class in pythonbuiltinfunctions
            or self.rhs_ref_to_class in self.v.quick_parse.quick_found_module_defs
        )

    def class_exists(self, instance_check=False):
        if instance_check:
            c = self.upper_just_first_char()
        else:
            c = self.rhs_ref_to_class
        return c in self.v.quick_parse.quick_found_classes

    def upper_just_first_char(self):
        return self.rhs_ref_to_class[0].upper() + self.rhs_ref_to_class[1:]

    @property
    def pos(self):
        return self.v.pos_rhs_call_pre_first_bracket

    @property
    def prefix(self):
        return ".".join(self.v.rhs[0 : self.pos])

    def is_prefixed_class_call(self):
        return self.v.made_rhs_call and self.pos > 0

    def is_prefixed_instance(self):
        return not self.v.made_rhs_call and len(self.v.rhs) > 1

    def is_there_syntax_after_class_call(self):
        lastpos = len(self.v.rhs) - 1
        return self.v.made_rhs_call and lastpos > self.pos

    def is_rhs_reference_to_a_class(self):
        """
        This is the main API method to call.
        Returns T/F
        """

        if self.is_prefixed_instance():  # G
            self.rhs_ref_to_class = None
            return False

        if self.v.made_rhs_call and self.is_there_syntax_after_class_call():  # E, #F, #G
            self.rhs_ref_to_class = None
            return False

        if self.is_prefixed_class_call():  # C, #D
            if self.prefix in self.v.imports_encountered:  # C1, # D4
                self.rhs_ref_to_class = "%s.%s" % (self.prefix, self.v.rhs[self.pos])
                return True
            else:
                self.rhs_ref_to_class = None
                return False

        assert not self.is_prefixed_class_call()

        if self.class_exists() and not self.in_module_methods_etc() and self.v.made_rhs_call:  # A1
            return True

        if (
            self.class_exists(instance_check=True)
            and not self.in_module_methods_etc()
            and not self.v.made_rhs_call
        ):  # B1
            self.rhs_ref_to_class = self.upper_just_first_char()
            return True

        if not self.class_exists() and self.in_module_methods_etc() and self.v.made_rhs_call:  # A2
            self.rhs_ref_to_class = None
            return False

        if (
            self.class_exists(instance_check=True)
            and self.in_module_methods_etc()
            and not self.v.made_rhs_call
        ):  # B2
            self.rhs_ref_to_class = None
            return False

        if self.class_exists() and self.in_module_methods_etc() and self.v.made_rhs_call:  # A3
            return True

        if (
            not self.class_exists() and not self.in_module_methods_etc() and self.v.made_rhs_call
        ):  # A4
            if self.rhs_ref_to_class[0].isupper():  # GUESS yes, if starts with uppercase letter
                return True
            else:
                self.rhs_ref_to_class = None
                return False

        self.rhs_ref_to_class = None
        return False
