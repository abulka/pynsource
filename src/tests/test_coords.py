import os
import unittest
from gui.settings import PRO_EDITION, LOCAL_OGL

if "TRAVIS" not in os.environ:
    if PRO_EDITION:
        # import ogl
        from ogl2 import Shape, RectangleShape, LineShape
        from ogl2 import OGLInitialize
        from ogl2 import line_control_points_to_xy_points
    else:
        if LOCAL_OGL:
            from ogl import Shape, RectangleShape, LineShape
            from ogl import OGLInitialize
        else:
            from wx.lib.ogl import Shape, RectangleShape, LineShape
            from wx.lib.ogl import OGLInitialize
    import wx

from gui.coord_utils import getpos  # returns left, top


@unittest.skip("In wx.ogl Shape is an abstract class and shouldn't be instantiated")
class TestCoordsShape(unittest.TestCase):
    def test_shape_basics(self):
        """Limited stuff we can do with a Shape because GetBoundingBox() is 0,0 and needs to be overriden"""
        shape = Shape(x=[0,100], y=[0,100])
        # expected, actual
        self.assertEqual((0,0), shape.GetBoundingBoxMax())
        self.assertEqual([0,100], shape.x)
        self.assertEqual([0,100], shape.y)

        self.assertFalse(hasattr(shape, "_width"))  # Shapes and Line shapes don't have these
        self.assertFalse(hasattr(shape, "_height"))

        # # You would think this is 100 but its 0 because width is done in terms of
        # # GetBoundingBoxMax() which is implemented in Shape as returning 0,0 and needs overriding
        # self.assertNotEqual(100, shape._width)
        # self.assertNotEqual(100, shape._height)
        # self.assertEqual(0, shape._width)
        # self.assertEqual(0, shape._height)

        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)


