# Coord Utilities

"""
Compensate for the fact that x, y for a ogl shape are the centre of the shape,
not the top left
"""

# Util

def _centrexy_to_topleftxy(shape, x, y):
    width, height = shape.GetBoundingBoxMax()
    topx = x + width / 2
    lefty = y + height / 2
    return topx, lefty
    
def _topleftxy_to_centrexy(shape):
    width, height = shape.GetBoundingBoxMax()
    centrex = shape.GetX() - width / 2
    centrey = shape.GetY() - height / 2
    return centrex, centrey

    width, height = shape.GetBoundingBoxMax()
    topx = x + width / 2
    lefty = y + height / 2
    return topx, lefty

# Traditional useful functions

def setpos(shape, x, y):
    topx, lefty = _centrexy_to_topleftxy(shape, x, y)
    shape.SetX(topx)
    shape.SetY(lefty)
    
def getpos(shape):
    return _topleftxy_to_centrexy(shape)

# Newer oo method, to be injected into the Shape class

def Move2(self, dc, x, y, display = True):
    """
    Provides a move function that works by top left
    not by the centre of the shape.
    
    Attach to ogl.Shape class using simple unbound technique see http://stackoverflow.com/questions/972/adding-a-method-to-an-existing-object
    Add a method to to a class very simply with e.g. 
        ogl.Shape.Move2 = Move2
    """
    topx, lefty = _centrexy_to_topleftxy(self, x, y)
    self.Move(dc, topx, lefty, display)
    
