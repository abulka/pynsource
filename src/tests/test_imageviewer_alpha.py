"""Transparent PlantUML PNGs must be composited onto an explicit white page."""

import os
import sys
import unittest

import wx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.gui_imageviewer import ImageViewer  # noqa: E402


class TestTransparentBitmapComposite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(redirect=False)

    def test_transparent_png_is_composited_onto_white(self):
        image = wx.Image(20, 20, True)
        image.InitAlpha()
        # Transparent page with a black 1px border, like PlantUML output.
        for x in range(20):
            for y in range(20):
                if x in (0, 19) or y in (0, 19):
                    image.SetRGB(x, y, 0, 0, 0)
                    image.SetAlpha(x, y, 255)
                else:
                    image.SetAlpha(x, y, 0)
        bitmap = wx.Bitmap(image)

        class FakeViewer:
            maxWidth = 0
            maxHeight = 0
            bmp_transparent_ori = None
            bmp = None

        viewer = FakeViewer()
        ImageViewer._set_bitmap(viewer, bitmap)
        result = viewer.bmp.ConvertToImage()

        # Border stays black, but the transparent interior is explicitly white
        # (not an uninitialised platform-dependent bitmap).
        self.assertEqual(result.GetRed(0, 0), 0)
        self.assertEqual(result.GetRed(10, 10), 255)
        self.assertEqual(result.GetGreen(10, 10), 255)
        self.assertEqual(result.GetBlue(10, 10), 255)
        self.assertFalse(result.HasAlpha())


if __name__ == "__main__":
    unittest.main()
