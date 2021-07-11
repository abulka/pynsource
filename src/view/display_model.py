import random
import sys
from .graph import Graph, GraphNode
from base64 import b64encode
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
from base64 import b64decode
from beautifultable import BeautifulTable
from termcolor import colored  # also install colorama to make this work on windows
from gui.coord_utils import getpos


class UmlGraph(Graph):
    def create_new_node(self, id, l, t, w, h):
        # subclasses overriding, opportunity to create different instance type
        return UmlNode(id, l, t, w, h)

    def create_new_comment(self, id, l, t, w, h):
        # subclasses overriding, opportunity to create different instance type
        return CommentNode(id, l, t, w, h)

    def _repr_flat(self, data: Dict) -> str:
        """
        Convert dictionary into a flat single string of k:v, k:v
        with each key and value single quoted.

        Args:
            data: dict

        Returns: string
        """
        result = ""
        for k, v in data.items():
            result += f", '{k}': '{v}'"
        return result

    def node_to_persistence_str(self, node) -> Tuple[str, str]:
        """subclasses to override, opportunity to inject additional persistence dict info
        first string is a type, second string is the node representation as flat single str
        """
        if type(node) == CommentNode:
            _type = "comment"
            # encode comment as bas64 but decode it into str so that it doesn't get saved as b'..'r
            data = {"comment": f"{str(b64encode(node.comment.encode('utf-8')).decode('utf-8'))}"}
        else:
            _type = "umlshape"
            data = {"attrs": "|".join(node.attrs), "meths": "|".join(node.meths)}
        return _type, self._repr_flat(data)

    def edge_to_persistence_str(self, edge) -> Tuple[str, str]:
        """subclasses to override, opportunity to inject additional persistence dict info
        first string is a type, second string is the node representation as flat single str

        No need to specify 'source' and 'target' as this is done by the graph persistence save
        along with the id, left, top etc.
        """
        data = {"uml_edge_type": edge["uml_edge_type"]}
        return "edge", self._repr_flat(data)

    def node_from_persistence_str(self, node, data):
        # subclass overriding, opportunity to add attributes to node
        if data.get("attrs", ""):
            node.attrs = data["attrs"].split("|")
        if data.get("meths", ""):
            node.meths = data["meths"].split("|")
        if data.get("comment", ""):
            comment = data["comment"]
            node.comment = b64decode(comment).decode("utf-8")

    def edge_from_persistence_str(self, edge, data):
        # subclass overriding, opportunity to add attributes to edge
        if data.get("uml_edge_type", ""):
            edge["uml_edge_type"] = data["uml_edge_type"]


class UmlNode(GraphNode):
    def __init__(self, id, left, top, width=60, height=60, attrs=[], meths=[]):
        GraphNode.__init__(self, id, left, top, width=width, height=height)
        self.attrs = attrs
        self.meths = meths
        self.shape = None

    def get_id(self):
        return self.id

    def set_id(self, val):
        self.id = val

    classname = property(get_id, set_id)


class UmlModuleNode(GraphNode):
    def __init__(self, id, left, top, width=60, height=60, attrs=[], meths=[]):
        GraphNode.__init__(self, id, left, top, width=width, height=height)
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
        GraphNode.__init__(self, id, left, top, width, height)
        self.comment = comment
        self.shape = None

    def get_id(self):
        return self.id

    def set_id(self, val):
        self.id = val

    classname = property(get_id, set_id)


