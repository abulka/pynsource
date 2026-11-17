"""Contract test for the wxdiagram features pynsource uses.

Kept in pynsource so a library change that removes or renames something the
canvas depends on fails here, next to the code that needs it.
"""

import unittest

import wxdiagram


NAMES = [
    # canvas/diagram
    "ShapeCanvas",
    "Diagram",
    "Shape",
    "ShapeEvtHandler",
    "ShapeRegion",
    # shapes
    "RectangleShape",
    "DividedShape",
    "BitmapShape",
    "PolygonShape",
    "LineShape",
    # mixins
    "Connectable",
    "Resizeable",
    "Selectable",
    "Attributable",
    # helpers
    "initialize",
    "GetArrowPoints",
    "GetPointOnLine",
    "line_control_points_to_xy_points",
    # arrows
    "ARROW_ARROW",
    "ARROW_DOUBLE_OBLIQUE",
    "ARROW_FILLED_CIRCLE",
    "ARROW_HOLLOW_CIRCLE",
    "ARROW_METAFILE",
    "ARROW_POSITION_END",
    "ARROW_POSITION_MIDDLE",
    "ARROW_POSITION_START",
    "ARROW_SINGLE_OBLIQUE",
    # text formatting
    "FORMAT_NONE",
    "FORMAT_CENTRE_HORIZ",
    "FORMAT_CENTRE_VERT",
]


class TestWxdiagramContract(unittest.TestCase):
    def test_pynsource_names_exist(self):
        missing = [name for name in NAMES if getattr(wxdiagram, name, None) is None]
        self.assertEqual(missing, [], f"wxdiagram is missing names pynsource uses: {missing}")

    def test_canvas_extension_points(self):
        self.assertTrue(hasattr(wxdiagram.Shape, "MoveTo"))
        self.assertTrue(hasattr(wxdiagram.ShapeCanvas, "getContentBounds"))
        self.assertTrue(hasattr(wxdiagram.ShapeCanvas, "getContentOrigin"))
        for name in ["update_virtual_size", "ZoomToFit", "ZoomIn", "ZoomOut", "ZoomReset"]:
            self.assertTrue(hasattr(wxdiagram.ShapeCanvas, name), name)

    def test_canvas_flags_default_to_automatic(self):
        # pynsource switches these off in UmlCanvas, so the defaults must stay on
        # for ordinary applications.
        self.assertLess(wxdiagram.ShapeCanvas.ZOOM_MIN_SCALE, 1.0)
        self.assertGreater(wxdiagram.ShapeCanvas.ZOOM_MAX_SCALE, 1.0)
