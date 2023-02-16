# CanvasResizer looks after canvas resizing and virtual size of canvas

from .coord_utils import percent_change, ZoomInfo
from common.architecture_support import whoscalling2
import wx
from typing import List, Set, Dict, Tuple, Optional
from enum import Enum
from gui.settings import PRO_EDITION

MIN_SENSIBLE_CANVAS_SIZE = 200

ZoomTo = Enum('ZoomTo', 'MOUSE_POS CLIENT_CENTER')
ZOOM_BEHAVIOUR = ZoomTo.MOUSE_POS  # when shape is unselected, what is the behaviour


class CanvasResizer(object):
    """
    Looks after the reszing of the canvas virtual size plus a few other related functions.
    We change virtual size by calling SetScrollbars()
    """

    def __init__(self, canvas):
        self.canvas = canvas
        self.allshapes_bounds_cached = None
        self.allshapes_bounds_last = None
        self.scale_last = None  # Cache zoom info

        # setting SetScrollbars() can trigger a frame resize thus this flag prevents 2 calls
        self.working = False

    def canvas_too_small(self):
        width, height = self.canvas.GetSize()
        return width < MIN_SENSIBLE_CANVAS_SIZE or height < MIN_SENSIBLE_CANVAS_SIZE

    # UTILITY - called by OnResizeFrame, layout_and_position_shapes
    def frame_calibration(self, auto_resize_virtualcanvas=True):
        """
        Calibrate model/shape/layout coordinate mapping system to the visible
        physical window canvas size. When resizing a frame, obviously the bounds
        of the "all shapes" area doesn't change which is why we pass
        bounds_dirty=False. And shrinkage_leeway=0 means resizing is strict and
        avoids the lazy delayed trimming algorithm.
        """
        if self.canvas_too_small():
            return
        self.canvas.coordmapper.Recalibrate(
            self.canvas.frame.GetClientSize()
        )  # passing self.GetVirtualSize() seems to spread the layout out too much

        if auto_resize_virtualcanvas:
            self.resize_virtual_canvas_tofit_bounds(shrinkage_leeway=0, bounds_dirty=False)

    def zoom_unchanged(self, zoom_info):
        """Check to see if cached zoom scale the same as new zoom scale"""
        if not zoom_info:
            return True
        if zoom_info.scale == self.scale_last:
            return True
        return False

    # UTILITY - used by 's' key, mega_refresh, frame_calibration, OnEndDragLeft
    def resize_virtual_canvas_tofit_bounds(self, shrinkage_leeway=40, bounds_dirty: bool=False, zoom_info: ZoomInfo=None):
        """
        Set canvas virtual size to the bounds of all the shapes.
        virtual size must be >= bounds
        virtual size should be trimmed down to bounds where possible
        """
        DEBUG = False
        DEBUG_ACTION_TAKEN = False

        if bounds_dirty:
            self.allshapes_bounds_cached = None

        if self.allshapes_bounds_last == self.calc_allshapes_bounds() and self.zoom_unchanged(zoom_info):
            if DEBUG_ACTION_TAKEN:
                print("nochange")
            return

        # Re-entrancy protection - because an action by _do_resize_virtual_canvas_tofit_bounds()
        # causes frame resize -> which then eventually calls back into here!
        if self.working:
            # print("working - return")
            return
        self.working = True

        bounds_width, bounds_height = self.calc_allshapes_bounds()
        virt_width, virt_height = self.canvas.GetVirtualSize()
        oldscrollx = self.canvas.GetScrollPos(wx.HORIZONTAL)
        oldscrolly = self.canvas.GetScrollPos(wx.VERTICAL)
        offsetx, offsety, zoom_point_x, zoom_point_y = self.calc_pan_offsets(zoom_info)

        if DEBUG:
            if zoom_info:
                print(
                  f"BOUNDS ({int(bounds_width):4d},{int(bounds_height):4d}) * "
                  f"Scale {zoom_info.scale:3.1f} => "
                  f"{int(bounds_width * zoom_info.scale):4d},{int(bounds_height * zoom_info.scale):4d}  |  "
                  f"PAN ({oldscrollx:3d},{oldscrolly:3d})",
                  f"+ {int(offsetx):-3d},{int(offsety):-3d} ",
                  f"=> {int(oldscrollx + offsetx):-3d},{int(oldscrolly + offsety):-3d}",
                  end=" ")
                if zoom_info.delta:
                    print(f"  |  DELTA {zoom_info.delta:-5.2f} |  zoom_point {zoom_point_x},{zoom_point_y}")
                else:
                    print()

        if zoom_info:
            bounds_width *= zoom_info.scale
            bounds_height *= zoom_info.scale
        else:
            if DEBUG:
                print("no zoom?", end=' ')

        need_more_virtual_room = bounds_width > virt_width or bounds_height > virt_height
        need_to_compact = will_compact = bounds_width < virt_width or bounds_height < virt_height

        if need_to_compact and shrinkage_leeway > 0:  # Relax the compacting rule
            will_compact = (
                percent_change(bounds_width, virt_width) > shrinkage_leeway
                or percent_change(bounds_height, virt_height) > shrinkage_leeway
                or (zoom_info != None and zoom_info.delta)
            )

        if not DEBUG_ACTION_TAKEN:
            if need_more_virtual_room or will_compact:
                self._do_resize_virtual_canvas_tofit_bounds((bounds_width, bounds_height), (offsetx, offsety))
                if zoom_info:
                    self.scale_last = zoom_info.scale
        else:
            # Debug version of above last two lines.
            #
            print(f"need_more_virtual_room={need_more_virtual_room}, need_to_compact={need_to_compact}")
            if need_to_compact and not will_compact:
               print("(compact pending)", end=" ")

            if need_more_virtual_room or will_compact:
               print("- action taken!")
               # print("\n",whoscalling2())
               self._do_resize_virtual_canvas_tofit_bounds((bounds_width, bounds_height), (offsetx, offsety))
               if zoom_info:
                   self.scale_last = zoom_info.scale
            else:
               print("(no action)")

        self.working = False

    def calc_pan_offsets(self, zoom_info):
        offsetx = 0
        offsety = 0
        zoom_point_x = zoom_point_y = None
        if zoom_info and zoom_info.delta != None:  # if have a zoom_info, then might have delta too
            scale_change = zoom_info.delta
            # zoom_point_x, zoom_point_y = 210, 489  # figure this out later
            if self.canvas.getSelectedShapes():
                selected_shape = self.canvas.getSelectedShapes()[0]
                zoom_point_x, zoom_point_y = selected_shape._xpos, selected_shape._ypos
            else:
                if ZOOM_BEHAVIOUR == ZoomTo.MOUSE_POS:
                    zoom_point_x, zoom_point_y = self.canvas.mouse_pos_in_client_coords()
                else:
                    # zoom to centre of workspace
                    zoom_point_x, zoom_point_y = self.canvas.GetClientSize()[0] / 2, \
                                                 self.canvas.GetClientSize()[1] / 2
            offsetx = (zoom_point_x * scale_change)
            offsety = (zoom_point_y * scale_change)
        return offsetx, offsety, zoom_point_x, zoom_point_y

    def _do_resize_virtual_canvas_tofit_bounds(self, bounds: Tuple, scroll_offsets: Tuple):
        """Does the actual resizing of the virtual canvas and setting the scrollbars.

        The SetScrollbars() call does the virtual canvas resizing using bounds_width, bounds_height
        so no need to call canvas.SetVirtualSize() - you can do either.

        The oldscrollx, oldscrolly are the elevator scroll positions which we preserve. If we
        are zooming in which case the scroll positions are adjusted by 'scroll_offsets' to keep
        the mouse or selected shape in view - the 'scroll_offsets' were tricky to figure out.
        """
        bounds_width, bounds_height = bounds

        oldscrollx = self.canvas.GetScrollPos(wx.HORIZONTAL)
        oldscrolly = self.canvas.GetScrollPos(wx.VERTICAL)

        if scroll_offsets:
            offsetx, offsety = scroll_offsets
            oldscrollx += offsetx
            oldscrolly += offsety

        # https://wxpython.org/Phoenix/docs/html/wx.Scrolled.html#wx.Scrolled.SetScrollbars
        self.canvas.SetScrollbars(
            1, 1,  # each scroll unit is 1 pixel, meaning scroll units match client coord units
            int(bounds_width), int(bounds_height),  # new virtual size
            int(oldscrollx), int(oldscrolly),  # new scroll positions
            noRefresh=True
        )
        if not PRO_EDITION:
            self.canvas.OnSize(evt=None)  # fix for GTK - will create a larger _buffer

        # Cache is different to last bounds value - cannot combine these concepts
        self.allshapes_bounds_last = bounds
        self.allshapes_bounds_cached = None

    def calc_allshapes_bounds(self):
        """
        Calculates the maxx and maxy for all the shapes on the canvas.
        """
        if self.allshapes_bounds_cached:
            # print ".",
            return self.allshapes_bounds_cached

        ALLSHAPES_BOUNDS_MARGIN = 20
        maxx = maxy = 0
        for shape in self.canvas.umlboxshapes:
            width, height = shape.GetBoundingBoxMax()
            right = shape.GetX() + width / 2
            bottom = shape.GetY() + height / 2
            maxx = max(right, maxx)
            maxy = max(bottom, maxy)
        # print "!",
        self.allshapes_bounds_cached = (
            maxx + ALLSHAPES_BOUNDS_MARGIN,
            maxy + ALLSHAPES_BOUNDS_MARGIN,
        )
        return self.allshapes_bounds_cached


