# uml workspace contains the results of a parse, for use by layout and gui
# holds shapes too, though Shape is not interrogated except for 'GetBoundingBoxMax()'
# meaning stubs could be used

class UmlWorkspace:
    def __init__(self):
        self.Clear()
        
    def Clear(self):
        self.classnametoshape = {}             # dict of classname => shape entries
        self.ClearAssociations()

    def ClearAssociations(self):
        self.associations_generalisation = []  # list of (classname, parentclassname) tuples
        self.associations_composition = []     # list of (rhs, lhs) tuples
        
    def DeleteShape(self, shape):
        classnames = self.classnametoshape.keys()
        for classname in classnames:
            if self.classnametoshape[classname] == shape:
                print 'found class to delete: ', classname
                break

        del self.classnametoshape[classname]
        """
        Too hard to remove the classname from these structures since these are tuples
        between two classes.  Harmless to keep them in here.
        """
        #if class1, class2 in self.associations_generalisation:
        #    self.associations_generalisation.remove(shape)
        #if shape in self.associations_composition:
        #    self.associations_composition.remove(shape)

    def Dump(self):
        # Debug
        from pprint import pprint
        print "="*80, "DUMP UML KNOWLEDGE: classnametoshape"
        pprint(self.classnametoshape)
        print "="*80, "associations_generalisation (class, parent)"
        pprint(self.associations_generalisation)
        print "="*80, "associations_composition (to, from)"
        pprint(self.associations_composition)
        print "======================"



