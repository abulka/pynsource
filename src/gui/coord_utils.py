"""Coordinate helpers for the pynsource canvas.

wxdiagram stores each shape's extent in ``shape.x``/``shape.y`` and exposes the
centre through ``GetX``/``GetY``. Pynsource's graph model uses top-left
coordinates, so all conversions go through :func:`setpos` and :func:`getpos`.
"""

from dataclasses import dataclass


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


@dataclass
class ZoomInfo:
    scale: float = 1
    delta: float = None