"""
Notes:

Purpose of shrinkage_leeway
---------------------------
Relax the compacting rule so that canvas virtual size may be shrinkage_leeway%
bigger than the "all shapes bounds" without it being trimmed/compacted down. The
purpose of this is to relax the rules and not have it so strict - after all it
doesn't hurt to have a slightly larger workspace - better than a trim workspace
jumping/flickering around all the time. Plus if you manually drag resize the
frame it will trim perfectly.

How canvas virtual size stretches
---------------------------------
As you resize the canvas size / frame, the canvas virtual size stays the same as
what you set it to using SetScrollbars() - up until the point at which the
scrollbars exhaust themselves and disappear - which means the that you have
finally made frame == virtualsize. After which point virtual size auto-grows as
the frame continues to grow. If you shrink the frame again, then virtualsize
will reduce until it hits the old original value of virtualsize set by
SetScrollbars(). If you continue to reduce the frame then the scrollbars appear,
but the virtualsize remains the same.

When bounds become dirty
-------------------------
After a programmatic change of "all shapes bounds" e.g. via mega_refresh
or when move a node via the mouse

"all shapes bounds" area doesn't change when resizing a frame, thus the
bounds is not dirty
        
Repeated calls from frame resize event
--------------------------------------
Note: repeated calls from frame resize event shouldn't be a problem because
current "all shapes bounds" == self.allshapes_bounds_last due to our
recording of allshapes_bounds_last every time it is set by us. If nothing has
changed then we don't do anything. Thus repeated hammering from resize event is
protected against.

Additionally we cache the calls to calc_allshapes_bounds in
self.allshapes_bounds_cached to avoid constant recalc. Typically the first
resize event might cause the SetScrollbars() call and then subsequent calls do
nothing.

Also since shrinkage_leeway is 0 when called from a frame resize event, if the
virtual canvas is any bigger than the bounds of the shapes - even 1% bigger -
then trim the virtual canvas. Normally the tolerance for shrinking has a leeway
of 20-40% or so.
        


"""

# print "bounds", self.calc_allshapes_bounds()
# print "canvas.GetVirtualSize()", self.GetVirtualSize()

# print "canvas.GetSize()", self.GetSize()
# print "frame.GetVirtualSize()", self.frame.GetVirtualSize()
# print "frame.GetSize()", self.frame.GetSize()
# print "frame.GetClientSize()", self.frame.GetClientSize()

# print "bounds now", self.calc_allshapes_bounds(), self.allshapes_bounds_cached
# print "canvas.GetVirtualSize()", self.GetVirtualSize()