class DisplayModel:
    """
    The Display Model is the graph of abstract nodes and edges, which can be laid out in space.
    Use build_graph( parsemodel ) to build it.

    Then call build_view() to attaches various Shapes to the nodes and edges
    which relies on calls into umlcanvas to create these OGL visual shapes.

    These calls into umlcanvas are limited to:

        self.canvas.delete_shape_view(node.shape)
            which in turn relies on canvas.app.run.CmdDeselectAllShapes()

        shape = self.canvas.createCommentShape(node)

        shape = self.canvas.CreateUmlShape(node)

        self.canvas.CreateUmlEdge(edge)

    Summary:

        context.displaymodel - this class, which points to a single Graph of nodes and edges.
        context.umlcanvas - an ogl scrolled window with visual shape functionality

        The 'graph' of 'nodes' is the abstract stuff, used in layout, but also containing
        the method, attributes, comment info.  After calling build_view(), each node points
        to a visual shape, and vice versa.

    """

    def __init__(self, canvas=None):
        self.graph = UmlGraph()
        self.umlcanvas = canvas
        self.pmodels_i_have_seen = []  # just for reference and dumping purposes
        self.alsms_i_have_seen = []  # just for reference and dumping purposes
        self.Clear()

    def Clear(self):
        self.graph.Clear()
        self.pmodels_i_have_seen = []
        self.alsms_i_have_seen = []

    def build_graphmodel(self, pmodel):
        """
        Build the graph with node and edges, from the pmodel (parse model)
        Shapes are added later by the build_view()

        Algorithm
        ---------
        Loops through each class in the pmodel.
        Note: Comments do not exist in the pmodel.

        1. First we create tuple entries in
            compositions
            generalisations
        2. Then we for each class, create
            self.AddUmlNode with its attrs and methods
        3. Lastly we create the edges by calling build_edges(), which goes through
            each association that we created in step 1 and attempts to create the uml node
            on either end. It uses AddUmlNode().  Most probably the node already exists
            and will not be created twice. AddUmlNode is smart - it even now merges attrs/meths.
            Then of course we create the edge using AddUmlEdge() which attempts new
            duplicate protection.

        Note AddUmlNode, AddUmlEdge are methods on the umlcanvas.
        """
        self.pmodels_i_have_seen.append(pmodel)

        generalisations = []
        compositions = []
        associations = []  # are no pure associations in a pmodel, but mention for completeness

        def build_edges(association_tuples, edge_type):
            for fromClassname, toClassname in set(association_tuples):  # avoid duplicates
                from_node = self.AddUmlNode(fromClassname)
                to_node = self.AddUmlNode(toClassname)
                edge = self.AddUmlEdge(
                    from_node, to_node, edge_type
                )  # incl. duplicate protection in here

        def AddGeneralisation(classname, parentclass):
            # if (classname, parentclass) in generalisations:
            #     return
            generalisations.append((classname, parentclass))

        def AddDependency(otherclass, classname):
            # if (otherclass, classname) in compositions:
            #     return
            compositions.append((otherclass, classname))  # reverse so arrows look correct

        # MAIN ALGORITHM BEGINS HERE

        for classname, classentry in list(pmodel.classlist.items()):

            for attr, otherclass in classentry.classdependencytuples:
                AddDependency(otherclass, classname)

            if classentry.classesinheritsfrom:
                for parentclass in classentry.classesinheritsfrom:
                    AddGeneralisation(classname, parentclass)

            classAttrs = sorted([attrobj.attrname for attrobj in classentry.attrs])  # type Attribute class
            classMeths = sorted(classentry.defs)
            node = self.AddUmlNode(classname, classAttrs, classMeths)

        # ensure no duplicate relationships exist
        # assert len(set(compositions)) == len(compositions)
        # assert len(set(generalisations)) == len(generalisations)

        # Will build edges, but also will build any UmlClass nodes referred to if they don't already
        # exist. Note there are no pure 'associations' in a pmodel, but mention for completeness.
        build_edges(generalisations, "generalisation")
        build_edges(compositions, "composition")
        # build_edges(associations, "associations")


    def build_graphmodel_from_alsm(self, alsm, options=None):
        """
        Build the graph with node and edges, from the ALSM (parse model)
        Shapes are added later by the build_view()
        """
        if not options:
            options = {}
        self.alsms_i_have_seen.append(alsm)

        generalisations: List[Tuple[str, str]] = []
        compositions: List[Tuple[str, str]] = []
        associations: List[Tuple[str, str]] = []
        
        def build_edges(associations: Tuple[str, str], edge_type):
            for from_class_name, to_class_name in set(associations):  # avoid duplicates
                from_node = self.AddUmlNode(from_class_name)
                to_node = self.AddUmlNode(to_class_name)
                edge = self.AddUmlEdge(
                    from_node, to_node, edge_type
                )  # incl. duplicate protection in here

        def add_generalisation(class_name, parent_class):
            generalisations.append((class_name, parent_class))

        def add_composition_dependency(other_class, class_name):
            compositions.append((other_class, class_name))  # reverse so arrows look correct

        def add_module_dependency(other_class, class_name):
            associations.append((other_class, class_name))

        # MAIN ALGORITHM BEGINS HERE

        for class_name, class_entry in list(alsm.classes.items()):

            for attr, other_class in class_entry.class_dependency_tuples:
                add_composition_dependency(other_class, class_name)

            if class_entry.classes_inherits_from:
                for parent_class in class_entry.classes_inherits_from:
                    add_generalisation(class_name, parent_class)

            class_attributes = sorted([attrobj.attr_name for attrobj in class_entry.attributes])  # type Attribute class
            class_methods = sorted(class_entry.methods)
            node = self.AddUmlNode(class_name, class_attributes, class_methods)
        
        # create a psuedo module class
        if options.get("visualise_modules", True):
            module_variables = [attrobj.attr_name for attrobj in sorted(alsm.variables, key=lambda attrobj: attrobj.attr_name)]
            module_functions = [adef for adef in sorted(alsm.functions)]
            node = self.AddUmlModuleNode(alsm.name, module_variables, module_functions)
            # module points to each class inside it
            for aclass in alsm.classes.keys():
                add_module_dependency(aclass, alsm.name)
            # module dependencies
            for module_class_dependency in alsm.module_dependencies:
                if isinstance(module_class_dependency, tuple):
                    from_var, to_class = module_class_dependency
                else:
                    from_var = 'uses'
                    to_class = module_class_dependency
                node = self.AddUmlNode(to_class)  # create it just in case its not there - will auto merge
                add_composition_dependency(to_class, alsm.name)  # 'from_var' should be a label on the edge

        build_edges(generalisations, "generalisation")
        build_edges(compositions, "composition")
        build_edges(associations, "association")


    def build_view(self, translatecoords=True, purge_existing_shapes=False):
        """
        Builds the shapes from the display model, attaching shapes to nodes
        and in the case of edge shapes, attaching them to the relevant graph edge dictionary entry.

        This is an important method.

        translatecoords - sets node positions to shape positions, translating coordinate systems.
            Can't remember why I added this. All uses of this methods call it with this
            parameter False. TODO remove this param?
            This is the culprit which keeps resetting the node positions after import!!

        Updates existing shapes by default, with option to zap all shapes (which used to be
                                                                            the default behaviour)

        Returns: -
        """

        if translatecoords:
            self.umlcanvas.AllToWorldCoords()

        # Clear existing visualisation, including any attached edges/lines
        if purge_existing_shapes:
            for node in self.graph.nodes:
                if node.shape:
                    self.umlcanvas.delete_shape_view(node.shape)
                    node.shape = None
            for edge in self.graph.edges:
                if edge.get("shape", None):
                    self.umlcanvas.delete_shape_view(edge["shape"])
                    edge["shape"] = None

        # Create fresh visualisation (or update existing)
        for node in self.graph.nodes:
            if isinstance(node, CommentNode) or hasattr(node, "comment"):
                # Comment shape
                if node.shape:
                    node.shape.ClearText()
                    node.shape.AddText(node.comment)
                else:
                    self.umlcanvas.createCommentShape(node)
            else:
                # UML class shape
                if node.shape:
                    node.shape.ClearRegions()
                    oldx, oldy = node.shape._xpos, node.shape._ypos
                    if isinstance(node, UmlModuleNode):
                        self.umlcanvas.CreateUmlModuleShape(node, update_existing_shape=node.shape)
                    else:
                        self.umlcanvas.CreateUmlShape(node, update_existing_shape=node.shape)
                    if node.shape._xpos != oldx or node.shape._ypos != oldy:
                        print(
                            f"Warning build_view(): reusing existing shape messed with coords {node.id} was {oldx}, {oldy} now {node.shape._xpos}, {node.shape._xpos}"
                        )
                else:
                    if isinstance(node, UmlModuleNode):
                        self.umlcanvas.CreateUmlModuleShape(node)
                    else:
                        self.umlcanvas.CreateUmlShape(node)

        for edge in self.graph.edges:
            if not edge.get("shape", None):
                self.umlcanvas.CreateUmlEdgeShape(edge)

    def AddUmlNode(self, id, attrs=[], meths=[]):
        node = self.graph.FindNodeById(id)
        if node:
            # could merge the nodes and their attributes etc. ?
            # print 'Skipping', node.classname, 'already built shape...'
            self.merge_attrs_and_meths(node, attrs, meths)
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

    def AddUmlModuleNode(self, id, attrs=[], meths=[]):
        node = self.graph.FindNodeById(id)
        if node:
            # could merge the nodes and their attributes etc. ?
            # print 'Skipping', node.classname, 'already built shape...'
            self.merge_attrs_and_meths(node, attrs, meths)
            return node
        t, l, w, h = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(60, 160),
            random.randint(60, 160),
        )
        node = UmlModuleNode(id, t, l, w, h, attrs=attrs, meths=meths)
        node = self.graph.AddNode(node)
        return node

    def AddCommentNode(self, id, comment):
        """
        Adds a graph node of subtype CommentNode to the graph.

        Note: A graph node is not a ogl shape!

        Position is random.  Size is set to reasonable defaults.  This method
        only gets called by the UI creation of comments.  When loading from
        persistence, GraphPersistence.Load and UmlGraph.create_new_comment
        do the same work and respect the size of the node coming from disk
        thus no randomisation or default size setting then.

        Args:
            id: random string id, randomised by the called e.g. D1788.
                For example CmdInsertComment allocates the id, pops up
                 a dialog box editor and then calls here to create the graph node.
                If an existing node with that id exists, it is further randomised.
            comment: text

        Returns: graph node
        """
        if self.graph.FindNodeById(id):
            id += str(random.randint(1, 9999))
        t, l, w, h = (
            random.randint(0, 100),
            random.randint(0, 100),
            200,  # random.randint(60, 160),
            100,  # random.randint(60, 160),
        )
        node = CommentNode(id, t, l, w, h, comment=comment)
        node = self.graph.AddNode(node)
        return node

    def AddUmlEdge(self, from_node, to_node, edge_type):  # NEW - to stop duplicates
        """
        Add edge but prevent creating another edge of type 'edge_type'
        of the set
            'generalisation', 'composition'
        that already exists between the two nodes.
        Interesting, we don't create the edge object here, but call into Graph()
        to do it.  Presumably because edges are dicts and a bit private, though we do
        add to the dict here. Hmm. Another reason is that Graph.AddEdge() auto creates nodes
        if they don't exist.  Attempts at duplicate protection inside Graph.AddEdge()
        were abandoned (see explanation there) but we are retrying here!  Good luck!.
        Update: duplicate edge protection seems to be working ok.

        Returns: -
        """
        edge = self.graph.FindEdge(from_node, to_node, edge_type)
        if edge:
            # print('Duplicate edge detected', edge, 'already exists...', "DUPLICATE_PROTECTION is", DUPLICATE_PROTECTION)
            return
        edge = self.graph.AddEdge(from_node, to_node)
        edge["uml_edge_type"] = edge_type

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

    def Dump(self, msg=""):

        # Utility

        def node_name(node: GraphNode):
            name: str = node.id
            if hasattr(node, "comment"):  # colourise_comments
                name = colored(name, "yellow")
            return name

        def edgetype_colourise(edgetype: str):
            # 'grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white',
            if edgetype == "association":
                edgetype = colored(edgetype, "blue")
            if edgetype == "generalisation":
                edgetype = colored(edgetype, "green")
            if edgetype == "composition":
                edgetype = colored(edgetype, "cyan")
            return edgetype

        # Main

        if msg:
            print(msg)  # Extra explanatory info to give context re when the dump is being made

        t = BeautifulTable(maxwidth=260)
        t.set_style(BeautifulTable.STYLE_BOX)  # nice ─── chars
        t.columns.header = ["node", "coords", "widths", "shape"]
        for node in self.graph.nodes:
            name = node_name(node)
            t.rows.append(
                [
                    name,
                    (node.left, node.top),
                    (node.width, node.height),
                    f"{node.shape} {self.obj_id(node.shape)} {self.get_shape_pos(node.shape)}",
                ]
            )
        t.columns.alignment["node"] = BeautifulTable.ALIGN_LEFT
        print(t)

        e = BeautifulTable(maxwidth=340)
        e.set_style(BeautifulTable.STYLE_GRID)  # nice ─── chars
        e.columns.header = ["edge", "from", "symbol", "to", "shape"]
        e.columns.alignment["shape"] = BeautifulTable.ALIGN_LEFT
        e.columns.alignment["from"] = BeautifulTable.ALIGN_LEFT
        e.columns.alignment["to"] = BeautifulTable.ALIGN_LEFT
        for edge in self.graph.edges:
            source = node_name(edge["source"])
            target = node_name(edge["target"])
            edgetype = edgetype_colourise(edge["uml_edge_type"])
            symbol = self.edgetype_symbol(edge["uml_edge_type"])
            if edgetype == "composition":
                source, target = target, source  # around the wrong way? - fix
            shape = edge.get("shape", None)
            e.rows.append(
                [
                    edgetype,
                    source,
                    symbol,
                    target,
                    f"{type(shape).__name__} {self.obj_id(shape)} {self.get_shape_pos(shape)} {self.get_line_shape_innards(shape)}",
                ]
            )
        print(e)

    def delete_node_or_edge_for_shape(self, shape):
        if "Line" in shape.GetShape().__class__.__name__:
            # Delete the edge from the graph model
            edge: Dict = self.graph.find_edge_for_lineshape(shape)
            self.graph.delete_edge(edge)
        else:
            self.graph.DeleteNodeById(shape.node.id)

    def merge_attrs_and_meths(self, node, attrs, meths):
        """
        adds new attrs and meths into existing node, avoiding duplicates
        """
        node.attrs = sorted(list(set(attrs + node.attrs)))
        node.meths = sorted(list(set(meths + node.meths)))

    def obj_id(self, obj) -> str:
        # as hex, just the last few digits of the id, to reduce noise.  None protection.
        return f"{id(obj):x}"[-3:] if obj else ""

    def get_shape_pos(self, shape) -> str:
        # as hex, just the last few digits of the id, to reduce noise.  None protection.
        if shape:
            x, y = getpos(shape)
            width, height = shape.GetBoundingBoxMax()  # wx.ogl doesn't have shape._width etc. so derive
            return f"({int(x):3},{int(y):3}) size: {width:3.0f}, {height:3.0f}"
            # return f"({int(x)},{int(y)}) size: {shape._width}, {shape._height} {shape._lineControlPoints}"
        else:
            return ""

    def edgetype_symbol(self, edgetype: str):
        if edgetype == "generalisation":
            symbol = "--|>"
        elif edgetype == "composition":
            symbol = "--->"
        else:
            symbol = "---"
        return symbol

    def get_line_shape_innards(self, shape) -> str:
        # as hex, just the last few digits of the id, to reduce noise.  None protection.
        if shape and hasattr(shape, "_lineControlPoints"):
            points = ["(%3.0f, %3.0f)" % (real_p.Get()[0], real_p.Get()[1]) for real_p in shape._lineControlPoints]
            return f"from: {shape._attachmentFrom} to: {shape._attachmentTo} _lcp: {' '.join(points)}"
        else:
            return ""

