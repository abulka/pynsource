"""Axis locking for ASCII two-finger scrolling."""

import os
import sys
import types
import unittest

import wx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pynsource_gui import MainApp  # noqa: E402


class FakeScroll:
    def __init__(self):
        self.position = [300, 300]

    def GetViewStart(self):
        return tuple(self.position)

    def Scroll(self, x, y):
        self.position = [x, y]


class FakeText:
    def GetTextExtent(self, text):
        return wx.Size(9 * len(text), 16)


class FakeWheel:
    def __init__(self, rotation, axis=wx.MOUSE_WHEEL_VERTICAL):
        self.rotation = rotation
        self.axis = axis

    def CmdDown(self):
        return False

    def ControlDown(self):
        return False

    def GetWheelRotation(self):
        return self.rotation

    def GetWheelDelta(self):
        return 10

    def GetWheelAxis(self):
        return self.axis

    def Skip(self):
        pass


def make_viewer():
    viewer = types.SimpleNamespace(
        working=False,
        multiText=FakeText(),
        asciiart=FakeScroll(),
        _ascii_scroll_remainder=0.0,
        _ascii_scroll_remainder_x=0.0,
        _ascii_scroll_axis=None,
        _ascii_axis_time=0.0,
        _ascii_zoom_point_size=None,
    )
    viewer.OnWheelZoom_ascii = types.MethodType(MainApp.OnWheelZoom_ascii, viewer)
    viewer._scroll_ascii_horizontally = types.MethodType(
        MainApp._scroll_ascii_horizontally, viewer
    )
    return viewer


class TestAsciiScrollAxisLock(unittest.TestCase):
    def test_vertical_scroll_ignores_small_lateral_noise(self):
        viewer = make_viewer()
        for _ in range(10):
            viewer.OnWheelZoom_ascii(FakeWheel(-10, wx.MOUSE_WHEEL_VERTICAL))
            viewer.OnWheelZoom_ascii(FakeWheel(-2, wx.MOUSE_WHEEL_HORIZONTAL))

        self.assertEqual(viewer.asciiart.position[0], 300)
        self.assertGreater(viewer.asciiart.position[1], 300)

    def test_small_horizontal_movement_alone_does_not_scroll(self):
        viewer = make_viewer()
        viewer.OnWheelZoom_ascii(FakeWheel(8, wx.MOUSE_WHEEL_HORIZONTAL))

        self.assertEqual(viewer.asciiart.position, [300, 300])

    def test_deliberate_horizontal_scroll_takes_over(self):
        viewer = make_viewer()
        for _ in range(10):
            viewer.OnWheelZoom_ascii(FakeWheel(8, wx.MOUSE_WHEEL_HORIZONTAL))

        self.assertGreater(viewer.asciiart.position[0], 300)
        self.assertEqual(viewer.asciiart.position[1], 300)

    def test_vertical_scroll_takes_over_right_after_horizontal(self):
        viewer = make_viewer()
        for _ in range(10):
            viewer.OnWheelZoom_ascii(FakeWheel(8, wx.MOUSE_WHEEL_HORIZONTAL))
        after_sideways = viewer.asciiart.position[0]

        for _ in range(6):
            viewer.OnWheelZoom_ascii(FakeWheel(-10, wx.MOUSE_WHEEL_VERTICAL))

        self.assertGreater(viewer.asciiart.position[1], 300)
        self.assertEqual(viewer.asciiart.position[0], after_sideways)


if __name__ == "__main__":
    unittest.main()
