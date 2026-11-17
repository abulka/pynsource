import wx
import wxdiagram

from .coord_utils import setpos, getpos
from gui.shape_menu_mgr import ShapeMenuMgr
from gui.node_edit_multi_purpose import node_edit_multi_purpose
from typing import List, Set, Dict, Tuple, Optional


class UmlShapeHandler(wxdiagram.ShapeEvtHandler):

    def __init__(self, log, frame, shapecanvas):
        wxdiagram.ShapeEvtHandler.__init__(self)
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
        canvas = self.GetCanvas()
        shift = event is not None and (
            getattr(event, "ShiftDown", lambda: False)()
            or getattr(event, "ControlDown", lambda: False)()
            or getattr(event, "CmdDown", lambda: False)()
        )
        if shape.Selected() and (shift or len(canvas.getSelectedShapes()) > 1):
            # Shift-click/up is additive, and clicking one shape of an existing
            # multi-selection must not collapse it before/after a group drag.
            canvas.UpdateStatusBar(shape=shape)
            self.focus_shape()
            return
        canvas.SelectNodeNow(shape)  # usually no need, but need for r.click
        canvas.UpdateStatusBar(shape=shape)
        self.focus_shape()

    def _post_move_or_resize(self, event, shape):
        canvas = shape.GetCanvas()
        shift = True if event and event.ShiftDown() else False

        canvas.UpdateStatusBar(shape)  # was on shape event handler, now on canvas
        suspended = getattr(canvas, "_suspend_overlap_removal", False)
        canvas.update_virtual_size()
        # Overlap removal is per-shape normally, but for a multi-shape drag the
        # canvas runs it once after every node has been updated.
        if not shift and not suspended:
            canvas.remove_overlaps()
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
        # wxdiagram.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)

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

