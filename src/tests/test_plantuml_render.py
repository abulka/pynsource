import unittest
import os
import sys
import asyncio

sys.path.append("../src")
from generate_code import gen_plantuml
from generate_code.gen_plantuml import (
    png_pixel_size,
    svg_pixel_size,
    clamp_plantuml_scale,
    plant_uml_create_png_and_return_image_url_async,
    PLANTUML_PNG_LIMIT,
)
from common.plantuml import plant_uml_url


def fake_png(width, height=100):
    """Minimal PNG header - enough for png_pixel_size."""
    return (b"\x89PNG\r\n\x1a\n"
            + b"\x00\x00\x00\rIHDR"
            + width.to_bytes(4, "big")
            + height.to_bytes(4, "big")
            + b"\x08\x02\x00\x00\x00")


def fake_svg(width, height=100):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            f'style="width:{width}px;height:{height}px;background:#FFFFFF;" '
            f'width="{width}px" height="{height}px" viewBox="0 0 {width} {height}" '
            f'zoomAndPan="magnify"><rect width="11.5" height="12.5"/></svg>').encode()


class TestCasePlantUmlPngSize(unittest.TestCase):

    def test_reads_width_and_height(self):
        self.assertEqual(png_pixel_size(fake_png(538, 366)), (538, 366))

    def test_rejects_non_png(self):
        self.assertIsNone(png_pixel_size(b"not a png at all, honest"))
        self.assertIsNone(png_pixel_size(b""))

    def test_rejects_zero_size(self):
        self.assertIsNone(png_pixel_size(fake_png(0, 10)))


class TestCasePlantUmlSvgSize(unittest.TestCase):

    def test_reads_root_svg_size_not_first_rect(self):
        # the width= of the first <rect> must not be mistaken for the diagram width
        self.assertEqual(svg_pixel_size(fake_svg(5649, 368)), (5649, 368))

    def test_ignores_missing_dimensions(self):
        self.assertIsNone(svg_pixel_size(b'<svg xmlns="x"><rect width="5"/></svg>'))
        self.assertIsNone(svg_pixel_size(b"<html>not an svg</html>"))
        self.assertIsNone(svg_pixel_size(None))


class TestCasePlantUmlScaleClamp(unittest.TestCase):

    def test_small_diagram_keeps_requested_scale(self):
        self.assertEqual(clamp_plantuml_scale(2, 500), (2, False))
        self.assertEqual(clamp_plantuml_scale(4, 500), (4, False))

    def test_wide_diagram_steps_scale_down(self):
        # 3000 px wide: 2x would be 6000 > 4096, so 1x is the best the server can do
        self.assertEqual(clamp_plantuml_scale(2, 3000), (1, False))
        # 2000 px wide: exactly 4096 at 2x
        self.assertEqual(clamp_plantuml_scale(2, 2000), (2, False))

    def test_diagram_too_wide_even_at_scale_one(self):
        self.assertEqual(clamp_plantuml_scale(2, PLANTUML_PNG_LIMIT + 1), (1, True))

    def test_unknown_width_keeps_requested_scale(self):
        self.assertEqual(clamp_plantuml_scale(2, None), (2, False))

    def test_rubbish_scale_falls_back_to_one(self):
        self.assertEqual(clamp_plantuml_scale("nonsense", None), (1, False))


