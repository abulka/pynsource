# graph / node abstraction
# for use by spring layout and overlap removeal

from line_intersection import FindLineIntersection
from permutations import getpermutations

class Graph:
    def __init__(self):
        self.Clear()
        
    def Clear(self):
        self.nodeSet = {}
        self.nodes = []
        self.edges = []

        self.layoutMinX = 0
        self.layoutMaxX = 0
        self.layoutMinY = 0
        self.layoutMaxY = 0
        
    def RenameNode(self, node, new_id):
        found_node = self.FindNodeById(node.id)
        assert found_node == node
        assert found_node.id == node.id

        del self.nodeSet[node.id]
        node.id = new_id
        self.nodeSet[node.id] = node

    def AddNode(self, node):
        if not self.FindNodeById(node.id):
            self.nodeSet[node.id] = node
            self.nodes.append(node)
        return node

    def AddEdge(self, source_node, target_node, weight=None):
        # Uniqueness of this edge relationship must be ensured by caller!
        #
        # Cannot add duplicate protection here, since there are call chains like:
        # LoadGraphFromStrings -> AddEdge -> NotifyOfEdgeCreateFromPersistence
        #     -> subclasses of this graph intercept NotifyOfEdgeCreateFromPersistence
        #        and add extra attributes to the edge, thus potentially making it
        #        the same or different to another existing edge.  We simply cannot
        #        tell at this point.
        
        # If node hasn't been added, then add it now
        if not self.FindNodeById(source_node.id): self.AddNode(source_node)
        if not self.FindNodeById(target_node.id): self.AddNode(target_node)
            
        edge = {'source': source_node, 'target': target_node}
        if weight:
            edge['weight'] = weight
        self.edges.append(edge)
        return edge

    def DeleteNode(self, node):
        if node:
            self.nodes.remove(node)
            if node.id in self.nodeSet.keys():
                del self.nodeSet[node.id]
        for edge in self.edges[:]:
            if edge['source'].id == node.id or edge['target'].id == node.id:
                self.edges.remove(edge)

    # Special getter which sorts nodes
    
    @property
    def nodes_sorted_by_generalisation(self):
        """
        The idea is to present the nodes in an order that is conducive to ascii
        display.  Those children nodes with the most children are prioritised
        so that they will end up along the left side of the page and thereby connected
        to the parent above with a generalisation ascii line.
        """

        def num_descendant_levels(node):
            if not node.children:
                return 0
            count = 1
            child_level_counts = []
            for n in node.children:
                child_level_counts.append( num_descendant_levels(n) )
            count += max(child_level_counts)
            return count

        def count_attrs_meths(node):
            result = 0
            if hasattr(node, 'attrs'):
                result += len(node.attrs)
            if hasattr(node, 'meths'):
                result += len(node.meths)
            return result
                
        def sort_siblings(children):
            if not children:
                return []
                
            # prioritise by num descendants so the leftmost node is part of the longest generalisation chain
            kids = sorted(children, key=lambda node: -num_descendant_levels(node))
            result = [kids[0]]
            
            # then prioritise by node height, from biggest to smallest
            if len(kids) > 1:
                result.extend( sorted(kids[1:], key=lambda node: -count_attrs_meths(node)) )

            return result
        
        def process_descendants(node, prevent_fc=False):
            result = []
            kids = sort_siblings(node.children)
            for child in kids:
                if child == kids[0]:
                    if prevent_fc:
                        annotation = "root"
                    else:
                        annotation = "fc"
                else:
                    annotation = "tab"
                    
                result.append((child, annotation))
                
            for child in kids:
                isfirst = child == kids[0]
                result.extend(process_descendants(child, prevent_fc=not isfirst))
            return result

        def setup_temporary_parent_child_relationships():
            # setup temporary parent and child relationship attributes based on generalisation
            for node in self.nodes:
                node.parents = []
                node.children = []
            for edge in self.edges:
                if edge.has_key('uml_edge_type') and edge['uml_edge_type'] == 'generalisation':
                    parent = edge['target']
                    child = edge['source']
                    if parent not in child.parents:
                        child.parents.append(parent)
                    if child not in parent.children:
                        parent.children.append(child)

        def del_temporary_parent_child_relationships():
            # remove parent / child knowledge attributes
            for node in self.nodes:
                del node.parents
                del node.children
            
        def order_the_nodes():                
            result = []
            parentless_nodes = [node for node in self.nodes if not node.parents]
            parentless_nodes = sorted(parentless_nodes[:], key=lambda node: -num_descendant_levels(node)) # put childless roots last
            for node in parentless_nodes:
                result.append((node,"root"))
                result.extend(process_descendants(node))
            return result

        assert len(set(self.nodes)) == len(self.nodes), [node.id for node in self.nodes]                                # ensure no duplicates exist
        
        setup_temporary_parent_child_relationships()
        result = order_the_nodes()
        
        assert len(result) == len(self.nodes), "Count increased! from %d to %d" %(len(self.nodes), len(result))         # ensure not introducing duplicates
        assert len(set(result)) == len(result), [node.id for node in result]                                            # ensure no duplicates exist
        
        del_temporary_parent_child_relationships()                    
        return result
    
    # These next methods take id as parameters, not nodes.
    
    def FindNodeById(self, id):
        node = self.nodeSet.get(id, None)
        return node

    def DeleteNodeById(self, id):
        node = self.FindNodeById(id)
        if node:
            self.DeleteNode(node)
        
    def RemoveDuplicatesButPreserveLineOrder(self, s):
        # remove duplicates but preserver line order.  Returns a list
        # Adapted from http://stackoverflow.com/questions/1215208/how-might-i-remove-duplicate-lines-from-a-file
        lines_seen = set() # holds lines already seen
        result = []
        for line in s.split('\n'):
            if line not in lines_seen: # not a duplicate
                result.append(line)
                lines_seen.add(line)
            else:
                #print "DUPLICATE in incoming file detected, skipped", line  # DUPLICATE DETECTION
                pass
        #print "******\n", '\n'.join(result)  # debug point - print exact replica of s but without duplicates
        return result

    # Persistence methods 

    def LoadGraphFromStrings(self, filedata_str):
        # load from persistence
        # nodes look like:     {'type':'node', 'id':'c5', 'x':230, 'y':174, 'width':60, 'height':120}
        # edges look like:     {'type':'edge', 'id':'c_to_c1', 'source':'c', 'target':'c1', 'weight':1}  weight >= 1

        for data in self.RemoveDuplicatesButPreserveLineOrder(filedata_str):
            data = data.strip()
            if not data:
                continue
            if data[0] == '#':
                continue
            #print data
            data = eval(data)
            if data['type'] == 'node':
                node = self.NotifyCreateNewNode(data['id'], data['x'], data['y'], data['width'], data['height'])
                self.AddNode(node)
                self.NotifyOfNodeCreateFromPersistence(node, data)
            elif data['type'] == 'edge':
                source_id = data['source']
                target_id = data['target']
                sourcenode = self.FindNodeById(source_id)
                targetnode = self.FindNodeById(target_id)
                if not sourcenode:
                    print "Couldn't load source from persistence", source_id
                    continue
                if not targetnode:
                    print "Couldn't load target from persistence", target_id
                    continue
                weight = data.get('weight', None)
                edge = self.AddEdge(sourcenode, targetnode, weight)  # AddEdge takes node objects as parameters
                self.NotifyOfEdgeCreateFromPersistence(edge, data)  # e.g. UmlGraph class would add edge['uml_edge_type'] if it exists in data
                
                # At this point we may have created a duplicate entry, we don't know for sure till after the UmlGraph does it's bit. So hard to detect.
                # Enable the following asserts if you suspect anything.  Bit expensive to have these on all the time.
                #
                #assert len(set(self.nodes)) == len(self.nodes), [node.id for node in self.nodes] # ensure no duplicates nodes have been created
                #assert len(set([str(e) for e in self.edges])) == len(self.edges), data # ensure no duplicates edges have been created                          

    def GraphToString(self):
        nodes = ""
        edges = ""
        for node in self.nodes:
            subclass_persistence_str = self.NotifyOfNodeBeingPersisted(node)
            str = "{'type':'node', 'id':'%s', 'x':%d, 'y':%d, 'width':%d, 'height':%d%s}\n" % (node.id, node.left, node.top, node.width, node.height, subclass_persistence_str)
            nodes += str
        for edge in self.edges:
            source = edge['source'].id
            target = edge['target'].id
            subclass_persistence_str = self.NotifyOfEdgeBeingPersisted(edge)
            str = "{'type':'edge', 'id':'%s_to_%s', 'source':'%s', 'target':'%s'%s}\n" % (source, target, source, target, subclass_persistence_str)
            edges += str
        return nodes + edges

    def NotifyCreateNewNode(self, id, l, t, w, h):
        return GraphNode(id, l, t, w, h) # subclasses to override, opportunity to create different instance type
    
    def NotifyOfNodeBeingPersisted(self, node):
        return ""  # subclasses to override, opportunity to inject additional persistence dict info

    def NotifyOfEdgeBeingPersisted(self, edge):
        return ""  # subclasses to override, opportunity to inject additional persistence dict info
    
    def NotifyOfNodeCreateFromPersistence(self, node, data):
        pass    # subclasses to override, opportunity to add attributes to node, by ref

    def NotifyOfEdgeCreateFromPersistence(self, edge, data):
        pass    # subclasses to override, opportunity to add attributes to edge, by ref
    
    def GetMementoOfLayoutPoints(self):
        memento = {}
        for node in self.nodes:
            memento[node.id] = (node.layoutPosX, node.layoutPosY)
        return memento

    def GetMementoOfPositions(self):
        memento = {}
        for node in self.nodes:
            memento[node.id] = (node.left, node.top)
        return memento

    @classmethod
    def MementosEqual(self, memento1, memento2, tolerance=5):
        for id, point in memento1.items():
            point2 = memento2.get(id, None)
            #if tolerance == 0.01:
            #    print "point %s diff %f greater than %f = %s" % (point, abs(point[0] - point2[0]), tolerance, abs(point[0] - point2[0]) > tolerance)
            if abs(point[0] - point2[0]) > tolerance or abs(point[1] - point2[1]) > tolerance:
                return False
        return True
    
    def RestoreWorldPositions(self, memento):
        for id, point in memento.items():
            node = self.FindNodeById(id)
            node.left, node.top = point

    def CountLineOverNodeCrossings(self):
        result = {}
        allcount = 0
        for node in self.nodes:
            total_crossing = []
            for edge in self.edges:
                line_start_point = edge['source'].centre_point
                line_end_point = edge['target'].centre_point
                if edge['source'] == node or edge['target'] == node:
                    continue
                crossings = node.CalcLineIntersectionPoints(line_start_point, line_end_point)
                if crossings:
                    total_crossing.extend(crossings)
            result[node.id] = len(total_crossing)
            allcount += len(total_crossing)
        result['ALL'] = allcount
        return result

    def CountLineOverLineIntersections(self, ignore_nodes=False):
        """
        Counts line crossings are counted in the world coordinate system.
        
        Parameter 'ignore_nodes' - means node height/width ignored, thus we are
        focussing on just the lines themselves. The number of LL (and LL raw -
        ignoring nodes width/height) can change as you scale up and down.

        Note: there are potentially line crossings (in world coordinates) even
        immediately after a layout. Even LL raw. Such is the nature of the
        layout->world coordinate scaling. After all the initial layout->world
        scale is to some arbitrary scale anyway - no scale is immune from
        removing LL overlaps - though... LL raw can reduce to 0 after sufficient
        scaling expansion.
        """
        
        def PointInsideANode(point):
            for node in self.nodes:
                if node.ContainsPoint(point):
                    return node
            return None
        
        def PointInCentreOfNode(point, edge1, edge2):
            return point in [edge1['source'].centre_point,  edge1['target'].centre_point,
                             edge2['source'].centre_point, edge2['target'].centre_point]
        
        result = []
        for edge1, edge2 in getpermutations(self.edges):
            line_start_point = edge1['source'].centre_point
            line_end_point = edge2['target'].centre_point
            point = FindLineIntersection(edge1['source'].centre_point, edge1['target'].centre_point,
                                         edge2['source'].centre_point, edge2['target'].centre_point)
            if point:
                point = (int(point[0]), int(point[1]))
                
                # We have a crossing
                if not ignore_nodes and PointInsideANode(point):
                    continue
                if PointInCentreOfNode(point, edge1, edge2):
                    continue
                result.append( point )
    
        # trim out duplicates
        def remove_duplicates(lzt):
            d = {}
            for x in lzt: d[tuple(x)]=x
            return d.values()
        result = remove_duplicates(result)
        return result
            
    def GetBounds(self):
        maxx = 0
        maxy = 0
        for node in self.nodes:
            maxx = max(node.left, maxx)
            maxy = max(node.top, maxy)

        return (maxx, maxy)
        
    def SaveOldPositionsForAnimationPurposes(self):
        for node in self.nodes:
            node.previous_left, node.previous_top = node.left, node.top  # for animation

    def ProposedNodeHitsWhatLines(self, proposednode, movingnode):
        """
        A node is fed a line and it will report the crossing points, if any
        """
        found_crossing_points = []
        found_edges = []
        edges = [edge for edge in self.edges if not (edge['source'] == movingnode or edge['target'] == movingnode)]
        for edge in edges:
            crossings = proposednode.CalcLineIntersectionPoints(edge['source'].centre_point, edge['target'].centre_point)
            if crossings:
                #print "%s would cross edge %s_%s crossings: %s" % (movingnode.id, edge['source'].id, edge['target'].id, crossings)
                found_crossing_points.extend(crossings)
                found_edges.append(edge)
        return found_crossing_points, found_edges
        
