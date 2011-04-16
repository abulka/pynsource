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
        
    def AddNode(self, node):
        if not self.FindNodeById(node.id):
            self.nodeSet[node.id] = node
            self.nodes.append(node)
        return node

    def AddEdge(self, source_node, target_node, weight=None):
        # Uniqueness of this edge relationship must be ensured by caller
        
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

    # These next methods take id as parameters, not nodes.
    
    def FindNodeById(self, id):
        node = self.nodeSet.get(id, None)
        return node

    def DeleteNodeById(self, id):
        node = self.FindNodeById(id)
        if node:
            self.DeleteNode(node)
        
    # Persistence methods 

    def LoadGraphFromStrings(self, filedata):
        # load from persistence
        # nodes look like:     {'type':'node', 'id':'c5', 'x':230, 'y':174, 'width':60, 'height':120}
        # edges look like:     {'type':'edge', 'id':'c_to_c1', 'source':'c', 'target':'c1', 'weight':1}  weight >= 1
        
        filedata = filedata.split('\n')
        for data in filedata:
            data = data.strip()
            if not data:
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
                self.NotifyOfEdgeCreateFromPersistence(edge, data)

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
        return "Node %s: x,y (%d, %d) w,h (%d, %d)" % (self.id, self.left, self.top, self.width, self.height)
   

if __name__ == '__main__':

    g = Graph()
    
    n1 = GraphNode('A', 0, 0, 200, 200)
    n2 = GraphNode('B', 0, 0, 200, 200)
    g.AddEdge(n1, n2)
    
    for node in g.nodes:
        print node, "layout info:", (node.layoutPosX, node.layoutPosY)

    print g.GraphToString().strip()

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
    for node in g.nodes:
        print node, "layout info:", (node.layoutPosX, node.layoutPosY)
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
    
    print "Done, tests passed"
