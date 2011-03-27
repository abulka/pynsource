# graph / node abstraction
# for use by spring layout and overlap removeal

class Graph:
    def __init__(self):
        self.clear()
        
    def clear(self):
        self.nodeSet = {}
        self.nodes = []
        self.edges = []

        self.layoutMinX = 0
        self.layoutMaxX = 0
        self.layoutMinY = 0
        self.layoutMaxY = 0
        
    def addNode(self, div):
        key = div.id
        element = div

        node = self.nodeSet.get(key, None)
        if not node:
            node = GraphNode(element)
            self.nodeSet[key] = node
            self.nodes.append(node)
        return node

    def findNode(self, id):
        node = self.nodeSet.get(id, None)
        return node

    def deleteNode(self, id):
        node = self.findNode(id)
        if node:
            self.nodes.remove(node)
            if id in self.nodeSet.keys():
                del self.nodeSet[id]
        for edge in self.edges[:]:
            if edge['source'] == id or edge['target'] == id:
                self.edges.remove(edge)
            
    def addEdge(self, source, target):
        # Uniqueness must be ensured by caller
        s = self.addNode(source)
        t = self.addNode(target)
        edge = {'source': s, 'target': t}
        self.edges.append(edge)

    def LoadGraphFromStrings(self, filedata):
        # load from persistence
        filedata = filedata.split('\n')
        for data in filedata:
            data = data.strip()
            if not data:
                continue
            #print data
            data = eval(data)
            if data['type'] == 'node':
                # {'type':'node', 'id':'c5', 'x':230, 'y':174, 'width':60, 'height':120}
                div = Div(data['id'], data['y'], data['x'], data['width'], data['height'])
                self.addNode(div)
            elif data['type'] == 'edge':
                source_id = data['source']
                target_id = data['target']
                # need to find the node corresponding to a div of id whatever
                # wire together the two divs
                sourcenode = self.findNode(source_id)
                targetnode = self.findNode(target_id)
                if not sourcenode:
                    print "Couldn't load source from persistence", source_id
                    continue
                if not targetnode:
                    print "Couldn't load target from persistence", target_id
                    continue
                self.addEdge(sourcenode.value, targetnode.value)  # addEdge takes div objects as parameters

    def GraphToString(self):
        nodes = ""
        edges = ""
        for node in self.nodes:
            v = node.value
            nodes += "{'type':'node', 'id':'%s', 'x':%d, 'y':%d, 'width':%d, 'height':%d}\n" % (v.id, v.left, v.top, v.width, v.height)
        for edge in self.edges:
            source = edge['source'].value.id
            target = edge['target'].value.id
            edges += "{'type':'edge', 'id':'%s_to_%s', 'source':'%s', 'target':'%s'}\n" % (source, target, source, target)
        return nodes + edges

class GraphNode:
    def __init__(self, value):
        self.value = value
        
        self.layoutPosX = 0
        self.layoutPosY = 0
        self.layoutForceX = 0
        self.layoutForceY = 0

    def GetBounds(self):
        v = self.value
        return v.left, v.top, v.right, v.bottom
        
    def __str__(self):
        return "NodeDiv %s: x,y (%d, %d) w,h (%d, %d)" % (self.value.id, self.value.left, self.value.top, self.value.width, self.value.height)
        
class Context:
    pass

class Div:
    def __init__(self, id, top, left, width=60, height=60):  # TODO: top, left should be left, top
        self.id = id
        self.top = top
        self.left = left
        self.width=width
        self.height=height
    
    def get_bottom(self):
        return self.top + self.height
    def get_right(self):
        return self.left + self.width
    bottom = property(get_bottom)
    right = property(get_right)
    

if __name__ == '__main__':

    g = Graph()
    
    #n1 = Div('wilma', 10, 10)
    #n2 = Div('fred', 50, 50)
    #g.addEdge(n1, n2)
    #n3 = Div('andy', 500, 500)
    #g.addEdge(n1, n3)

    n1 = Div('A', 0, 0, 200, 200)
    n2 = Div('B', 0, 0, 200, 200)
    g.addEdge(n1, n2)
    
    for node in g.nodes:
        print node.value.id, (node.layoutPosX, node.layoutPosY)
    
    print 'Done'
