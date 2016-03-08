import math
from line_intersection import FindLineIntersection

class Node:
    def __init__(self, id, left, top, width=60, height=60):
        self.id = id
        
        self.left = left
        self.top = top
        self.width = width
        self.height = height

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


def CalcEdgeBounds(a, c, vertical_edge_aware=True):
    """
    BEST
    
    Want to find where the line between a and c crosses the bounds of node 
    a and c and build a bounds rectangle from those points - of the taken up by the edge.
    The edge is outside and between the two nodes.
    """
    X,Y = 0,1
    point1 = list(a.CalcLineIntersectionPoints(a.get_centre_point(), c.get_centre_point())[0])
    point2 = list(c.CalcLineIntersectionPoints(a.get_centre_point(), c.get_centre_point())[0])
    
    # Adjust coords so that l,r in the correct order
    if point2[X] < point1[X]:
        point1, point2 = point2, point1
        
    # Adjust coords so that t,b in the correct order
    if point1[Y] > point2[Y]:
        point1[Y], point2[Y] = point2[Y], point1[Y]
        
    # Check for pure vertical lines
    if point1[X] == point2[X]:
        point1[X] -= 1
        point2[X] += 1
        
    # Check for pure horizontal lines
    if point1[Y] == point2[Y]:
        point1[Y] -= 1
        point2[Y] += 1
    
    print point1, point2
    return point1[X], point1[Y], point2[X], point2[Y], 


def CalcEdgeBounds_FromCrossingPoints(crossings):
    """
    UNUSED
    
    Makes a very tiny bounds sometimes, often unsuitable for avoiding edges
    because want to avoid the whole edge not just a portion of the edge.
    """
    X,Y = 0,1
    point1 = list(crossings[0])
    point2 = list(crossings[1])
    
    # Adjust coords so that l,r in the correct order
    if point2[X] < point1[X]:
        point1, point2 = point2, point1
        
    # Adjust coords so that t,b in the correct order
    if point1[Y] > point2[Y]:
        point1[Y], point2[Y] = point2[Y], point1[Y]
        
    # Check for pure vertical lines
    if point1[X] == point2[X]:
        point1[X] -= 1
        point2[X] += 1
        
    # Check for pure horizontal lines
    if point1[Y] == point2[Y]:
        point1[Y] -= 1
        point2[Y] += 1
    
    print point1, point2
    return point1[X], point1[Y], point2[X], point2[Y], 


"""
DEFUNCT TECHNIQUE - Here for historical purposes only.

Algorithm Purpose: to find points marked @
The key is figuring out angle A, using adj and opp
Then using angle A, feed in different adj lengths to work out all the needed
opposite lengths opp2 and opp3


  +------------+
  | a          |
  |            |
  |     +      |                 |  |
  |     |\     |                 |  |
  |     |A\    |                 |  | adiff
  |     |  \   |                 |  |
  +-----+---@--+                 |  |
        |opp2\            ydiff  |
    adj |     `.                 |
        |       \                |
        +----+---@----------+    |  |
        | opp3    \       c |    |  | cdiff
        |    |     \        |    |  |
        +----+------+       |    |  |
             | opp          |
             |              |
             +--------------+


            xdiff
        ..............
        
Note opposite and adjacent are relative terms - relative to the angle you are
trying to find.  In this case, we only care about angle A.

"""

def CalcEdgeBounds_USING_TRIG(a, c, vertical_edge_aware=True):
    # ABANDONED as my smarter CalcEdgeBounds() method does this and more, in less code!
    X,Y = 0,1
    def xdiff():
        return float(c_centre[X] - a_centre[X])
    def ydiff():
        return float(c_centre[Y] - a_centre[Y])
    def adiff():
        return float(a.bottom - a_centre[Y])
    def cdiff():
        return float(c_centre[Y] - c.top)
    def arctan(n):
        return abs(math.degrees(math.atan(n)))  # my version returns degrees
    def tan(deg):
        return math.tan(math.radians(deg))  # my version takes degrees as param
    def a_on_left():
        return a_centre[X] < c_centre[X]
        
    a_centre = a.get_centre_point()
    c_centre = c.get_centre_point()

    # assumes a is on top and c below and there is an edge between each of their
    # centres. If not, swap to make it so.
    if a_centre[Y] > c_centre[Y]:
        a,c = c,a
        a_centre,c_centre = c_centre,a_centre

    # if edge is exactly horizontal....
    # hmmmm
    if ydiff() == 0:
        if a.right  < c.left:
            who_is_on_left = a
        else:
            who_is_on_left = c
        l = a.right
        t = a_centre[Y] - 1
        r = c.left
        b = a_centre[Y] + 1
        return (l, t, r, b)        
    
    # step 1 - figure out top angle, which is the same whether c is to the left or to the right
    opposite = xdiff()
    adjacent = ydiff()
    angleA = arctan(opposite/adjacent)
    
    # step 2 - using angle, use adjacent length to give opposite length thus x we want
    adjacent2 = adiff()
    opposite2 = adjacent2 * tan(angleA)

    # step 3 - using angle, use long adjacent length to give opposite length thus x we want
    adjacent3 = ydiff() - cdiff()
    opposite3 = adjacent3 * tan(angleA)

    if a_on_left():
        l = a_centre[X]+opposite2
        r = a_centre[X]+opposite3
    else:
        l = a_centre[X]-opposite3
        r = a_centre[X]-opposite2
    
    # Repair tricky edge case - edge is exactly vertical, nodes centres exactly above each other
    # create a sensible bounds that has a little bit of width
    def x_are_equal():
        return abs(l-r) <= 0.001 
    if vertical_edge_aware and x_are_equal():
        l -= 1
        r += 1
        
    t = a.bottom
    b = c.top

    return (l, t, r, b)


