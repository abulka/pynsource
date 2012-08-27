# Event handler

import wx
import wx.lib.ogl as ogl
from coord_utils import setpos, getpos

import sys
if ".." not in sys.path: sys.path.append("..")
from architecture_support import *

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
            #shape.GetCanvas().stateofthenation()   # do we need this?  did quite well without it before
            pass
        else:
            canvas = shape.GetCanvas()
            if canvas.remove_overlaps():
                canvas.stateofthenation()

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
            canvas.stateofthenation()
        
    def OnEndSize(self, width, height):
        #print "OnEndSize", width, height
        pass

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        #self.UpdateStatusBar(shape)
        #if "wxMac" in wx.PlatformInfo:
        #    shape.GetCanvas().Refresh(False) 

    def OnPopupItemSelected(self, event):
        item = self.popupmenu.FindItemById(event.GetId()) 
        text = item.GetText() 
        if text == "Delete\tDel":
            self.RightClickDeleteNode()
        elif text == "Properties...":
            self.NodeProperties()
        elif text == "Begin - Draw Line from this class\tq":
            self.GetShape().GetCanvas().NewEdgeMarkFrom()
        elif text == "End - Draw Line to this class (composition)\tw":
            self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type='composition')
        elif text == "End - Draw Line to this class (generalisation)\tW":
            self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type='generalisation')
        elif text == "Reset Image Size":
            shape = self.GetShape()
            shape.ResetSize()
            #shape.GetCanvas().Refresh(False)   # don't seem to need since SelectNodeNow() might be doing it for us
            shape.GetCanvas().SelectNodeNow(shape)
            self.UpdateStatusBar(shape)

    def OnRightClick(self, x, y, keys, attachment):
        self._SelectNodeNow(x, y, keys, attachment)

        #self.log.WriteText("%s\n" % self.GetShape())
        self.popupmenu = wx.Menu()     # Creating a menu
        
        def MakeMenuItem(menu, msg):
            item = menu.Append(wx.NewId(), msg)
            self.frame.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)  # Not sure why but passing item is needed.  Not to find the menu item later, but to avoid crashes?  try two right click deletes followed by main menu edit/delete.  Official Bind 3rd parameter DOCO:  menu source - Sometimes the event originates from a different window than self, but you still want to catch it in self. (For example, a button event delivered to a frame.) By passing the source of the event, the event handling system is able to differentiate between the same event type from different controls.
            
        MakeMenuItem(self.popupmenu, "Properties...")
        self.popupmenu.AppendSeparator()

        menu_sub = wx.Menu()
        MakeMenuItem(menu_sub, "Begin - Draw Line from this class\tq")
        MakeMenuItem(menu_sub, "End - Draw Line to this class (composition)\tw")
        MakeMenuItem(menu_sub, "End - Draw Line to this class (generalisation)\tW")
        self.popupmenu.AppendMenu(wx.NewId(), "Draw Line", menu_sub)

        if self.GetShape().__class__.__name__ == 'BitmapShapeResizable':
            self.popupmenu.AppendSeparator()
            MakeMenuItem(self.popupmenu, "Reset Image Size")
        
        self.popupmenu.AppendSeparator()
        MakeMenuItem(self.popupmenu, "Delete\tDel")
        self.popupmenu.AppendSeparator()
        MakeMenuItem(self.popupmenu, "Cancel")
        
        self.frame.PopupMenu(self.popupmenu, wx.Point(x,y))

    def RightClickDeleteNode(self):
        self.app.run.CmdNodeDelete(self.GetShape())

    def OnLeftDoubleClick(self, x, y, keys, attachment):
        self.app.run.CmdEditClass(self.GetShape())

    def NodeProperties(self):
        self.app.run.CmdEditClass(self.GetShape())

