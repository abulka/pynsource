# uml workspace contains the results of a parse, for use by layout and gui
# holds shapes too, though Shape is not interrogated except for 'GetBoundingBoxMax()'
# meaning stubs could be used

import random
import sys
sys.path.append("../Research/layout force spring")
from graph import Graph, GraphNode

class UmlGraph(Graph):

    def NotifyCreateNewNode(self, id, l, t, w, h):
        # subclasses overriding, opportunity to create different instance type
        return UmlNode(id, l, t, w, h)

    def NotifyOfNodeBeingPersisted(self, node):
        # subclass overriding, opportunity to inject additional persistence dict info
        return ", 'attrs':'%s', 'meths':'%s'" % ('|'.join(node.attrs), '|'.join(node.meths))

    def NotifyOfEdgeBeingPersisted(self, edge):
        # subclass overriding, opportunity to inject additional persistence dict info
        return ", 'uml_edge_type':'%s'" % (edge['uml_edge_type'])

    def NotifyOfNodeCreateFromPersistence(self, node, data):
        # subclass overriding, opportunity to add attributes to node
        if data.get('attrs', ""):
            node.attrs = data['attrs'].split('|')
        if data.get('meths', ""):
            node.meths = data['meths'].split('|')

    def NotifyOfEdgeCreateFromPersistence(self, edge, data):
        # subclass overriding, opportunity to add attributes to edge
        if data.get('uml_edge_type', ""):
            edge['uml_edge_type'] = data['uml_edge_type']
    
class UmlNode(GraphNode):
    def __init__(self, id, left, top, width=60, height=60, attrs=[], meths=[]):
        GraphNode.__init__(self, id, left, top, width=60, height=60)
        self.attrs = attrs
        self.meths = meths
        self.shape = None

    def get_id(self):
        return self.id
    def set_id(self, val):
        self.id = val
    classname = property(get_id, set_id)
    
class UmlWorkspace:
    def __init__(self):
        self.graph = UmlGraph()
        self.Clear()
        
    def Clear(self):
        self.classnametoshape = {}             # dict of classname => shape entries
        self.ClearAssociations()
        self.graph.Clear()

    def ClearAssociations(self):
        self.associations_generalisation = []  # list of (classname, parentclassname) tuples
        self.associations_composition = []     # list of (rhs, lhs) tuples
        
    def DeleteShape(self, shape):
        classnames = self.classnametoshape.keys()
        for classname in classnames:
            if self.classnametoshape[classname] == shape:
                print 'found class to delete: ', classname
                break

        self.graph.DeleteNodeById(shape.node.id)
        print 'delete node shape.node.id', shape.node.id

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
        def line(ch='-'):
            return ch*70
        from pprint import pprint
        print line('*'), "DUMP UML KNOWLEDGE: classnametoshape"
        pprint(self.classnametoshape)
        print line(), "associations_generalisation (class, parent)"
        pprint(self.associations_generalisation)
        print line(), "associations_composition (to, from)"
        pprint(self.associations_composition)
        print line('='), self.graph
        for node in self.graph.nodes:
            pprint(node)
        print line('-')

    def AddUmlNode(self, id, attrs=[], meths=[]):
        node = self.graph.FindNodeById(id)
        if node:
            # could merge the nodes and their attributes etc. ?
            #print 'Skipping', node.classname, 'already built shape...'
            return node
        t,l,w,h = random.randint(0, 100),random.randint(0,100),random.randint(60, 160),random.randint(60,160)
        node = UmlNode(id, t, l, w, h, attrs=attrs, meths=meths)
        node = self.graph.AddNode(node)
        return node

    def AddSimpleNode(self, id):
        if self.graph.FindNodeById(id):
            id += str(random.randint(1,9999))
        t,l,w,h = random.randint(0, 100),random.randint(0,100),random.randint(60, 160),random.randint(60,160)
        node = GraphNode(id, t, l, w, h)
        node = self.graph.AddNode(node)
        return node
        

