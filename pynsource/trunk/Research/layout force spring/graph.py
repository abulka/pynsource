# graph / node abstraction
# for use by spring layout and overlap removeal

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
                node = GraphNode(data['id'], data['x'], data['y'], data['width'], data['height'])
                self.AddNode(node)
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
                self.AddEdge(sourcenode, targetnode, weight)  # AddEdge takes node objects as parameters

    def GraphToString(self):
        nodes = ""
        edges = ""
        for node in self.nodes:
            nodes += "{'type':'node', 'id':'%s', 'x':%d, 'y':%d, 'width':%d, 'height':%d}\n" % (node.id, node.left, node.top, node.width, node.height)
        for edge in self.edges:
            source = edge['source'].id
            target = edge['target'].id
            edges += "{'type':'edge', 'id':'%s_to_%s', 'source':'%s', 'target':'%s'}\n" % (source, target, source, target)
        return nodes + edges

class GraphNode:
    def __init__(self, id, left, top, width=60, height=60):
        #self.value = value
        
        self.id = id
        
        self.top = top
        self.left = left
        self.width = width
        self.height = height

        self.layoutPosX = 0
        self.layoutPosY = 0
        self.layoutForceX = 0
        self.layoutForceY = 0

    def get_bottom(self):
        return self.top + self.height

    def get_right(self):
        return self.left + self.width

    bottom = property(get_bottom)
    right = property(get_right)

    def GetBounds(self):
        return self.left, self.top, self.right, self.bottom
        
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
    
    print 'Done'
