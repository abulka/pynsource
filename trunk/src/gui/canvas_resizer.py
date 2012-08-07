# CanvasResizer looks after canvas resizing and virtual size of canvas

from coord_utils import percent_change

import wx
import wx.lib.ogl as ogl

class CanvasResizer(object):
    def __init__(self, canvas):
        self.canvas = canvas
        
        self.allshapes_bounds_cached = None
        self.allshapes_bounds_last = None
    
    def canvas_too_small(self):
        MIN_SENSIBLE_CANVAS_SIZE = 200
        width, height = self.canvas.GetSize()
        return width < MIN_SENSIBLE_CANVAS_SIZE or height < MIN_SENSIBLE_CANVAS_SIZE
        
    # UTILITY - called by OnResizeFrame, layout_and_position_shapes
    def frame_calibration(self):
        """
        Calibrate model / shape / layout coordinate mapping system to the
        visible physical window canvas size.
        """
        if self.canvas_too_small():
            return

        self.canvas.coordmapper.Recalibrate(self.canvas.frame.GetClientSize())  # passing self.GetVirtualSize() seems to spread the layout out too much

        #Tip2: Since the bounds of the shapes area doesn't change when resizing
        #a frame, we don't need to set the virtualsize of the canvas repeatedly.
        #But we do call this routine in case we can shrink the virtual area at
        #least once. Due to shrinkage_leeway being zero, if the
        #virtual canvas is any bigger than the bounds of the shapes - even 1%
        #bigger - then trim the virtual canvas. Normally the tolerance for
        #shrinking has a leeway of 20-40% or so.
        #

        self.resize_virtual_canvas_tofit_bounds(shrinkage_leeway=0, bounds_dirty=False)

        
    # UTILITY - used by 's' key, stateofthenation, frame_calibration, OnEndDragLeft
    def resize_virtual_canvas_tofit_bounds(self, shrinkage_leeway=40, bounds_dirty=False):
        """
        Set canvas virtual size to the bounds of all the shapes.
        You change virtual size by calling SetScrollbars()
        
        As you resize the frame, the canvas virtual size stays the same as what
        you set it to using SetScrollbars() - up until the point at which the
        scrollbars exhaust themselves and disappear - which means the that you
        have finally made frame == virtualsize. After which point virtual size
        auto-grows as the frame continues to grow. If you shrink the frame
        again, then virtualsize will reduce until it hits the old original value
        of virtualsize set by SetScrollbars(). If you continue to reduce the
        frame then the scrollbars appear, but the virtualsize remains the same.
        
        ALGORITHM:
        If its a programmatic change of bounds e.g. via stateofthenation:
            set canvas virtualsize to match bounds taking account % leeway when compacting
        elif is_frame_resize i.e. its a call from resize of frame event:
            if frame > bounds then must be in virtualsize autogrow mode and we should not attempt to alter virtualsize
            else: set canvas virtualsize to match bounds, not taking into account any % leeway.

        Note: repeated calls to frame resize shouldn't be a problem because
        canvas virtualsize should == bounds after the first time its done.
        Making frame smaller won't affect bounds or canvas virtualsize. Making
        frame bigger ditto. Making frame bigger than bounds will result in
        nothing happening cos we do nothing in "autogrow mode".
        """
        if bounds_dirty:
            self.allshapes_bounds_cached = None
            
        if self.allshapes_bounds_last == self.GetBoundsAllShapes():
            print "nochange",
            return
        #print "bounds", self.GetBoundsAllShapes()
        #print "canvas.GetVirtualSize()", self.GetVirtualSize()

        #print "canvas.GetSize()", self.GetSize()
        #print "frame.GetVirtualSize()", self.frame.GetVirtualSize()
        #print "frame.GetSize()", self.frame.GetSize()
        #print "frame.GetClientSize()", self.frame.GetClientSize()

        bounds_width, bounds_height = self.GetBoundsAllShapes()
        virt_width, virt_height = self.canvas.GetVirtualSize()
        frame_width, frame_height = self.canvas.GetClientSize()
        
        """
        Rules: virtual size must be >= bounds
               virtual size should be trimmed down to bounds where possible
        """
        need_more_virtual_room = bounds_width > virt_width or bounds_height > virt_height
        need_to_compact = (bounds_width < virt_width or bounds_height < virt_height)
        
        if need_to_compact and shrinkage_leeway > 0:
            """
            Relax the compacting rule so that canvas virtual size may be
            shrinkage_leeway% bigger than the bounds without it
            being trimmed/compacted down. The purpose of this is to relax the
            rules and not have it so strict - after all it doesn't hurt to have
            a slightly larger workspace - better than a trim workspace
            jumping/flickering around all the time. Plus if you manually drag
            resize the frame it will trim perfectly. """
            will_compact = \
                (percent_change(bounds_width, virt_width) > shrinkage_leeway or \
                 percent_change(bounds_height, virt_height) > shrinkage_leeway)
        else:
            will_compact = need_to_compact
            
        print need_more_virtual_room, need_to_compact,
        if need_to_compact and not will_compact:
            print "(compact pending)",
                    
        if need_more_virtual_room or will_compact:
            print "(action)"
            self._do_resize_virtual_canvas_tofit_bounds((bounds_width, bounds_height))
        else:
            print "(no action)"
    
    def _do_resize_virtual_canvas_tofit_bounds(self, bounds):
        bounds_width, bounds_height = bounds

        oldscrollx = self.canvas.GetScrollPos(wx.HORIZONTAL)
        oldscrolly = self.canvas.GetScrollPos(wx.VERTICAL)

        print "Setting virtual size to %d,%d" % (bounds_width, bounds_height)

        self.canvas.SetScrollbars(1, 1, bounds_width, bounds_height, oldscrollx, oldscrolly, noRefresh = True)
        
        # Cache is different to last bounds value - cannot combine these concepts
        self.allshapes_bounds_last = bounds
        self.allshapes_bounds_cached = None

        #print "bounds now", self.GetBoundsAllShapes(), self.allshapes_bounds_cached
        #print "canvas.GetVirtualSize()", self.GetVirtualSize()
        
    def GetBoundsAllShapes(self):
        """
        Calculates the maxx and maxy for all the shapes on the canvas.
        """
        if self.allshapes_bounds_cached:
            print ".",
            return self.allshapes_bounds_cached
        
        ALLSHAPES_BOUNDS_MARGIN = 20
        maxx = maxy = 0
        for shape in self.canvas.umlboxshapes:
            width, height = shape.GetBoundingBoxMax()
            right = shape.GetX() + width/2
            bottom = shape.GetY() + height/2
            maxx = max(right, maxx)
            maxy = max(bottom, maxy)
        print "!",
        self.allshapes_bounds_cached= (maxx + ALLSHAPES_BOUNDS_MARGIN,
                                        maxy + ALLSHAPES_BOUNDS_MARGIN)
        return self.allshapes_bounds_cached

