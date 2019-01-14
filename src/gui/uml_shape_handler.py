# Event handler

import wx
import wx.lib.ogl as ogl
from .coord_utils import setpos, getpos
from common.architecture_support import *
from gui.uml_shapes import CommentShape
from view.display_model import GraphNode, UmlNode, CommentNode
from typing import List, Set, Dict, Tuple, Optional


class UmlShapeHandler(ogl.ShapeEvtHandler):
    def __init__(self, log, frame, shapecanvas):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.frame = frame  # these are arbitrary initialisations
        self.umlcanvas = shapecanvas  # these are arbitrary initialisations
        self.app = (
            None
        )  # assigned later by event sent to controller from uml canvas when creating new shapes

        self.popupmenu = None   # ANDY HACK

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

    def OnRightClick(self, x, y, keys, attachment):
        """
        Popup menu when r.click on shape.

        Note: unlike proper toolbar menus, these shortcut keys don't work - you need to add
        onKeyChar() interceptions in umlcanvas.py

        Args:
            x:
            y:
            keys:
            attachment:

        Returns:

        """
        self._SelectNodeNow(x, y, keys, attachment)
        # self.log.WriteText("%s\n" % self.GetShape())





        # EXPERIMENT

        self.accel_entries : List[wx.AcceleratorEntry] = []

        if self.popupmenu:  # already exists - don't build it again
            print("already exists")
        else:
            print("creating popup")
            self.popupmenu = wx.Menu()  # This is the popup menu to which we attach menu items
            item : wx.MenuItem = self.popupmenu.Append(wx.ID_ANY, "Do Z")
            self.frame.Bind(wx.EVT_MENU, self.doZ, item)

            item.Enable(False)  # hmm, accelerator still fires :-(

            entry = wx.AcceleratorEntry()
            # entry.Set(wx.ACCEL_NORMAL, ord('Z'), item.GetId())
            entry.Set(wx.ACCEL_CTRL, ord('Z'), item.GetId())
            self.accel_entries.append(entry)

            accel_tbl = wx.AcceleratorTable(self.accel_entries)
            self.frame.SetAcceleratorTable(accel_tbl)
            print("self.accel_entries", self.accel_entries)

        self.frame.PopupMenu(self.popupmenu, wx.Point(x, y))


        return


        self.popupmenu = wx.Menu()  # This is the popup menu to which we attach menu items
        self.submenu = wx.Menu()  # This is the sub menu within the popupmenu

        self.accel_entries : List[wx.AcceleratorEntry] = []

        def add_menuitem(item_text, method, submenu=False, key_code=None):
            if submenu:
                to_menu = self.submenu
            else:
                to_menu = self.popupmenu
            item : wx.MenuItem = to_menu.Append(wx.ID_ANY, item_text)
            self.frame.Bind(wx.EVT_MENU, method, item)
            self.frame.Bind(wx.EVT_UPDATE_UI, self.TestUpdateUI, item)

            if key_code:
                # https://wxpython.org/Phoenix/docs/html/wx.AcceleratorEntryFlags.enumeration.html#wx-acceleratorentryflags
                entry = wx.AcceleratorEntry()
                entry.Set(wx.ACCEL_NORMAL, key_code, item.GetId())
                self.accel_entries.append(entry)

            return item

        def add_submenu_to_popup():
            self.popupmenu.Append(wx.ID_ANY, "Draw Line", self.submenu)

        def add_separator():
            self.popupmenu.AppendSeparator()

        def add_properties():
            add_menuitem("Properties...", self.OnNodeProperties)

        def add_from():
            item : wx.MenuItem = add_menuitem(
                "Begin - Remember selected class as FROM node (for drawing lines)\tq",
                self.OnDrawBegin,
                submenu=True,
                key_code=ord('Z')
            )
            # item.Enable(False)  # hmm, accelerator still fires :-(

        def add_from_cancel():
            add_menuitem(
                "Cancel Line Begin\tx",
                self.OnCancelDrawBegin,
                submenu=True
            )

        def add_association_edge():
            add_menuitem(
                "End - Draw Line TO selected comment/class (association - dashed)\ta",
                self.OnDrawEnd3,
                submenu = True
            )

        def add_generalise_composition_edges():
            add_menuitem(
                "End - Draw Line TO selected class (composition)\tw",
                self.OnDrawEnd1,
                submenu=True
            )
            add_menuitem(
                "End - Draw Line TO selected class (generalisation)\te",
                self.OnDrawEnd2,
                submenu = True
            )

        def add_reset_image_size():
            add_menuitem("Reset Image Size", self.OnResetImageSize)

        def add_delete():
            add_menuitem("Delete\tDel", self.OnRightClickDeleteNode)

        def add_cancel():
            add_menuitem("Cancel", self.OnPopupMenuCancel)

        shape = self.GetShape()
        from_node : GraphNode = self.umlcanvas.new_edge_from
        is_bitmap = shape.__class__.__name__ == "BitmapShapeResizable"
        is_comment = isinstance(shape.node, CommentNode)
        is_umlclass = isinstance(shape.node, UmlNode)
        assert not is_umlclass == (is_comment or is_bitmap)
        started_connecting = from_node != None
        from_is_comment = isinstance(from_node, CommentNode)

        if is_umlclass or is_comment:
            add_properties()
            add_separator()
            if not from_node:
                add_from()

        if is_umlclass:
            if started_connecting:
                add_association_edge()
                if not from_is_comment:
                    add_generalise_composition_edges()
            else:
                pass  # don't offer 'to' menu choices cos haven't started connecting yet
        elif is_comment:
            if started_connecting:
                add_association_edge()
            else:
                pass  # don't offer 'to' menu choices cos haven't started connecting yet
        elif is_bitmap:
            add_reset_image_size()
        else:
            raise RuntimeError("Right click on unknown shape")

        if is_umlclass or is_comment:
            if from_node:
                add_from_cancel()

        add_submenu_to_popup()

        add_separator()
        add_delete()
        add_separator()
        add_cancel()

        self.frame.PopupMenu(self.popupmenu, wx.Point(x, y))

        accel_tbl = wx.AcceleratorTable(self.accel_entries)
        self.frame.SetAcceleratorTable(accel_tbl)

        # wx.GetApp().Bind(wx.EVT_UPDATE_UI, self.TestUpdateUI, id=506)
        # self.frame.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        #
        # def doBind(item, handler, updateUI=None):
        #     self.Bind(wx.EVT_TOOL, handler, item)
        #     if updateUI is not None:
        #         self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        #
        # doBind(tbar.AddTool(-1, images._rt_bold.GetBitmap(), isToggle=True, shortHelpString="Bold"),
        #        self.OnBold,
        #        self.OnUpdateBold)

    def TestUpdateUI(self, evt):
        import time
        text = time.ctime()
        # How to get to the target of the event e.g. the specific menu item - AH you need to
        # bind a different handler to each menuitem,
        # Or you can check evt.GetId()

        # evt.SetText(text)  # gosh this sets the text of the menuitem!

        evt.Enable(False)  # Accelerator still fires !!??????

        # print("TestUpdateUI", text, evt.EventObject)

    def doZ(self, event):
        print("doZ")

    def OnRightClickDeleteNode(self, event):
        self.app.run.CmdNodeDelete(self.GetShape())

    def OnLeftDoubleClick(self, x, y, keys, attachment):
        node_edit_multi_purpose(self.GetShape(), self.app)

    def OnNodeProperties(self, event):
        node_edit_multi_purpose(self.GetShape(), self.app)

    def OnDrawBegin(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkFrom()

    def OnCancelDrawBegin(self, event):
        self.GetShape().GetCanvas().new_edge_from = None

    def OnDrawEnd1(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type="composition")

    def OnDrawEnd2(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type="generalisation")

    def OnDrawEnd3(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type="association")

    def OnResetImageSize(self, event):
        shape = self.GetShape()
        shape.ResetSize()
        # shape.GetCanvas().Refresh(False)   # don't seem to need since SelectNodeNow() might be doing it for us
        shape.GetCanvas().SelectNodeNow(shape)
        self.UpdateStatusBar(shape)

    def OnPopupMenuCancel(self, event):
        pass


def node_edit_multi_purpose(shape, app):
    """
    Edit a uml class node or a comment node

    Main menu calls this from pynsourcegui or
    Or uml shape handler (above) calls this when right click on a shape

    Args:
        shape:
        app:

    Returns: -

    """
    # node is a regular node, its the node.shape that is different for a comment
    from gui.uml_shapes import DividedShape

    if isinstance(shape, DividedShape):
        app.run.CmdEditUmlClass(shape)
    elif isinstance(shape, CommentShape):
        app.run.CmdEditComment(shape)
    else:
        print("Unknown Shape", shape)
