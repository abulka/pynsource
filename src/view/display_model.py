# uml workspace contains the results of a parse, for use by layout and gui
# holds shapes too, though Shape is not interrogated except for 'GetBoundingBoxMax()'
# meaning stubs could be used

import random
import sys
from .graph import Graph, GraphNode


class UmlGraph(Graph):
    def NotifyCreateNewNode(self, id, l, t, w, h):
        # subclasses overriding, opportunity to create different instance type
        return UmlNode(id, l, t, w, h)

    def NotifyOfNodeBeingPersisted(self, node):
        # subclass overriding, opportunity to inject additional persistence dict info
        return ", 'attrs':'%s', 'meths':'%s'" % ("|".join(node.attrs), "|".join(node.meths))

    def NotifyOfEdgeBeingPersisted(self, edge):
        # subclass overriding, opportunity to inject additional persistence dict info
        return ", 'uml_edge_type':'%s'" % (edge["uml_edge_type"])

    def NotifyOfNodeCreateFromPersistence(self, node, data):
        # subclass overriding, opportunity to add attributes to node
        if data.get("attrs", ""):
            node.attrs = data["attrs"].split("|")
        if data.get("meths", ""):
            node.meths = data["meths"].split("|")

    def NotifyOfEdgeCreateFromPersistence(self, edge, data):
        # subclass overriding, opportunity to add attributes to edge
        if data.get("uml_edge_type", ""):
            edge["uml_edge_type"] = data["uml_edge_type"]


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


class CommentNode(GraphNode):
    def __init__(self, id, left, top, width=60, height=60, comment=""):
        GraphNode.__init__(self, id, left, top, width=60, height=60)
        self.comment = comment
        self.shape = None

    def get_id(self):
        return self.id

    def set_id(self, val):
        self.id = val

    classname = property(get_id, set_id)


