"""Geometry and selection tests for the custom ASCII view."""

import os
import sys
import unittest

import wx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gui.ascii_view import AsciiView  # noqa: E402


class TestAsciiView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = wx.GetApp() or wx.App(redirect=False)

    def setUp(self):
        self.frame = wx.Frame(None, size=(600, 400))
        self.view = AsciiView(self.frame)
        self.frame.Show()
        self.frame.Layout()
        wx.Yield()

    def tearDown(self):
        self.frame.Destroy()
        wx.Yield()

    def test_set_value_builds_scrollable_content(self):
        text = "\n".join(f"line {i:03d}" for i in range(100))
        self.view.SetValue(text)

        self.assertEqual(self.view.GetValue(), text)
        self.assertGreater(self.view.GetVirtualSize().height, self.view.GetClientSize().height)
        self.assertEqual(self.view.GetViewStart(), (0, 0))

        self.view.Scroll(0, 80)
        wx.Yield()
        self.assertEqual(self.view.GetViewStart()[1], 80)

    def test_bigger_font_increases_content_size(self):
        self.view.SetValue("\n".join(f"line {i:03d} " + "a" * 100 for i in range(50)))
        before = self.view.GetVirtualSize()
        self.view.SetFont(wx.Font(24, wx.MODERN, wx.NORMAL, wx.NORMAL, False))
        after = self.view.GetVirtualSize()

        self.assertGreater(after.height, before.height)
        self.assertGreater(after.width, before.width)

    def test_selection_text_across_lines(self):
        self.view.SetValue("alpha\nbeta\ngamma")
        self.view._selection_anchor = (0, 2)
        self.view._selection_current = (1, 2)

        self.assertEqual(self.view._selected_text(), "pha\nbe")


if __name__ == "__main__":
    unittest.main()
