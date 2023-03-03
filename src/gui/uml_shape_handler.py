import wx
from gui.settings import PRO_EDITION, NATIVE_LINES_OGL_LIKE, LOCAL_OGL
if PRO_EDITION:
    import ogl2 as ogl
else:
    if LOCAL_OGL:
        import ogl
    else:
        import wx.lib.ogl as ogl

from .coord_utils import setpos, getpos, ZoomInfo
from gui.shape_menu_mgr import ShapeMenuMgr
from gui.node_edit_multi_purpose import node_edit_multi_purpose
from typing import List, Set, Dict, Tuple, Optional


class UmlShapeHandlerOglTwo(ogl.ShapeEvtHandler):

    def __init__(self, log, frame, shapecanvas):
        assert PRO_EDITION
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.frame = frame  # these are arbitrary initialisations
        self.umlcanvas = shapecanvas  # these are arbitrary initialisations
        self.shapemenu_mgr = ShapeMenuMgr(self.frame, self)

        # app assigned later by event sent to controller from uml canvas when creating new shapes
        # self.app = None

    def OnLeftUp(self, event):
        self._SelectNodeNow(event)  # wx.ogl has x, y, keys, attachment

    def OnRightDown(self, event):
        # print("OnRightDown/OnRightClick")
        self._SelectNodeNow(event)
        self.umlcanvas.Refresh()  # seems to be needed

    def OnRightUp(self, event):
        """
        Popup menu when r.click on shape.
        The popupmenu is already built and waiting, due to the call to BuildPopupMenuItems()
        via focus_shape() call, which happens when left or right click on a shape.
        Don't specify a point at which to popup the menu, so that the scrolled window is taken into account
        """
        # print("OnRightUp")
        self.frame.PopupMenu(self.shapemenu_mgr.popupmenu)  # , wx.Point(x, y))

    def OnLeftDClick(self, event):
        node_edit_multi_purpose(self, self.umlcanvas.app)

    def focus_shape(self):
        """
        Called by both left and right click on a shape
        We build both a ready to go but dormant popupmenu and update the main frame's accelerator
        table with only the entries that are relevant to this shape.
        """
        self.shapemenu_mgr.BuildPopupMenuItems()

    def _SelectNodeNow(self, event):
        # print("_SelectNodeNow", self)
        shape = self
        self.GetCanvas().SelectNodeNow(shape)  # usually no need, but need for r.click
        self.GetCanvas().UpdateStatusBar(shape=self)
        self.focus_shape()

    def _post_move_or_resize(self, event, shape):
        canvas = shape.GetCanvas()
        shift = True if event and event.ShiftDown() else False

        canvas.UpdateStatusBar(shape)  # was on shape event handler, now on canvas
        if not shift:
            canvas.remove_overlaps()
        canvas.canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=True,
                                                                 zoom_info=ZoomInfo(
                                                                     scale=canvas.scalex))
        # Invoke overlap removal (unless hold down shift key).
        # Also allows multiple shapes to be moved at the same time.
        if not shift:
            canvas.mega_refresh(auto_resize_canvas=False)  # False cos we just did the resize, above

    def OnEndDragLeft(self, event):
        shape = self
        # print("OnEndDragLeft COMMON", shape)
        newpos = getpos(shape)
        canvas = shape.GetCanvas()
        try:
            # print shape.node.id, "moved from", oldpos, "to", newpos
            # Adjust the GraphNode to match the shape x,y
            shape.node.left, shape.node.top = newpos
        except:
            print("Warning OnEndDragLeft: no node model attached to this shape?")

        self._post_move_or_resize(event, shape)

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        """Critical to know this:
            1. can resize underlying node for the shape, which means that layout
            and overlap detection will work properly
            2. the virtual canvas size can be adjusted to take into account the new shape size
        """
        # shape = self.GetShape()
        shape = self
        canvas = shape.GetCanvas()

        # super
        # ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)

        width, height = shape.GetBoundingBoxMin()
        if hasattr(shape, "node"):
            # print shape.node, "resized to", width, height
            # print shape.node.id, shape.node.left, shape.node.top, "resized to", width, height

            # Adjust the GraphNode to match the shape x,y
            shape.node.width, shape.node.height = width, height
            shape.node.left, shape.node.top = getpos(shape)

        event = None  # TODO can we get this info one day?
        self._post_move_or_resize(event, shape)

    def ping(self):
        print("pong")