if __name__ == "__main__":

    # Node A is above and to the left of node C
    # assumes A and C are connected with an edge
    a = Node('A', 0, 0, 4, 4)
    c = Node('C', 2, 6, 4, 2)
    res = CalcEdgeBounds_USING_TRIG(a,c)
    print res
    assert [str(round(f,2)) for f in res ] == ['2.8', '4.0', '3.6', '6.0']
    CalcEdgeBounds(a,c)
    
    # Handle feeding in swapped around parameters - algorithm should be
    # resilient and figure out who is on top
    res = CalcEdgeBounds_USING_TRIG(c,a)
    print res
    assert [str(round(f,2)) for f in res ] == ['2.8', '4.0', '3.6', '6.0']
    CalcEdgeBounds(c,a)
    
    # Node A is above and to the right of node C
    a = Node('A', 2, 0, 4, 4)
    c = Node('C', 0, 6, 4, 2)
    res = CalcEdgeBounds_USING_TRIG(a,c)
    print res
    assert [str(round(f,2)) for f in res ] == ['2.4', '4.0', '3.2', '6.0']
    CalcEdgeBounds(a,c)

    # Tricky edge case - edge is exactly vertical, nodes centres exactly above each other
    a = Node('A', 0, 0, 4, 4)
    c = Node('C', 0, 6, 4, 4)
    res = CalcEdgeBounds_USING_TRIG(a,c,vertical_edge_aware=False)
    print res
    assert [str(round(f,2)) for f in res ] == ['2.0', '4.0', '2.0', '6.0']
    CalcEdgeBounds(a,c)

    res = CalcEdgeBounds_USING_TRIG(a,c,)
    print res
    assert [str(round(f,2)) for f in res ] == ['1.0', '4.0', '3.0', '6.0']
    CalcEdgeBounds(a,c)

    # More cases - nodes side by side
    
    # two nodes side by side case 1, a slightly higer than c - TRIG version not
    # handling this yet, abandoned as CalcEdgeBounds() handles it nicely.
    a = Node('A', 0, 0, 4, 4)
    c = Node('C', 6, 1, 4, 4)
    res = CalcEdgeBounds_USING_TRIG(a,c,vertical_edge_aware=False)
    print res
    #assert [str(round(f,2)) for f in res ] == ['4.0', '1.8', '6.0', '2.2']  # 1.8 and 2.2 are guesses
    CalcEdgeBounds(a,c)

    # two nodes side by side case 2, c slightly higer than a - just swap params to test -  - TRIG version not
    # handling this yet, abandoned as CalcEdgeBounds() handles it nicely.
    res = CalcEdgeBounds_USING_TRIG(c,a,vertical_edge_aware=False)
    print res
    #assert [str(round(f,2)) for f in res ] == ['4.0', '1.8', '6.0', '2.2']  # 1.8 and 2.2 are guesses
    CalcEdgeBounds(c,a)

    # Tricky edge case - two nodes exactly side by side, edge is horizontal
    a = Node('A', 0, 0, 4, 4)
    c = Node('C', 6, 0, 4, 4)
    res = CalcEdgeBounds_USING_TRIG(a,c,vertical_edge_aware=False)
    print res
    # would otherwise be (4, 2, 6, 2) with both y's the same
    assert [str(round(f,2)) for f in res ] == ['4.0', '1.0', '6.0', '3.0']
    CalcEdgeBounds(a,c)

    a = Node('A', 0, 0, 4, 4)
    c = Node('C', 6, 3, 4, 2)
    CalcEdgeBounds(a,c)
    
    print "-"*80
        
    print "done"