class GraphNode:
    def __init__(self, id, left, top, width=60, height=60):
        self.id = id
        
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        self.layoutPosX = 0
        self.layoutPosY = 0
        self.layoutForceX = 0
        self.layoutForceY = 0

        self.previous_left = left
        self.previous_top = top

    def get_bottom(self):
        return self.top + self.height

    def get_right(self):
        return self.left + self.width

    bottom = property(get_bottom)
    right = property(get_right)

    def GetBounds(self):
        return self.left, self.top, self.right, self.bottom

    def get_lines(self):
        return [((self.left, self.top), (self.right, self.top)),
                ((self.right, self.top), (self.right, self.bottom)),
                ((self.right, self.bottom), (self.left, self.bottom)),
                ((self.left, self.bottom), (self.left, self.top))]

    lines = property(get_lines)
        
    def CalcLineIntersectionPoints(self, line_start_point, line_end_point):
        result = []
        for nodeline in self.lines:
            point = FindLineIntersection(line_start_point, line_end_point, nodeline[0], nodeline[1])
            if point:
                result.append( (int(point[0]), int(point[1])) )
    
        # trim out duplicated and Nones
        def remove_duplicates(lzt):
            d = {}
            for x in lzt: d[tuple(x)]=x
            return d.values()
        result = [r for r in result if r != None]
        result = remove_duplicates(result)
        return result

    def get_centre_point(self):
        return ((self.left+self.width/2), (self.top+self.height/2))
        
    centre_point = property(get_centre_point)
    
    def ContainsPoint(self, point):
        return point[0] >= self.left and point[0] <= self.right and point[1] >= self.top and point[1] <= self.bottom
        
    def __str__(self):
        return "Node %40s: x/left,y/top (% 4d, % 4d) w,h (% 4d, % 4d) layoutPosX,layoutPosY (% 2.2f, % 2.2f)" % (self.id, self.left, self.top, self.width, self.height, self.layoutPosX, self.layoutPosY)
   

