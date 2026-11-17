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
# Positions are stored as top-left coordinates, matching the graph model and
# JSON persistence. wxdiagram's x/y lists hold the shape's extents.

def setpos(shape, x, y):
    shape.move_to(x, y)


def getpos(shape):
    if hasattr(shape, "_lineControlPoints") and len(shape._lineControlPoints) == 0:
        # don't want weird -2000 coords just because lines don't have control points
        width = shape.x[1] - shape.x[0]
        height = shape.y[1] - shape.y[0]
    else:
        width, height = shape.GetBoundingBoxMin()
    left = shape._xpos - width / 2
    top = shape._ypos - height / 2
    return left, top


# Other util

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
