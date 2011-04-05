import math

def aa(opposite, adjacent):
    return round(180-(90+math.degrees(math.atan(float(opposite)/float(adjacent)))), 1)

alpha = aa(5,2)
#print alpha
assert round(alpha, 1) == 21.8

def bb(adjacent, angle):
    deg = angle * math.pi/180
    o = round(deg*float(adjacent), 1)
    return o

beta = bb(2, 21.8)
#print beta
assert round(beta, 1) == 0.8

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


a = Node('A', 0, 0, 4, 4)
c = Node('C', 2, 6, 4, 2)
a_centre = a.get_centre_point()
c_centre = c.get_centre_point()

# step 1
opposite = c_centre[1]-a_centre[1]
adjacent = c_centre[0]-c.left
assert opposite == 5, opposite
assert adjacent == 2, adjacent
alpha = aa(opposite, adjacent)
assert round(alpha, 1) == 21.8

# step 2
adjacent = a.bottom-a_centre[1]
assert adjacent == 2, adjacent
beta = bb(adjacent, alpha)
assert round(beta, 1) == 0.8

print "line crossing A node at", (a_centre[0]+beta, a.bottom)

######################

def CalcTopOfEdge(a, c):
    # assumes a is on top and c below and there is an edge between them going from
    # each of their centres
    a_centre = a.get_centre_point()
    c_centre = c.get_centre_point()
    
    # step 1
    opposite = c_centre[1]-a_centre[1]
    adjacent = c_centre[0]-c.left
    alpha_angle = aa(opposite, adjacent)
    
    # step 2
    adjacent = a.bottom-a_centre[1]
    opposite = bb(adjacent, alpha_angle)

    return (a_centre[0]+opposite, a.bottom)

print CalcTopOfEdge(a, c)

print "done"