# Coord Utilities

"""
Compensate for the fact that x, y for a ogl shape are the centre of the shape,
not the top left
"""

# Util

def _topleftxy_to_centrexy(shape, x, y):
    width, height = shape.GetBoundingBoxMax()
    centrex = x + width / 2
    centrey = y + height / 2
    return centrex, centrey
    
def _shape_centrexy_to_lefttopxy(shape):
    width, height = shape.GetBoundingBoxMax()
    leftx = shape.GetX() - width / 2
    topy = shape.GetY() - height / 2
    return leftx, topy

# Traditional useful functions

def setpos(shape, x, y):
    centrex, centrey = _topleftxy_to_centrexy(shape, x, y)
    shape.SetX(centrex)
    shape.SetY(centrey)
    
def getpos(shape):
    return _shape_centrexy_to_lefttopxy(shape)

# Newer oo method, to be injected into the Shape class

def Move2(self, dc, x, y, display = True):
    """
    Provides a move function that works by top left
    not by the centre of the shape.
    
    Attach to ogl.Shape class using simple unbound technique see http://stackoverflow.com/questions/972/adding-a-method-to-an-existing-object
    Add a method to to a class very simply with e.g. 
        ogl.Shape.Move2 = Move2
    """
    topx, lefty = _topleftxy_to_centrexy(self, x, y)
    self.Move(dc, topx, lefty, display)
    
# Other util

def percent_change(end, start):
    if end > start:
        percent_increase = 100*(end-start)/start
        #print 'Percent increase:', percent_increase,'%'
        return percent_increase
    elif start > end:
        percent_decrease = 100*(start-end)/start
        #print 'Percent decrease:', percent_decrease,'%'
        return percent_decrease
    else:
        #print 'There is no change in value.'
        return 0

if __name__ == '__main__':
    print percent_change(9,10)
    print percent_change(5, 10)    