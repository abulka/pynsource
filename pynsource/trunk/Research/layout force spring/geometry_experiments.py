import math

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

    def get_centre_point(self):
        return ((self.left+self.width/2), (self.top+self.height/2))

"""

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

def CalcEdgeBounds(a, c, vertical_edge_aware=True):
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
        
    # assumes a is on top and c below and there is an edge between each of their centres
    a_centre = a.get_centre_point()
    c_centre = c.get_centre_point()

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

    # Node A is above and to the right of node C
    # assumes A and C are connected with an edge
    a = Node('A', 0, 0, 4, 4)
    c = Node('C', 2, 6, 4, 2)
    res = CalcEdgeBounds(a,c)
    print res
    assert [str(round(f,2)) for f in res ] == ['2.8', '4.0', '3.6', '6.0']
    
    # Node A is above and to the left of node C
    a = Node('A', 2, 0, 4, 4)
    c = Node('C', 0, 6, 4, 2)
    res = CalcEdgeBounds(a,c)
    print res
    assert [str(round(f,2)) for f in res ] == ['2.4', '4.0', '3.2', '6.0']

    # Tricky edge case - edge is exactly vertical, nodes centres exactly above each other
    a = Node('A', 0, 0, 4, 4)
    c = Node('C', 0, 6, 4, 4)
    res = CalcEdgeBounds(a,c,vertical_edge_aware=False)
    print res
    assert [str(round(f,2)) for f in res ] == ['2.0', '4.0', '2.0', '6.0']

    res = CalcEdgeBounds(a,c,)
    print res
    assert [str(round(f,2)) for f in res ] == ['1.0', '4.0', '3.0', '6.0']
    
    print "done"