class TestCasePlantUmlTextlessRetry(unittest.TestCase):
    """The public server sometimes returns a render with no text: the layout
    collapses, so the PNG is narrower than its SVG. A retry with a different
    url normally gets a good one back."""

    def setUp(self):
        self.original_fetch_png = gen_plantuml._plant_uml_fetch_direct_async
        self.original_fetch_svg = gen_plantuml.plant_uml_fetch_svg_bytes_async
        plant_uml_create_png_and_return_image_url_async.cache_clear()
        self.progress_messages = []
        gen_plantuml.set_progress_callback(self.progress_messages.append)

    def tearDown(self):
        gen_plantuml._plant_uml_fetch_direct_async = self.original_fetch_png
        gen_plantuml.plant_uml_fetch_svg_bytes_async = self.original_fetch_svg
        gen_plantuml.set_progress_callback(None)
        plant_uml_create_png_and_return_image_url_async.cache_clear()

    def _run(self, txt, png_payloads, svg_width=300, requested_scale=1):
        calls = []

        async def fake_svg_fetch(*args, **kwargs):
            return fake_svg(svg_width)

        async def fake_png_fetch(plant_uml_txt, fmt, server):
            width = png_payloads[min(len(calls), len(png_payloads) - 1)]
            calls.append((plant_uml_txt, width))
            return fake_png(width), 200

        gen_plantuml.plant_uml_fetch_svg_bytes_async = fake_svg_fetch
        gen_plantuml._plant_uml_fetch_direct_async = fake_png_fetch
        render = asyncio.run(plant_uml_create_png_and_return_image_url_async(
            txt, plantuml_server_local_url=None, requested_scale=requested_scale))
        return render, calls

    def test_good_render_is_used_first_time(self):
        render, calls = self._run("good render", [300])
        self.assertEqual(self.progress_messages, [])
        self.assertEqual(len(calls), 1)
        self.assertEqual(render.attempts, 1)
        self.assertFalse(render.too_wide)
        self.assertNotIn("pynsource-retry", render.image_url)

    def test_textless_render_is_retried(self):
        render, calls = self._run("textless then good", [100, 300])
        self.assertEqual(len(calls), 2)
        self.assertEqual(render.attempts, 2)
        self.assertIn("pynsource-retry", calls[1][0])
        # the url handed to the viewer is the retried one
        self.assertEqual(render.image_url, plant_uml_url(calls[1][0], fmt="png"))
        # and the user was told a retry was happening
        self.assertTrue(any("retrying" in m for m in self.progress_messages))

    def test_keeps_widest_when_every_attempt_loses_its_text(self):
        render, calls = self._run("always textless", [100, 120, 110])
        self.assertEqual(len(calls), 3)
        self.assertEqual(render.attempts, 3)
        # widest render was the second attempt, so its url wins
        self.assertEqual(render.image_url, plant_uml_url(calls[1][0], fmt="png"))

    def test_scale_is_clamped_for_wide_diagrams(self):
        render, _ = self._run("wide diagram", [3000], svg_width=3000, requested_scale=2)
        self.assertEqual(render.scale, 1)
        self.assertFalse(render.too_wide)

    def test_too_wide_is_reported(self):
        render, _ = self._run("very wide diagram", [4096],
                              svg_width=PLANTUML_PNG_LIMIT + 500, requested_scale=2)
        self.assertEqual(render.scale, 1)
        self.assertTrue(render.too_wide)

    def test_cropped_render_is_reported(self):
        # server cut the diagram off at its 4096 px limit
        render, _ = self._run("cropped diagram", [PLANTUML_PNG_LIMIT],
                              svg_width=PLANTUML_PNG_LIMIT, requested_scale=2)
        self.assertTrue(render.too_wide)

    def test_degraded_svg_width_is_corrected_from_the_png(self):
        # the svg came back textless (width 108) but the png is fine (269 at 1x)
        render, calls = self._run("degraded svg", [269], svg_width=108, requested_scale=1)
        self.assertEqual(render.attempts, 1)
        self.assertEqual(render.image_url, plant_uml_url(calls[0][0], fmt="png"))


def suite():
    suite1 = unittest.makeSuite(TestCasePlantUmlPngSize, "test")
    suite2 = unittest.makeSuite(TestCasePlantUmlSvgSize, "test")
    suite3 = unittest.makeSuite(TestCasePlantUmlScaleClamp, "test")
    suite4 = unittest.makeSuite(TestCasePlantUmlTextlessRetry, "test")
    alltests = unittest.TestSuite((suite1, suite2, suite3, suite4))
    return alltests


def main():
    runner = unittest.TextTestRunner(descriptions=0, verbosity=2)
    runner.run(suite())


if __name__ == "__main__":
    main()
