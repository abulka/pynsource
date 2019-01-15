# Event handler

import wx
import wx.lib.ogl as ogl
from .coord_utils import setpos, getpos
from common.architecture_support import *
from gui.uml_shapes import CommentShape
from typing import List, Set, Dict, Tuple, Optional
from gui.shape_menu import ShapeMenu
from gui.node_edit_multi_purpose import node_edit_multi_purpose

class UmlShapeHandler(ogl.ShapeEvtHandler):
    def __init__(self, log, frame, shapecanvas):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.frame = frame  # these are arbitrary initialisations
        self.umlcanvas = shapecanvas  # these are arbitrary initialisations
        self.app = (
            None
        )  # assigned later by event sent to controller from uml canvas when creating new shapes

        self.shapemenu_mgr = ShapeMenu(self.frame, self)

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

        self.frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d) %s" % (x, y, width, height, msg))

    def OnLeftClick(self, x, y, keys=0, attachment=0):
        self._SelectNodeNow(x, y, keys, attachment)

    def _SelectNodeNow(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        shape.GetCanvas().SelectNodeNow(shape)
        self.UpdateStatusBar(shape)
        self.focus_shape()

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        oldpos = getpos(shape)
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)  # super
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        newpos = getpos(shape)
        try:
            # print shape.node.id, "moved from", oldpos, "to", newpos
            # Adjust the GraphNode to match the shape x,y
            shape.node.left, shape.node.top = newpos
        except:
            print("no node model attached to this shape!")

        self.UpdateStatusBar(shape)

        shape.GetCanvas().canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=True)

        # Invoke overlap removal (unless hold down shift key)
        KEY_SHIFT = 1
        if keys & KEY_SHIFT:
            # shape.GetCanvas().mega_refresh()   # do we need this?  did quite well without it before
            pass
        else:
            canvas = shape.GetCanvas()
            if canvas.remove_overlaps():
                pass

        canvas.mega_refresh()

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

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)

        self.UpdateStatusBar(shape)

        if (
            "wxMac" in wx.PlatformInfo
        ):  # Definitely seem to need this on Mac to avoid ghost lines being left after a move
            shape.GetCanvas().Refresh(False)


    def focus_shape(self):
        """
        Called by both left and right click on a shape

        This is where we need to refresh the values in the central table

        This is where we need to bind accelerators to shape events just in case it was a
        left click and accelerator key pressed, thus no popup menu ever occurs.
        FUN FACT: Keyboard shortcuts in wxPython are actually menu events (i.e. wx.EVT_MENU), probably because the shortcuts are usually also a menu item.

        If it is a right click then we bind from the menu items again?  But how does that
        interact with the (non menu popup) first bindings?  Does the fact that menu items
        share ids nicely affect things?  Need to experiment a bit.

        what about unbinding when no shape is selected?  or when shape is deleted?
        well, we just cross our fingers the wxpython event handling does the right thing.

        """
        # Need to build accelerator table with only the entries that are relevant
        # and bind to the shape's handlers
        print("focus_shape")
        self.shapemenu_mgr.BuildPopupMenuItems()  # easy way, we simply don't popup the menu
        # accelerator table gets put in place - bonus
        # and the menu is ready to be displayed if we right click - bonus

    def OnRightClick(self, x, y, keys, attachment):
        """
        Popup menu when r.click on shape.

        Note: unlike proper toolbar menus, these shortcut keys don't work - you need to add
        onKeyChar() interceptions in umlcanvas.py
        Or we use a global accelerator table on the frame.  <-- 2019 current approach.

        Args:
            x:
            y:
            keys:
            attachment:

        Returns:

        """
        self._SelectNodeNow(x, y, keys, attachment)
        # self.log.WriteText("%s\n" % self.GetShape())

        # self.BuildPopupMenuItems()  should already be built cos of the focus_shape() call
        self.frame.PopupMenu(self.shapemenu_mgr.popupmenu, wx.Point(x, y))


        # # MGR attempt
        # pm = self.umlcanvas.shape_popup_menu_mgr
        # pmm.clear()
        # pmm.add_properties()
        # self.frame.PopupMenu(pmm.popupmenu, wx.Point(x, y))
        #
        # return


        # # EXPERIMENT
        #
        # self.accel_entries : List[wx.AcceleratorEntry] = []
        #
        # if self.popupmenu:  # already exists - don't build it again
        #     print("already exists")
        # else:
        #     print("creating popup")
        #     self.popupmenu = wx.Menu()  # This is the popup menu to which we attach menu items
        #     item : wx.MenuItem = self.popupmenu.Append(wx.ID_ANY, "Do Z")
        #     self.frame.Bind(wx.EVT_MENU, self.doZ, item)
        #
        #     item.Enable(False)  # hmm, accelerator still fires :-(
        #
        #     entry = wx.AcceleratorEntry()
        #     # entry.Set(wx.ACCEL_NORMAL, ord('Z'), item.GetId())
        #     entry.Set(wx.ACCEL_CTRL, ord('Z'), item.GetId())
        #     self.accel_entries.append(entry)
        #
        #     accel_tbl = wx.AcceleratorTable(self.accel_entries)
        #     self.frame.SetAcceleratorTable(accel_tbl)
        #     print("self.accel_entries", self.accel_entries)
        #
        # self.frame.PopupMenu(self.popupmenu, wx.Point(x, y))
        #
        #
        # return




    # def TestUpdateUI(self, evt):
    #     import time
    #     text = time.ctime()
    #     # How to get to the target of the event e.g. the specific menu item - AH you need to
    #     # bind a different handler to each menuitem,
    #     # Or you can check evt.GetId()
    #
    #     # evt.SetText(text)  # gosh this sets the text of the menuitem!
    #
    #     evt.Enable(False)  # Accelerator still fires !!??????
    #
    #     # print("TestUpdateUI", text, evt.EventObject)
    #
    # def doZ(self, event):
    #     print("doZ")

    # def _update_line_state(self):
    #     set_item_state(MENU_ID_BEGIN_LINE, self.GetShape().GetCanvas().new_edge_from == None)

    def OnLeftDoubleClick(self, x, y, keys, attachment):
        node_edit_multi_purpose(self.GetShape(), self.app)


