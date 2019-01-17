import random
import sys
from .graph import Graph, GraphNode
from base64 import b64encode
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
from base64 import b64decode
from beautifultable import BeautifulTable
from termcolor import colored  # also install colorama to make this work on windows

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
        self.Clear()

    def Clear(self):
        self.graph.Clear()

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

            classAttrs = [attrobj.attrname for attrobj in classentry.attrs]  # type Attribute class
            classMeths = classentry.defs
            node = self.AddUmlNode(classname, classAttrs, classMeths)

        # ensure no duplicate relationships exist
        # assert len(set(compositions)) == len(compositions)
        # assert len(set(generalisations)) == len(generalisations)

        # Will build edges, but also will build any UmlClass nodes referred to if they don't already
        # exist. Note there are no pure 'associations' in a pmodel, but mention for completeness.
        build_edges(generalisations, "generalisation")
        build_edges(compositions, "composition")
        # build_edges(associations, "associations")

    def build_view(self, translatecoords=True):
        """
        Builds the shapes from the display model, attaching shapes to nodes
        and in the case of edge shapes, attaching them to the relevant graph edge dictionary entry

        This is an important method.

        Called by
            CmdFileLoadWorkspaceBase.load_model_from_text_and_build_shapes()

            CmdFileImportBase - and its subclasses
                class CmdFileImportFromFilePath(CmdFileImportBase):  # was class CmdFileImportSource(CmdBase):
                class CmdFileImportViaDialog(CmdFileImportBase):  # was class CmdFileImport(CmdBase):

            CmdBuildColourChartWorkspace

        This used to live in Umlcanvas.

        Args:
            translatecoords: ?

        Returns:
        """
        if translatecoords:
            self.umlcanvas.AllToWorldCoords()

        # Clear existing visualisation, including any attached edges/lines
        for node in self.graph.nodes:
            if node.shape:
                self.umlcanvas.delete_shape_view(node.shape)
                node.shape = None

        # Create fresh visualisation
        for node in self.graph.nodes:
            assert not node.shape
            if isinstance(node, CommentNode) or hasattr(node, "comment"):
                shape = self.umlcanvas.createCommentShape(node)
            else:
                shape = self.umlcanvas.CreateUmlShape(node)
            # self.displaymodel.classnametoshape[
            #     node.id
            # ] = shape  # Record the name to shape map so that we can wire up the links later.

        for edge in self.graph.edges:
            self.umlcanvas.CreateUmlEdge(edge)

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
        print("incoming id", id)
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

    def Dump(self):

        # Utility

        def node_name(node: GraphNode):
            name: str = node.id
            if hasattr(node, "comment"):  # colourise_comments
                name = colored(name, "yellow")
            return name

        def edge_name_colourise(edgetype: str):
            # 'grey',
            # 'red',
            # 'green',
            # 'yellow',
            # 'blue',
            # 'magenta',
            # 'cyan',
            # 'white',
            if edgetype == "association":
                edgetype = colored(edgetype, "blue")
            if edgetype == "generalisation":
                edgetype = colored(edgetype, "green")
            if edgetype == "composition":
                edgetype = colored(edgetype, "cyan")
            return edgetype

        # Main

        t = BeautifulTable()
        t.column_headers = ["node", "coords", "widths", "shape"]
        for node in self.graph.nodes:
            name = node_name(node)
            t.append_row([name, (node.left, node.top), (node.width, node.height), node.shape])
        t.column_alignments['node'] = BeautifulTable.ALIGN_LEFT
        t.row_separator_char = ''
        print(t)

        e = BeautifulTable(max_width=240)
        e.column_headers = ["edge", "from", "symbol", "to", "shape"]
        e.column_alignments['shape'] = BeautifulTable.ALIGN_LEFT
        for edge in self.graph.edges:
            source = node_name(edge["source"])
            target = node_name(edge["target"])
            edgetype = edge_name_colourise(edge["uml_edge_type"])
            shape = edge.get("shape", None)
            if edgetype == "generalisation":
                symbol = "--|>"
            elif edgetype == "composition":
                source, target = target, source  # around the wrong way? - fix
                symbol = "--->"
            else:
                symbol = "---"
            e.append_row([edgetype, source, symbol, target, shape])
        e.row_separator_char = ''
        print(e)

    def Dump_plain_old(self):
        def line(ch="-"):
            return ch * 70

        print()
        print("     DisplayModel (Graph)   ")
        print()

        # The nodeSet is just a dictionary of unique nodes, good info but not generally
        # needing to be dumped.
        #
        # print(line("-"), "graph.nodeSet is")
        # pprint(list(self.graph.nodeSet.keys()))

        print(line("-"), "self.graph.nodes")
        print()
        for node in self.graph.nodes:
            print(node)
        print(line("-"), "self.graph.edges")
        for edge in self.graph.edges:
            source = edge["source"].id
            target = edge["target"].id
            edgetype = edge["uml_edge_type"]
            shape = edge.get("shape", None)
            if edgetype == "generalisation":
                symbol = "--|>"
            elif edgetype == "composition":
                source, target = target, source  # around the wrong way? - fix
                symbol = "--->"
            else:
                symbol = "---"
            print("from %40s %s %-40s  (%s)  shape=%s" % (source, symbol, target, edgetype, shape))

    def decouple_node_from_shape(self, shape):
        pass

    def delete_node_for_shape(self, shape):
        # self.decouple_node_from_shape(shape)

        self.graph.DeleteNodeById(shape.node.id)
        print("deleted node shape.node.id", shape.node.id)

    def merge_attrs_and_meths(self, node, attrs, meths):
        """
        adds new attrs and meths into existing node, avoiding duplicates
        """
        node.attrs = list(set(attrs + node.attrs))
        node.meths = list(set(meths + node.meths))

