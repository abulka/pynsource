"""Canvas content bounds: what fit-to-window and the scrollbars cover.

Regression test for "resize an image large, zoom in, and the far edges cannot
be scrolled to": UmlCanvas.getContentBounds() used to count only UML boxes, so
imported images were outside the canvas' scroll range.

Uses plain fakes rather than a real wx canvas so it runs headless.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gui.uml_canvas import UmlCanvas  # noqa: E402


class FakeShape:
    def __init__(self, left, top, width, height, bitmap=False):
        self._left = left
        self._top = top
        self._width = width
        self._height = height
        if bitmap:
            self.is_bitmap = True

    def GetBoundingBoxMax(self):
        return self._width, self._height

    def GetX(self):
        return self._left + self._width / 2

    def GetY(self):
        return self._top + self._height / 2


class FakeDiagram:
    def __init__(self, shapes):
        self._shapes = shapes

    def GetShapeList(self):
        return list(self._shapes)


class FakeCanvas:
    def __init__(self, shapes, boxes):
        self._shapes = shapes
        self.umlboxshapes = boxes

    def GetDiagram(self):
        return FakeDiagram(self._shapes)


def _bounds(shapes, boxes):
    # Call the real method without constructing a wx window.
    return UmlCanvas.getContentBounds(FakeCanvas(shapes, boxes))


def test_images_extend_content_bounds():
    box = FakeShape(0, 0, 100, 80)
    image = FakeShape(0, 0, 2000, 1500, bitmap=True)

    assert _bounds([box, image], boxes=[box]) == (2000, 1500)


def test_lines_are_excluded_from_content_bounds():
    box = FakeShape(0, 0, 100, 80)
    stray_line = FakeShape(0, 0, 9000, 9000)  # no is_bitmap, not a box

    assert _bounds([box, stray_line], boxes=[box]) == (100, 80)


def test_boxes_still_count_on_their_own():
    box = FakeShape(50, 40, 200, 100)

    assert _bounds([box], boxes=[box]) == (250, 140)
