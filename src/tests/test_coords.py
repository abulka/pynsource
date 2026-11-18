import os
import unittest

from wxdiagram import Shape, RectangleShape, LineShape
from wxdiagram import initialize
from wxdiagram import line_control_points_to_xy_points

if "TRAVIS" not in os.environ:
    import wx

from gui.coord_utils import getpos  # returns left, top


@unittest.skip("Shape is an abstract base class and shouldn't be instantiated")
class TestCoordsShape(unittest.TestCase):
    def test_shape_basics(self):
        """Limited stuff we can do with a Shape because GetBoundingBox() is 0,0 and needs to be overriden"""
        shape = Shape(x=[0, 100], y=[0, 100])
        # expected, actual
        self.assertEqual((0, 0), shape.GetBoundingBoxMax())
        self.assertEqual([0, 100], shape.x)
        self.assertEqual([0, 100], shape.y)

        self.assertFalse(hasattr(shape, "_width"))  # Shapes and Line shapes don't have these
        self.assertFalse(hasattr(shape, "_height"))

        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)


@unittest.skipIf("TRAVIS" in os.environ, "no wxpython possible on travis")
class TestCoords(unittest.TestCase):
    """Create a wx.App() so that initialize() can set up the fonts RectangleShape uses."""

    def _create_rect(self, w, h):
        shape = RectangleShape(0, 0, w, h)
        shape.SetX(50)
        shape.SetY(50)
        return shape

    def test_basics(self):
        app = wx.App()
        initialize()
        shape = self._create_rect(100, 100)

        self.assertEqual([0, 100], shape.x)
        self.assertEqual([0, 100], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(50.0, shape._xpos)
        self.assertEqual(50.0, shape._ypos)
        self.assertEqual((100, 100), shape.GetBoundingBoxMax())
        self.assertEqual((0, 0), getpos(shape))

    def test_set_width(self):
        app = wx.App()
        initialize()
        shape = self._create_rect(100, 100)
        shape._width = 40
        self.assertEqual([30, 70], shape.x)
        self.assertEqual([0, 100], shape.y)
        self.assertEqual(40, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((40, 100), shape.GetBoundingBoxMax())
        self.assertEqual((30, 0), getpos(shape))

    def test_set_height(self):
        app = wx.App()
        initialize()
        shape = self._create_rect(100, 100)
        shape._height = 40
        self.assertEqual([0, 100], shape.x)
        self.assertEqual([30, 70], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(40, shape._height)
        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((100, 40), shape.GetBoundingBoxMax())
        self.assertEqual((0, 30), getpos(shape))

    def test_set_xpos(self):
        app = wx.App()
        initialize()
        shape = self._create_rect(100, 100)
        shape._xpos = 60
        self.assertEqual([10, 110], shape.x)
        self.assertEqual([0, 100], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(60, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((100, 100), shape.GetBoundingBoxMax())
        self.assertEqual((10, 0), getpos(shape))

    def test_set_ypos(self):
        app = wx.App()
        initialize()
        shape = self._create_rect(100, 100)
        shape._ypos = 60
        self.assertEqual([0, 100], shape.x)
        self.assertEqual([10, 110], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(50, shape._xpos)
        self.assertEqual(60, shape._ypos)
        self.assertEqual((100, 100), shape.GetBoundingBoxMax())
        self.assertEqual((0, 10), getpos(shape))

    # Move() which is move_center()

    def test_move_center(self):
        app = wx.App()
        initialize()
        shape = self._create_rect(100, 100)
        shape.move_center(60, 60)
        self.assertEqual([10, 110], shape.x)
        self.assertEqual([10, 110], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(60, shape._xpos)
        self.assertEqual(60, shape._ypos)
        self.assertEqual((100, 100), shape.GetBoundingBoxMax())
        self.assertEqual((10, 10), getpos(shape))

    # Edge case where create a 0 dimension shape and place at xpos/ypos (shape center) somewhere

    def test_zero_dimension_rect(self):
        app = wx.App()
        initialize()
        shape = self._create_rect(0, 0)
        shape._xpos = 50
        shape._ypos = 50
        self.assertEqual([50, 50], shape.x)
        self.assertEqual([50, 50], shape.y)
        self.assertEqual(0, shape._width)
        self.assertEqual(0, shape._height)
        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((0, 0), shape.GetBoundingBoxMax())
        self.assertEqual((50, 50), getpos(shape))

    def test_zero_dimension_line(self):
        app = wx.App()
        initialize()
        shape = LineShape()
        self.assertEqual([0, 0], shape.x)
        self.assertEqual([0, 0], shape.y)
        self.assertFalse(hasattr(shape, "_width"))  # Line shapes don't have these, use boundingbox
        self.assertFalse(hasattr(shape, "_height"))

        self.assertEqual(0, shape._xpos)
        self.assertEqual(0, shape._ypos)

        self.assertEqual((-20000, -20000), shape.GetBoundingBoxMax())  # cos no _lineControlPoints

        shape._xpos = 50
        shape._ypos = 50
        shape._lineControlPoints = [wx.RealPoint(40, 60), wx.RealPoint(60, 40)]

        self.assertEqual([50, 50], shape.x)
        self.assertEqual([50, 50], shape.y)

        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((20, 20), shape.GetBoundingBoxMax())
        self.assertEqual((40, 40), getpos(shape))

    def test_line_control_points_to_xy_points(self):
        lc_points = [(88.3, 164.0), (87.5, 54.0)]
        x_expected = [88.3, 87.5]
        y_expected = [164.0, 54.0]

        x_list, y_list = line_control_points_to_xy_points(lc_points)
        self.assertEqual(x_expected, x_list)
        self.assertEqual(y_expected, y_list)