@unittest.skipIf("TRAVIS" in os.environ, "no wxpython possible on travis")
class TestCoords(unittest.TestCase):
    """Note: create of wx.App() needed so that we can OGLInitialize() which is needed for fonts that
    RectangleShape uses.  Creating app doesn't seem to work if put in setUp or setUpClass,
    unfortunately"""

    def _create_rect(self, w, h):
        if PRO_EDITION:
            shape = RectangleShape(0, 0, w, h)
        else:
            shape = RectangleShape(w, h)

        # set shape center
        shape.SetX(50)
        shape.SetY(50)

        return shape

    def test_basics(self):
        app = wx.App()
        OGLInitialize()
        shape = self._create_rect(100, 100)

        # expected, actual

        if PRO_EDITION:
            self.assertEqual([0,100], shape.x)
            self.assertEqual([0,100], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(50.0, shape._xpos)
        self.assertEqual(50.0, shape._ypos)
        self.assertEqual((100, 100), shape.GetBoundingBoxMax())
        self.assertEqual((0, 0), getpos(shape))

    def test_set_width(self):
        app = wx.App()
        OGLInitialize()
        shape = self._create_rect(100, 100)
        shape._width = 40
        if PRO_EDITION:
            self.assertEqual([30,70], shape.x)
            self.assertEqual([0,100], shape.y)
        self.assertEqual(40, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((40, 100), shape.GetBoundingBoxMax())
        self.assertEqual((30, 0), getpos(shape))

    def test_set_height(self):
        app = wx.App()
        OGLInitialize()
        shape = self._create_rect(100, 100)
        shape._height = 40
        if PRO_EDITION:
            self.assertEqual([0,100], shape.x)
            self.assertEqual([30,70], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(40, shape._height)
        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((100, 40), shape.GetBoundingBoxMax())
        self.assertEqual((0, 30), getpos(shape))

    def test_set_xpos(self):
        app = wx.App()
        OGLInitialize()
        shape = self._create_rect(100, 100)
        shape._xpos = 60
        if PRO_EDITION:
            self.assertEqual([10,110], shape.x)
            self.assertEqual([0,100], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(60, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((100, 100), shape.GetBoundingBoxMax())
        self.assertEqual((10, 0), getpos(shape))

    def test_set_ypos(self):
        app = wx.App()
        OGLInitialize()
        shape = self._create_rect(100, 100)
        shape._ypos = 60
        if PRO_EDITION:
            self.assertEqual([0,100], shape.x)
            self.assertEqual([10,110], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(50, shape._xpos)
        self.assertEqual(60, shape._ypos)
        self.assertEqual((100, 100), shape.GetBoundingBoxMax())
        self.assertEqual((0, 10), getpos(shape))

    # Move() which is move_center()

    @unittest.skipIf(not PRO_EDITION, "ogltwo specific test")
    def test_move_center(self):
        app = wx.App()
        OGLInitialize()
        shape = self._create_rect(100, 100)
        shape.move_center(60, 60)
        self.assertEqual([10,110], shape.x)
        self.assertEqual([10,110], shape.y)
        self.assertEqual(100, shape._width)
        self.assertEqual(100, shape._height)
        self.assertEqual(60, shape._xpos)
        self.assertEqual(60, shape._ypos)
        self.assertEqual((100, 100), shape.GetBoundingBoxMax())
        self.assertEqual((10, 10), getpos(shape))

    # Edge case where create a 0 dimension shape and place at xpos/ypos (shape center) somewhere

    def test_zero_dimension_rect(self):
        app = wx.App()
        OGLInitialize()
        shape = self._create_rect(0, 0)
        shape._xpos = 50
        shape._ypos = 50
        if PRO_EDITION:
            self.assertEqual([50,50], shape.x)
            self.assertEqual([50,50], shape.y)
        self.assertEqual(0, shape._width)
        self.assertEqual(0, shape._height)
        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((0, 0), shape.GetBoundingBoxMax())
        self.assertEqual((50, 50), getpos(shape))

    def test_zero_dimension_line(self):
        app = wx.App()
        OGLInitialize()
        shape = LineShape()
        if PRO_EDITION:
            self.assertEqual([0,0], shape.x)
            self.assertEqual([0,0], shape.y)
        self.assertFalse(hasattr(shape, "_width"))  # Line shapes don't have these, use boundingbox
        self.assertFalse(hasattr(shape, "_height"))

        # ogltwo fails this because for a line without line control points, xpos and ypos
        # which are derived from boundingbox, end up in -2000 land - yikes!
        # perhaps we re-implement xpos and ypos for Lines? to be based on .x.y point lists?
        # OK I did that - and these tests pass - but what implications for the rest of the system?
        self.assertEqual(0, shape._xpos)
        self.assertEqual(0, shape._ypos)

        self.assertEqual((-20000, -20000), shape.GetBoundingBoxMax())  # cos no _lineControlPoints
        # self.assertEqual((0, 0), getpos(shape))

        shape._xpos = 50
        shape._ypos = 50
        shape._lineControlPoints = [wx.RealPoint(40, 60), wx.RealPoint(60, 40)]

        if PRO_EDITION:
            self.assertEqual([50,50], shape.x)
            self.assertEqual([50,50], shape.y)

        # Lines don't have ._width, ._height attributes, according to wx.ogl
        # self.assertEqual(0, shape._width)
        # self.assertEqual(0, shape._height)

        self.assertEqual(50, shape._xpos)
        self.assertEqual(50, shape._ypos)
        self.assertEqual((20, 20), shape.GetBoundingBoxMax())
        self.assertEqual((40, 40), getpos(shape))


    @unittest.skipIf(not PRO_EDITION, "ogltwo specific test")
    def test_line_control_points_to_xy_points(self):
        lc_points = [(88.3, 164.0), (87.5, 54.0)]
        x_expected = [88.3, 87.5]
        y_expected = [164.0, 54.0]

        x_list, y_list = line_control_points_to_xy_points(lc_points)
        self.assertEqual(x_expected, x_list)
        self.assertEqual(y_expected, y_list)