if __name__ == '__main__':

    g = Graph()
    
    n1 = GraphNode('A', 0, 0, 200, 200)
    n2 = GraphNode('B', 0, 0, 200, 200)
    g.AddEdge(n1, n2)
    
    #for node in g.nodes:
    #    print node, "layout info:", (node.layoutPosX, node.layoutPosY)

    #print g.GraphToString().strip()

    assert len(g.nodes) == 2
    assert len(g.nodeSet.keys()) == 2
    assert len(g.edges) == 1
    g.DeleteNodeById('B')
    assert len(g.nodes) == 1
    assert len(g.nodeSet.keys()) == 1
    assert len(g.edges) == 0

    filedata = """
{'type':'node', 'id':'c', 'x':230, 'y':174, 'width':60, 'height':120}
{'type':'node', 'id':'c1', 'x':130, 'y':174, 'width':60, 'height':120}
{'type':'edge', 'id':'c_to_c1', 'source':'c', 'target':'c1'}
    """
    g.Clear()
    assert len(g.nodes) == 0
    assert g.GraphToString().strip() == ""
    
    g.LoadGraphFromStrings(filedata)
    #for node in g.nodes:
    #    print node, "layout info:", (node.layoutPosX, node.layoutPosY)
    assert g.GraphToString().strip() == filedata.strip()

    # Line intersection tests
    
    res = FindLineIntersection((0,0), (200,200), (10,10), (10,50))
    assert res == [10, 10]
    
    res = FindLineIntersection((0,30), (200,30), (10,10), (10,50))
    assert res == [10, 30]
    
    node = GraphNode("A", 10, 10, 30, 40)
    assert len(node.lines) == 4
    assert (10,10) in node.lines[0]
    assert (40,10) in node.lines[0]
    assert (40,10) in node.lines[1]
    assert (40,50) in node.lines[1]
    assert (40,50) in node.lines[2]
    assert (10,50) in node.lines[2]
    assert (10,50) in node.lines[3]
    assert (10,10) in node.lines[3]
    
    res = node.CalcLineIntersectionPoints((0, 0), (200, 200))
    assert len(res) == 2
    assert (10, 10) in res
    assert (40, 40) in res
    
    res = node.CalcLineIntersectionPoints((20, 0), (20, 1000))
    assert len(res) == 2
    assert (20, 10) in res
    assert (20, 50) in res
    
    
    """
    TESTS re generalisation sort order
    """
    
    # C --|> B --|> A
    g = Graph()
    c = GraphNode('C', 0, 0, 200, 200)
    b = GraphNode('B', 0, 0, 200, 200) # parent of C
    a = GraphNode('A', 0, 0, 200, 200) # parent of B
    # add out of order
    g.AddNode(b)
    g.AddNode(c)
    g.AddNode(a)
    g.AddEdge(c, b)['uml_edge_type'] = 'generalisation'
    g.AddEdge(b, a)['uml_edge_type'] = 'generalisation'
    nodelist_normal = [node.id for node in g.nodes]
    nodelist_sorted = [node.id for node,annotation in g.nodes_sorted_by_generalisation]
    nodelist_sorted_expected = ['A', 'B', 'C']
    #print "nodelist_normal", nodelist_normal
    #print "nodelist_sorted_expected", nodelist_sorted_expected
    #print "nodelist_sorted", nodelist_sorted
    assert nodelist_sorted_expected == nodelist_sorted

    # D --|> C --|> B --|> A
    d = GraphNode('D', 0, 0, 200, 200)
    g.AddNode(d)
    g.AddEdge(d, c)['uml_edge_type'] = 'generalisation'
    nodelist_sorted = [node.id for node,annotation in g.nodes_sorted_by_generalisation]
    nodelist_sorted_expected = ['A', 'B', 'C', 'D']
    assert nodelist_sorted_expected == nodelist_sorted

    # E node not connected to anything
    e = GraphNode('E', 0, 0, 200, 200)
    g.AddNode(e)
    nodelist_sorted = [node.id for node,annotation in g.nodes_sorted_by_generalisation]
    nodelist_sorted_expected = ['A', 'B', 'C', 'D', 'E']
    assert nodelist_sorted_expected == nodelist_sorted

    # D --|> C --|> B --|> A
    # E
    # C2 --|> B
    c2 = GraphNode('C2', 0, 0, 200, 200)
    g.AddNode(c2)
    g.AddEdge(c2, b)['uml_edge_type'] = 'generalisation'
    nodelist_sorted = [node.id for node,annotation in g.nodes_sorted_by_generalisation]
    nodelist_sorted_expected = ['A', 'B', 'C', 'C2', 'D', 'E']
    assert nodelist_sorted_expected == nodelist_sorted

    # START AGAIN - more tests, ensure children nodes with children themselves, are prioritised
    
    # C2,C --|> B
    # B,B2 --|> A
    g = Graph()
    c = GraphNode('C', 0, 0, 200, 200)
    c2 = GraphNode('C2', 0, 0, 200, 200)
    b = GraphNode('B', 0, 0, 200, 200)
    b2 = GraphNode('B2', 0, 0, 200, 200)
    a = GraphNode('A', 0, 0, 200, 200)
    # add out of order
    g.AddNode(b2)
    g.AddNode(b)
    g.AddNode(c)
    g.AddNode(c2)
    g.AddNode(a)
    g.AddEdge(c, b)['uml_edge_type'] = 'generalisation'
    g.AddEdge(c2, b)['uml_edge_type'] = 'generalisation'
    g.AddEdge(b2, a)['uml_edge_type'] = 'generalisation'
    g.AddEdge(b, a)['uml_edge_type'] = 'generalisation'
    nodelist_normal = [node.id for node in g.nodes]
    nodelist_sorted = [node.id for node,annotation in g.nodes_sorted_by_generalisation]
    nodelist_sorted_expected = ['A', 'B', 'B2', 'C', 'C2']
    nodelist_sorted_expected2 = ['A', 'B', 'B2', 'C2', 'C']
    #print "nodelist_normal", nodelist_normal
    #print "nodelist_sorted_expected", nodelist_sorted_expected
    #print "nodelist_sorted", nodelist_sorted
    assert nodelist_sorted_expected == nodelist_sorted or \
            nodelist_sorted_expected2 == nodelist_sorted

    # START AGAIN - more tests, ensure children nodes with children themselves, are prioritised
    # and furthermore, children with the most descendants are prioritised even more.
    
    # B,B1 --|> A
    # C --|> B
    g = Graph()
    c = GraphNode('C', 0, 0, 200, 200)
    b = GraphNode('B', 0, 0, 200, 200)
    b1 = GraphNode('B1', 0, 0, 200, 200)
    a = GraphNode('A', 0, 0, 200, 200)
    c2 = GraphNode('C2', 0, 0, 200, 200)
    d = GraphNode('D', 0, 0, 200, 200)
    # add out of order
    g.AddNode(b1)
    g.AddNode(b)
    g.AddNode(a)
    g.AddNode(c)
    g.AddNode(c2)
    g.AddNode(d)
    g.AddEdge(c2, b1)['uml_edge_type'] = 'generalisation'
    g.AddEdge(d, c)['uml_edge_type'] = 'generalisation'
    g.AddEdge(c, b)['uml_edge_type'] = 'generalisation'
    g.AddEdge(b1, a)['uml_edge_type'] = 'generalisation'
    g.AddEdge(b, a)['uml_edge_type'] = 'generalisation'
    nodelist_normal = [node.id for node in g.nodes]
    nodelist_sorted = [node.id for node,annotation in g.nodes_sorted_by_generalisation]
    nodelist_sorted_expected = ['A', 'B', 'B1', 'C', 'D', 'C2']
    #print "nodelist_normal", nodelist_normal
    #print "nodelist_sorted_expected", nodelist_sorted_expected
    #print "nodelist_sorted", nodelist_sorted
    assert nodelist_sorted_expected == nodelist_sorted

    # START AGAIN - more tests, check stranger trees, though the algorithm
    # is proving pretty smart, prioritising children who have children to the left

    # B,B1,C,K --|> A
    # D --|> C
    g = Graph()
    a = GraphNode('A', 0, 0, 200, 200)
    b = GraphNode('B', 0, 0, 200, 200)
    b1 = GraphNode('B1', 0, 0, 200, 200)
    c = GraphNode('C', 0, 0, 200, 200)
    k = GraphNode('K', 0, 0, 200, 200)
    d = GraphNode('D', 0, 0, 200, 200)
    # add out of order
    g.AddNode(b1)
    g.AddNode(b)
    g.AddNode(a)
    g.AddNode(c)
    g.AddNode(k)
    g.AddNode(d)
    g.AddEdge(k, a)['uml_edge_type'] = 'generalisation'
    g.AddEdge(d, c)['uml_edge_type'] = 'generalisation'
    g.AddEdge(c, a)['uml_edge_type'] = 'generalisation'
    g.AddEdge(b1, a)['uml_edge_type'] = 'generalisation'
    g.AddEdge(b, a)['uml_edge_type'] = 'generalisation'
    nodelist_normal = [node.id for node in g.nodes]
    nodelist_sorted = [node.id for node,annotation in g.nodes_sorted_by_generalisation]
    #print "nodelist_normal", nodelist_normal
    #print "nodelist_sorted_expected", nodelist_sorted_expected
    #print "nodelist_sorted", nodelist_sorted
    assert nodelist_sorted[0] == 'A'
    assert nodelist_sorted[1] == 'C'
    assert nodelist_sorted[-1] == 'D'

    nodelist_sorted_annotated = [(node.id, annotation) for node,annotation in g.nodes_sorted_by_generalisation]
    assert nodelist_sorted_annotated[0] == ('A', 'root')
    assert nodelist_sorted_annotated[1] == ('C', 'fc')
    assert nodelist_sorted_annotated[-1] == ('D', 'fc')
    assert ('K', 'tab') in nodelist_sorted_annotated
    assert ('B', 'tab') in nodelist_sorted_annotated
    assert ('B1', 'tab') in nodelist_sorted_annotated
    
    # START AGAIN - more tests, check stranger trees

    # B,D,F --|> A
    # G --|> C --|> B
    # E --|> D
    g = Graph()
    a = GraphNode('A', 0, 0, 200, 200)
    b = GraphNode('B', 0, 0, 200, 200)
    c = GraphNode('C', 0, 0, 200, 200)
    d = GraphNode('D', 0, 0, 200, 200)
    e = GraphNode('E', 0, 0, 200, 200)
    f = GraphNode('F', 0, 0, 200, 200)
    h = GraphNode('H', 0, 0, 200, 200)
    # add out of order
    g.AddNode(f)
    g.AddNode(b)
    g.AddNode(a)
    g.AddNode(h)
    g.AddNode(c)
    g.AddNode(e)
    g.AddNode(d)
    g.AddEdge(b, a)['uml_edge_type'] = 'generalisation'
    g.AddEdge(d, a)['uml_edge_type'] = 'generalisation'
    g.AddEdge(f, a)['uml_edge_type'] = 'generalisation'
    g.AddEdge(h, c)['uml_edge_type'] = 'generalisation'
    g.AddEdge(c, b)['uml_edge_type'] = 'generalisation'
    g.AddEdge(e, d)['uml_edge_type'] = 'generalisation'
    nodelist_normal = [node.id for node in g.nodes]

    nodelist_sorted = [node.id for node,annotation in g.nodes_sorted_by_generalisation]
    nodelist_sorted_expected = ['A', 'B', 'D', 'F', 'C', 'H', 'E']
    assert nodelist_sorted_expected == nodelist_sorted

    nodelist_sorted_annotated = [(node.id, annotation) for node,annotation in g.nodes_sorted_by_generalisation]
    nodelist_sorted_expected_annotated = [('A', 'root'), ('B', 'fc'), ('D', 'tab'), ('F', 'tab'), ('C', 'fc'), ('H', 'fc'), ('E', 'root')]
    assert nodelist_sorted_expected_annotated == nodelist_sorted_annotated

    #print "nodelist_normal", nodelist_normal
    #print "nodelist_sorted_expected", nodelist_sorted_expected
    #print "nodelist_sorted", nodelist_sorted

    
    print "Done, tests passed"
