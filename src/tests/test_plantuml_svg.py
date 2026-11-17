import unittest
import os
import sys

sys.path.append("../src")
from common.plantuml import plant_uml_url, deflate_and_encode


class TestCasePlantUmlUrl(unittest.TestCase):

    def test_svg_and_png_share_encoded_payload(self):
        txt = "class Foo {\n  bar()\n}\n"
        svg_url = plant_uml_url(txt, fmt="svg")
        png_url = plant_uml_url(txt, fmt="png")
        self.assertTrue(svg_url.startswith("http://www.plantuml.com/plantuml/svg/"))
        self.assertTrue(png_url.startswith("http://www.plantuml.com/plantuml/png/"))
        # same diagram -> same encoded payload, only the format differs
        self.assertEqual(svg_url.split("/svg/")[1], png_url.split("/png/")[1])
        self.assertEqual(svg_url.split("/svg/")[1], deflate_and_encode(txt))

    def test_uml_page_endpoint_swapped_for_format(self):
        # the configured server url is the /uml/ page endpoint - the
        # direct image endpoints are siblings of it
        txt = "class Foo {\n}\n"
        url = plant_uml_url(txt, fmt="svg", server_url="http://localhost:8080/plantuml/uml")
        self.assertTrue(url.startswith("http://localhost:8080/plantuml/svg/"))

    def test_bare_base_server_url(self):
        txt = "class Foo {\n}\n"
        url = plant_uml_url(txt, fmt="png", server_url="http://localhost:8080/plantuml")
        self.assertTrue(url.startswith("http://localhost:8080/plantuml/png/"))

    def test_trailing_slash_tolerated(self):
        txt = "class Foo {\n}\n"
        url = plant_uml_url(txt, fmt="svg", server_url="http://www.plantuml.com/plantuml/uml/")
        self.assertTrue(url.startswith("http://www.plantuml.com/plantuml/svg/"))
        self.assertNotIn("//svg", url.split("http://")[1])

    def test_invalid_format_raises(self):
        with self.assertRaises(ValueError):
            plant_uml_url("class Foo {\n}\n", fmt="jpg")


def suite():
    suite1 = unittest.makeSuite(TestCasePlantUmlUrl, "test")
    alltests = unittest.TestSuite((suite1,))
    return alltests


def main():
    runner = unittest.TextTestRunner(
        descriptions=0, verbosity=2
    )  # default is descriptions=1, verbosity=1
    runner.run(suite())


if __name__ == "__main__":
    main()
