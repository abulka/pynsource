"""SVG exports must carry an explicit white page background."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from generate_code.gen_plantuml import svg_on_white_background  # noqa: E402


class TestPlantUmlSvgBackground(unittest.TestCase):
    def test_white_rect_is_inserted_after_root_svg(self):
        svg = (
            b'<?xml version="1.0"?>\n'
            b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            b"<g><rect width=\"5\" height=\"5\"/></g></svg>"
        )
        result = svg_on_white_background(svg)

        self.assertIn(b'fill="#ffffff"', result)
        self.assertGreater(result.index(b"<rect"), result.index(b"<svg"))
        self.assertLess(result.index(b'fill="#ffffff"'), result.index(b"<g>"))

    def test_non_svg_and_empty_inputs_are_unchanged(self):
        self.assertEqual(svg_on_white_background(b""), b"")
        self.assertEqual(svg_on_white_background(b"not an svg"), b"not an svg")


if __name__ == "__main__":
    unittest.main()