class DisplayModel:
    """
    This is the Display Model
    Referred to by context.displaymodel
    Not to be confused with context.umlcanvas which is the UmlCanvas object which is a OGL visual thing

    The 'graph' of 'nodes' is the abstract stuff, used in layout, but also containing
    the method, attributes, comment info.  Each node points to a visual shape,
    and vice versa.
    """

    def __init__(self):
        self.graph = UmlGraph()
        self.classnametoshape = {}  # dict of classname => shape entries
        self.associations_generalisation = []  # list of (classname, parentclassname) tuples
        self.associations_composition = []  # list of (rhs, lhs) tuples

        self.Clear()

    def Clear(self):
        self.classnametoshape = {}
        self.ClearAssociations()
        self.graph.Clear()

    def ClearAssociations(self):
        self.associations_generalisation = []
        self.associations_composition = []

    def decouple_node_from_shape(self, shape):
        classname = next(
            (
                classname
                for classname, shaperef in list(self.classnametoshape.items())
                if shaperef == shape
            )
        )  # see http://johnstachurski.net/lectures/generators.html on how generators work, which can be built from list comprehension syntax
        print("found class to decouple: ", classname)

        del self.classnametoshape[classname]
        """
        Too hard to remove the classname from these structures since these are tuples
        between two classes.  Harmless to keep them in here.
        """
        # if class1, class2 in self.associations_generalisation:
        #    self.associations_generalisation.remove(shape)
        # if shape in self.associations_composition:
        #    self.associations_composition.remove(shape)

    def delete_node_for_shape(self, shape):
        self.decouple_node_from_shape(shape)

        self.graph.DeleteNodeById(shape.node.id)
        print("deleted node shape.node.id", shape.node.id)

    def Dump(self):
        def line(ch="-"):
            return ch * 70

        from pprint import pprint

        print()
        print("     DisplayModel    ")
        print()
        print(line("*"), "DUMP UML KNOWLEDGE: classnametoshape")
        pprint(self.classnametoshape)
        print(line(), "associations_generalisation (class, parent)")
        pprint(self.associations_generalisation)
        print(line(), "associations_composition (to, from)")
        pprint(self.associations_composition)
        print()
        print("     GRAPH Model     ")
        print()
        print(line("-"), "graph.nodeSet is")
        pprint(list(self.graph.nodeSet.keys()))
        print(line("-"), "self.graph.nodes")
        print()
        for node in self.graph.nodes:
            print(node)
        print(line("-"), "self.graph.edges")
        for edge in self.graph.edges:
            source = edge["source"].id
            target = edge["target"].id
            edgetype = edge["uml_edge_type"]
            print("from %40s --> %-40s  (%s)" % (source, target, edgetype))

    def AddUmlNode(self, id, attrs=[], meths=[]):
        node = self.graph.FindNodeById(id)
        if node:
            # could merge the nodes and their attributes etc. ?
            # print 'Skipping', node.classname, 'already built shape...'
            return node
        t, l, w, h = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(60, 160),
            random.randint(60, 160),
        )
        node = UmlNode(id, t, l, w, h, attrs=attrs, meths=meths)
        node = self.graph.AddNode(node)
        return node

    def AddSimpleNode(self, id):
        if self.graph.FindNodeById(id):
            id += str(random.randint(1, 9999))
        t, l, w, h = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(60, 160),
            random.randint(60, 160),
        )
        node = GraphNode(id, t, l, w, h)
        node = self.graph.AddNode(node)
        return node

    def AddCommentNode(self, id, comment):
        """
        Adds a graph node of subtype CommentNode to the graph.

        Note: A graph node is not a ogl shape!

        Args:
            id: random string id, randomised by the called e.g. D1788.
                For example CmdInsertComment allocates the id, pops up
                 a dialog box editor and then calls here to create the graph node.
                If an existing node with that id exists, it is further randomised.
            comment: text

        Returns: graph node
        """
        print("incoming id", id)
        if self.graph.FindNodeById(id):
            id += str(random.randint(1, 9999))
        t, l, w, h = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(60, 160),
            random.randint(60, 160),
        )
        node = CommentNode(id, t, l, w, h, comment=comment)
        node = self.graph.AddNode(node)
        return node

    def ConvertParseModelToUmlModel(self, p):
        def BuildEdgeModel(association_tuples, edge_label):
            for fromClassname, toClassname in association_tuples:
                from_node = self.AddUmlNode(fromClassname)
                to_node = self.AddUmlNode(toClassname)
                edge = self.graph.AddEdge(from_node, to_node)
                edge["uml_edge_type"] = edge_label

        def AddGeneralisation(classname, parentclass):
            if (classname, parentclass) in self.associations_generalisation:
                # print "DUPLICATE Generalisation skipped when ConvertParseModelToUmlModel", (classname, parentclass) # DUPLICATE DETECTION
                return
            self.associations_generalisation.append((classname, parentclass))

        def AddDependency(otherclass, classname):
            if (otherclass, classname) in self.associations_composition:
                # print "DUPLICATE Dependency skipped when ConvertParseModelToUmlModel", (otherclass, classname) # DUPLICATE DETECTION
                return
            self.associations_composition.append(
                (otherclass, classname)
            )  # reverse direction so round black arrows look ok

        for classname, classentry in list(p.classlist.items()):
            """
            These are a list of (attr, otherclass) however they imply that THIS class
            owns all those other classes.
            """
            # print 'CLASS', classname, classentry

            # Composition / Dependencies
            for attr, otherclass in classentry.classdependencytuples:
                AddDependency(otherclass, classname)

            # Generalisations
            if classentry.classesinheritsfrom:
                for parentclass in classentry.classesinheritsfrom:

                    # if parentclass.find('.') <> -1:         # fix names like "unittest.TestCase" into "unittest"
                    #    parentclass = parentclass.split('.')[0] # take the lhs
                    AddGeneralisation(classname, parentclass)

            classAttrs = [attrobj.attrname for attrobj in classentry.attrs]
            classMeths = classentry.defs
            node = self.AddUmlNode(classname, classAttrs, classMeths)

        # ensure no duplicate relationships exist
        assert len(set(self.associations_composition)) == len(
            self.associations_composition
        ), self.associations_composition  # ensure no duplicates exist
        assert len(set(self.associations_generalisation)) == len(
            self.associations_generalisation
        ), self.associations_generalisation  # ensure no duplicates exist

        BuildEdgeModel(self.associations_generalisation, "generalisation")
        BuildEdgeModel(self.associations_composition, "composition")