class UmlShapeHandler(ogl.ShapeEvtHandler):
    """Traditional wx.ogl event handler which we wire up to each new shape, comment,
    line and image.  This event handler object not used by ogltwo mode, though"""
    def __init__(self, log, frame, shapecanvas):
        assert not PRO_EDITION
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.frame = frame  # these are arbitrary initialisations
        self.umlcanvas = shapecanvas  # these are arbitrary initialisations
        self.shapemenu_mgr = ShapeMenuMgr(self.frame, self)

        # # app assigned later by event sent to controller from uml canvas when creating new shapes
        # self.app = None  # TODO remove,  instead use self.umlcanvas.app

    def OnLeftClick(self, x, y, keys=0, attachment=0):
        self._SelectNodeNow(x, y, keys, attachment)

    def OnRightClick(self, x, y, keys, attachment):
        """
        Popup menu when r.click on shape.
        The popupmenu is already built and waiting, due to the call to BuildPopupMenuItems()
        via focus_shape() call, which happens when left or right click on a shape.
        Don't specify a point at which to popup the menu, so that the scrolled window is taken into account
        """
        print("UmlShapeHandlerOglTwo.OnRightClick")
        self._SelectNodeNow(x, y, keys, attachment)
        self.frame.PopupMenu(self.shapemenu_mgr.popupmenu)  # , wx.Point(x, y))

    def OnLeftDoubleClick(self, x, y, keys, attachment):
        node_edit_multi_purpose(self.GetShape(), self.umlcanvas.app)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        # print("uml shape got OnEndDragLeft")
        shape = self.GetShape()
        oldpos = getpos(shape)
        super().OnEndDragLeft(x, y, keys, attachment)  # super
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        newpos = getpos(shape)
        try:
            # print shape.node.id, "moved from", oldpos, "to", newpos
            # Adjust the GraphNode to match the shape x,y
            shape.node.left, shape.node.top = newpos
        except:
            print("Warning OnEndDragLeft: no node model attached to this shape?")

        self.UpdateStatusBar(shape)

        shape.GetCanvas().canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=True)
        canvas = shape.GetCanvas()

        # Invoke overlap removal (unless hold down shift key)
        KEY_SHIFT = 1
        if keys & KEY_SHIFT:
            # shape.GetCanvas().mega_refresh()   # do we need this?  did quite well without it before
            pass
        else:
            if canvas.remove_overlaps():
                pass

        canvas.mega_refresh()

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        self.UpdateStatusBar(shape)

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        shape = self.GetShape()

        # super
        ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)

        width, height = shape.GetBoundingBoxMin()
        if hasattr(shape, "node"):
            # print shape.node, "resized to", width, height
            # print shape.node.id, shape.node.left, shape.node.top, "resized to", width, height

            # Adjust the GraphNode to match the shape x,y
            shape.node.width, shape.node.height = width, height
            shape.node.left, shape.node.top = getpos(shape)

        self.UpdateStatusBar(self.GetShape())

        shape.GetCanvas().canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=True)

        canvas = shape.GetCanvas()
        if canvas.remove_overlaps():
            pass

        canvas.mega_refresh()

    def OnEndSize(self, width, height):
        # print "OnEndSize", width, height
        pass

    def focus_shape(self):
        """
        Called by both left and right click on a shape
        We build both a ready to go but dormant popupmenu and update the main frame's accelerator
        table with only the entries that are relevant to this shape.
        """
        self.shapemenu_mgr.BuildPopupMenuItems()

    def _SelectNodeNow(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        shape.GetCanvas().SelectNodeNow(shape)
        self.UpdateStatusBar(shape)
        self.focus_shape()

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        x, y = getpos(shape)
        width, height = shape.GetBoundingBoxMax()

        msg = ""
        node = getattr(shape, "node", None)
        if node:
            colour_index = getattr(node, "colour_index", None)
            if colour_index != None:
                msg += "colour_index %d" % colour_index
            msg += f"node: {node.left}, {node.top}"
        self.frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d) %s" % (x, y, width, height, msg))
