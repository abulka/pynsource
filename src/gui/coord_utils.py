# Coord Utilities

"""
Compensate for the fact that x, y for a ogl shape are the centre of the shape,
not the top left
"""

# Util

import platform
import sys

if sys.version_info.minor >= 7:
    from dataclasses import dataclass
from gui.settings import PRO_EDITION

# Traditional useful functions

if PRO_EDITION:
    def setpos(shape, x, y):
        shape.move_to(x, y)

    def getpos(shape):
        # return shape.x[0], shape.y[0]

        if hasattr(shape, "_lineControlPoints") and len(shape._lineControlPoints) == 0:
            # don't want weird -2000 coords just because lines don't have
            width = shape.x[1] - shape.x[0]
            height = shape.y[1] - shape.y[0]
        else:
            width, height = shape.GetBoundingBoxMin()
        left = shape._xpos - width / 2
        top = shape._ypos - height / 2
        return left, top

    # def Move2(self, dc, x, y, display=True):
    #     # OK this is the problem.  move_to is a left, top thing which is what we want, but we
    #     # actually need the smarts of self.Move which also does movelinks etc.
    #     self.move_to(x, y)
else:
    # WX.OGL

    def setpos(shape, x, y):
        centrex, centrey = _topleftxy_to_centrexy(shape, x, y)
        shape.SetX(centrex)
        shape.SetY(centrey)

    def getpos(shape):
        return _shape_centrexy_to_lefttopxy(shape)

    # Newer oo method, to be injected into the Shape class

def Move2(self, dc, x, y, display=True):
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

def percent_change(end, start):
    if end > start:
        percent_increase = 100 * (end - start) / start
        # print 'Percent increase:', percent_increase,'%'
        return percent_increase
    elif start > end:
        percent_decrease = 100 * (start - end) / start
        # print 'Percent decrease:', percent_decrease,'%'
        return percent_decrease
    else:
        # print 'There is no change in value.'
        return 0

if sys.version_info.minor < 7:
    # If running under Python 3.6 which doesn't have data classes
    class ZoomInfo:
        def __init__(self, scale: float=1, delta: float=None):
            self.scale = scale
            self.delta = delta
else:
    @dataclass
    class ZoomInfo:
        scale: float = 1
        delta: float = None

if __name__ == "__main__":
    print(percent_change(9, 10))
    print(percent_change(5, 10))
