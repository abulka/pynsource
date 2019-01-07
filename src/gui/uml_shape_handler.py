# Event handler

import wx
import wx.lib.ogl as ogl
from coord_utils import setpos, getpos
from common.architecture_support import *

class UmlShapeHandler(ogl.ShapeEvtHandler):
    def __init__(self, log, frame, shapecanvas):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.frame = frame              # these are arbitrary initialisations
        self.shapecanvas = shapecanvas  # these are arbitrary initialisations
        self.app = None  # assigned later by event sent to controller from uml canvas when creating new shapes

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        x, y = getpos(shape)
        width, height = shape.GetBoundingBoxMax()
        
        msg = ""
        node = getattr(shape, "node", None)
        if node:
            colour_index = getattr(node, "colour_index", None)
            if colour_index <> None:
                msg += "colour_index %d" % colour_index
            
        self.frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d) %s" % (x, y, width, height, msg))

    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        self._SelectNodeNow(x, y, keys, attachment)

    def _SelectNodeNow(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        shape.GetCanvas().SelectNodeNow(shape)
        self.UpdateStatusBar(shape)

    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        oldpos = getpos(shape)
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment) # super
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        newpos = getpos(shape)
        try:
            #print shape.node.id, "moved from", oldpos, "to", newpos
            # Adjust the GraphNode to match the shape x,y
            shape.node.left, shape.node.top = newpos
        except:
            print "no node model attached to this shape!"
            
        self.UpdateStatusBar(shape)
        
        shape.GetCanvas().canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=True)

        # Invoke overlap removal (unless hold down shift key)
        KEY_SHIFT = 1
        if keys & KEY_SHIFT:
            #shape.GetCanvas().mega_refresh()   # do we need this?  did quite well without it before
            pass
        else:
            canvas = shape.GetCanvas()
            if canvas.remove_overlaps():
                canvas.mega_refresh()

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        shape = self.GetShape()

        # super        
        ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
        
        width, height = shape.GetBoundingBoxMin()
        if hasattr(shape, 'node'):
            #print shape.node, "resized to", width, height
            #print shape.node.id, shape.node.left, shape.node.top, "resized to", width, height
            
            # Adjust the GraphNode to match the shape x,y
            shape.node.width, shape.node.height = width, height
            shape.node.left, shape.node.top = getpos(shape)
        
        self.UpdateStatusBar(self.GetShape())

        canvas = shape.GetCanvas()
        if canvas.remove_overlaps():
            canvas.mega_refresh()
        
    def OnEndSize(self, width, height):
        #print "OnEndSize", width, height
        pass

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        
        self.UpdateStatusBar(shape)
        
        if "wxMac" in wx.PlatformInfo:      # Definitely seem to need this on Mac to avoid ghost lines being left after a move
            shape.GetCanvas().Refresh(False) 


    def OnRightClick(self, x, y, keys, attachment):
        self._SelectNodeNow(x, y, keys, attachment)
        #self.log.WriteText("%s\n" % self.GetShape())

        self.popupmenu = wx.Menu()
        
        def MakeMenuItem(parent_menu, msg, method):
            """
            Not sure why but passing item is needed to Bind. Not to find the
            menu item later, but to avoid crashes? try two right click deletes
            followed by main menu edit/delete. Official Bind 3rd parameter DOCO:
            menu source - Sometimes the event originates from a different window
            than self, but you still want to catch it in self. (For example, a
            button event delivered to a frame.) By passing the source of the
            event, the event handling system is able to differentiate between
            the same event type from different controls. 
            """
            item = parent_menu.Append(wx.NewId(), msg)
            self.frame.Bind(wx.EVT_MENU, method, item)
            
        MakeMenuItem(self.popupmenu, "Properties...", self.NodeProperties)
        self.popupmenu.AppendSeparator()

        menu_sub = wx.Menu()
        MakeMenuItem(menu_sub, "Begin - Remember selected class as FROM node (for drawing lines)\tq", self.OnDrawBegin)  # Note: unlike proper toolbar menus, these shortcut keys don't work - you need to add onKeyChar() interceptions in umlcanvas.py
        MakeMenuItem(menu_sub, "End - Draw Line TO selected class (composition)\tw", self.OnDrawEnd1)
        MakeMenuItem(menu_sub, "End - Draw Line TO selected class (generalisation)\te", self.OnDrawEnd2)
        self.popupmenu.AppendMenu(wx.NewId(), "Draw Line", menu_sub)

        if self.GetShape().__class__.__name__ == 'BitmapShapeResizable':
            self.popupmenu.AppendSeparator()
            MakeMenuItem(self.popupmenu, "Reset Image Size", self.OnResetImageSize)
        
        self.popupmenu.AppendSeparator()
        MakeMenuItem(self.popupmenu, "Delete\tDel", self.RightClickDeleteNode)
        self.popupmenu.AppendSeparator()
        MakeMenuItem(self.popupmenu, "Cancel", self.OnPopupMenuCancel)
        
        self.frame.PopupMenu(self.popupmenu, wx.Point(x,y))

    def RightClickDeleteNode(self, event):
        self.app.run.CmdNodeDelete(self.GetShape())

    def OnLeftDoubleClick(self, x, y, keys, attachment):
        node_edit_multi_purpose(self.GetShape(), self.app)

    def NodeProperties(self, event):
        node_edit_multi_purpose(self.GetShape(), self.app)

    def OnDrawBegin(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkFrom()

    def OnDrawEnd1(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type='composition')

    def OnDrawEnd2(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type='generalisation')

    def OnResetImageSize(self, event):
        shape = self.GetShape()
        shape.ResetSize()
        #shape.GetCanvas().Refresh(False)   # don't seem to need since SelectNodeNow() might be doing it for us
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
    else:
        app.run.CmdEditComment(shape)
