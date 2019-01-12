# Uml canvas

if __name__ == "__main__":
    import sys

    if ".." not in sys.path:
        sys.path.append("..")

import random

from generate_code.gen_java import PySourceAsJava

from view.display_model import DisplayModel
from view.display_model import CommentNode
from .uml_shapes import *
from .coord_utils import setpos, getpos, Move2
from layout.layout_basic import LayoutBasic
from layout.snapshots import GraphSnapshotMgr
from layout.layout_spring import GraphLayoutSpring
from layout.overlap_removal import OverlapRemoval
from layout.coordinate_mapper import CoordinateMapper
from .canvas_resizer import CanvasResizer
import wx
import wx.lib.ogl as ogl
from .uml_shape_handler import UmlShapeHandler
from common.architecture_support import *

from gui.repair_ogl import repairOGL

repairOGL()

ogl.Shape.Move2 = Move2

# class DiagramAndy(ogl.Diagram):
#
#     def RedrawORI(self, dc):
#         """Redraw the shapes in the diagram on the specified device context."""
#         if self._shapeList:
#             for object in self._shapeList:
#                 object.Draw(dc)
#
#     # def Redraw(self, dc):
#     #     """Redraw the shapes in the diagram on the specified device context."""
#     #     if self._shapeList:
#     #         for object in self._shapeList:
#     #             print "redrawing", object, object.GetX(), object.GetY()
#     #             object.Draw(dc)
#
# class ShapeCanvasAndy(ogl.ShapeCanvas):
#     """Custom ogl canvas for mucking around"""
#
#     def DrawORI(self):
#         """
#         Update the buffer with the background and redraw the full diagram.
#         """
#         dc = wx.MemoryDC(self._buffer)
#
#         dc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.BRUSHSTYLE_SOLID))
#         dc.Clear() # make sure you clear the bitmap!
#
#         if self.GetDiagram():
#             self.GetDiagram().Redraw(dc)
#         print("andy draw ori")
#
#     def OnPaintORI(self, evt):
#         """
#         The paint handler, uses :class:`BufferedPaintDC` to draw the
#         buffer to the screen.
#         """
#         dc = wx.PaintDC(self)
#         self.PrepareDC(dc)
#         dc.DrawBitmap(self._buffer, 0, 0)
#         print("andy onPaint ori")
#
#     def DrawNEW(self):
#         """
#         Update the buffer with the background and redraw the full diagram.
#         """
#         # dc = wx.MemoryDC(self._buffer)
#         #
#         # dc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.BRUSHSTYLE_SOLID))
#         # dc.Clear() # make sure you clear the bitmap!
#         #
#         # if self.GetDiagram():
#         #     self.GetDiagram().Redraw(dc)
#         # print("andy draw")
#
#     def OnPaintNEWNEW(self, evt):
#
#         dc = wx.PaintDC(self)
#         self.PrepareDC(dc)
#         dc.SetUserScale(self.scalex,self.scaley)
#         dc.DrawBitmap(self._buffer, 0, 0)
#
#         # # dc.BeginDrawing()
#         # # for item in self.diagram.shapes + self.nodes:
#         # #     item.draw(dc)
#         # dc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.BRUSHSTYLE_SOLID))
#         #
#         # dc.SetBrush(wx.CYAN_BRUSH)
#         # dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
#         #
#         # if self.GetDiagram():
#         #     self.GetDiagram().Redraw(dc)
#         #
#
#         # if self.GetDiagram()._shapeList:
#         #     for object in self.GetDiagram()._shapeList:
#         #         print "shapelist item", object
#         #         # object.Draw(dc)
#         #         dc.SetBrush(wx.RED_BRUSH)
#         #         dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
#         #
#         #         # last_x = object.GetX()
#         #         # last_y = object.GetY()
#         #         # last_width = object.GetWidth()
#         #         # last_height = object.GetHeight()
#         #         # dc.DrawRectangle(object.GetX(),object.GetY(),object.GetWidth(), object.GetHeight())
#
#         # Big
#         # dc.SetBrush(wx.CYAN_BRUSH)
#         # dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
#         # r = float(random.randint(200,400))
#         # print "random width is", r
#         # dc.DrawRectangle(320.0,320.0,r,400.0)
#
#         # dc.SetBrush(wx.YELLOW_BRUSH)
#         # rx = float(random.randint(250,450))
#         # ry = float(random.randint(50,150))
#         # rwidth = float(random.randint(50,150))
#         # rheight = float(random.randint(50,150))
#         # dc.DrawRectangle(rx, ry, rwidth, rheight)
#
#         # dc.SetBrush(wx.BLUE_BRUSH)
#         # dc.DrawRectangle(last_x, last_y, last_width, last_height)
#         # print "last", last_x, last_y, last_width, last_height
#
#         print("andy onPaint")
#
#         # dc.EndDrawing()
#
#     def OnMouseEvent(self, evt):
#         ogl.ShapeCanvas.OnMouseEvent(self, evt)
#         # print "mouse stuff..."  # Andy
#         self.Refresh()  # Andy

# class RectangleShapeAndy(ogl.RectangleShape):
#     # def Draw(self, dc):
#     #     ogl.RectangleShape.Draw(self, dc)
#     #     # print "RectangleShapeAndy Draw ...... ", self._visible
#     #
#     # def OnDraw(self, dc):
#     #     ogl.RectangleShape.OnDraw(self, dc)
#     #     # print "RectangleShapeAndy OnDraw ,,,, ", self._visible
#     #     #
#     #     # dc.SetBrush(wx.GREEN_BRUSH)
#     #     # dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
#     #     # dc.DrawRectangle(self.GetX(),self.GetY(),self.GetWidth(), self.GetHeight())
#
#     def OnDragLeft(self, draw, x, y, keys = 0, attachment = 0):
#         # ogl.RectangleShape.OnDragLeft(self, draw, x, y, keys = 0, attachment = 0)  # useless these days
#
#         # xx, yy = self._canvas.Snap(x, y)
#         # xx, yy = x, y  # if don't want snapping
#         #
#         # w, h = self.GetBoundingBoxMax()
#         # dc = wx.ClientDC(self.GetCanvas())  # wx.ClientDC doesn't work these days
#         # self.GetCanvas().PrepareDC(dc)
#         # self.Move(dc, xx, yy)
#
#         self.SetX(x)
#         self.SetY(y)
#
#     def OnBeginDragLeft(self, x, y, keys = 0, attachment = 0):
#         self.SetX(x)
#         self.SetY(y)
#
#     def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
#         self.SetX(x)
#         self.SetY(y)

# repairOGL()


class UmlCanvas(ogl.ShapeCanvas):
    # class UmlCanvas(ShapeCanvasAndy):

    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)
        # ShapeCanvasAndy.__init__(self, parent)  # ANDY HACK OGL
        # self.scalex =2.0  # ANDY HACK OGL
        # self.scaley =2.0  # ANDY HACK OGL

        self.observers = multicast()
        self.app = None  # assigned later by app boot

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE")

        self.SetDiagram(ogl.Diagram())
        # self.SetDiagram(DiagramAndy())  # ANDY HACK OGL
        self.GetDiagram().SetCanvas(self)

        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Bind(wx.EVT_CHAR, self.onKeyChar)

        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.font2 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)

        self.working = False
        self._kill_layout = (
            False
        )  # flag to communicate with layout engine.  aborting keypress in gui should set this to true

        self.new_edge_from = None  # the 'from' node when creating new edges manually via UI

        @property
        def kill_layout(self):
            return self._kill_layout

        @kill_layout.setter
        def kill_layout(self, value):
            self._kill_layout = value

    def InitSizeAndObjs(self):
        # Only call this once enclosing frame has been set up, so that get correct world coord dimensions

        self.canvas_resizer = CanvasResizer(canvas=self)

        # Don't assert canvas size sanity anymore as wxpython3 (phoenix) doesn't set canvas size
        # as quickly as wxpython2.8 does, even though frame has been sized and shown
        # with frame.SetSize(WINDOW_SIZE) and frame.Show(True)
        # In wxpython3 (phoenix) canvas stays at (20,20) despite the frame increasing in size to (1024,768)
        # but good ole wxpython2.8 does indeed change canvas size immediately to (1024,768)
        #
        # assert not self.canvas_resizer.canvas_too_small(), "InitSizeAndObjs being called too early - please set up enclosing frame size first"

        self.displaymodel = DisplayModel()
        self.layout = LayoutBasic(
            leftmargin=5,
            topmargin=5,
            verticalwhitespace=50,
            horizontalwhitespace=50,
            maxclassesperline=7,
        )
        self.snapshot_mgr = GraphSnapshotMgr(graph=self.displaymodel.graph, umlcanvas=self)
        self.coordmapper = CoordinateMapper(self.displaymodel.graph, self.GetSize())
        self.layouter = GraphLayoutSpring(self.displaymodel.graph, gui=self)
        self.overlap_remover = OverlapRemoval(self.displaymodel.graph, margin=50, gui=self)

    def AllToLayoutCoords(self):
        self.coordmapper.AllToLayoutCoords()

    def AllToWorldCoords(self):
        self.coordmapper.AllToWorldCoords()

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()  # http://www.wxpython.org/docs/api/wx.KeyEvent-class.html

        if self.working:
            event.Skip()
            return
        self.working = True

        if keycode == wx.WXK_ESCAPE:
            self.frame.SetStatusText("ESC key detected: Abort Layout")
            self.kill_layout = True

            # # HACK PLAY
            # shape = RectangleShapeAndy(50,50)
            # self.AddShape(shape)
            # shape.SetX(random.randint(40,80))
            # shape.SetY(random.randint(40,80))
            # shape.Show(True)
            # self.Refresh()
            # # END HACK PLAY

        if keycode == wx.WXK_RIGHT:
            self.app.run.CmdLayoutExpand(remove_overlaps=not event.ShiftDown())

        elif keycode == wx.WXK_LEFT:
            self.app.run.CmdLayoutContract(remove_overlaps=not event.ShiftDown())

        self.working = False
        event.Skip()

    def onKeyChar(self, event):
        """
        These are secret keycodes not exposed on the menu
        Normally shortcuts added on the menu work fine.
        """
        if event.GetKeyCode() >= 256:
            event.Skip()
            return
        if self.working:
            event.Skip()
            return
        self.working = True

        keycode = chr(event.GetKeyCode())
        print("keycode", keycode)

        if keycode in ["q", "Q"]:
            self.NewEdgeMarkFrom()

        elif keycode in ["w", "W"]:
            self.NewEdgeMarkTo(edge_type="composition")

        elif keycode in ["e", "E"]:
            self.NewEdgeMarkTo(edge_type="generalisation")

        elif keycode in ["a", "A"]:
            self.NewEdgeMarkTo(edge_type="association")

        elif keycode in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            todisplay = ord(keycode) - ord("1")
            self.snapshot_mgr.Restore(todisplay)

        elif keycode == "P":
            self.Refresh()

        elif keycode in ["d", "D"]:
            self.app.run.CmdDumpUmlWorkspace()

        elif keycode == "s":
            self.CmdTrimScrollbars()

        elif keycode == "G":  # and event.ShiftDown() and event.ControlDown():
            self.app.run.CmdBuildColourChartWorkspace()

        elif keycode in ["h", "H"]:
            self.app.run.CmdColourSequential(color_range_offset=(keycode == "H"))

        self.working = False

        # event.Skip()  # makes an annoying beep if enabled

    def CmdTrimScrollbars(self):
        self.canvas_resizer.resize_virtual_canvas_tofit_bounds(
            shrinkage_leeway=0, bounds_dirty=True
        )

    def CmdRememberLayout1(self):
        self.snapshot_mgr.QuickSave(slot=1)

    def CmdRememberLayout2(self):
        self.snapshot_mgr.QuickSave(slot=2)

    def CmdRestoreLayout1(self):
        self.snapshot_mgr.QuickRestore(slot=1)

    def CmdRestoreLayout2(self):
        self.snapshot_mgr.QuickRestore(slot=2)

    def SelectNodeNow(self, shape):
        canvas = shape.GetCanvas()

        self.app.run.CmdDeselectAllShapes()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        shape.Select(
            True, dc
        )  # could pass None as dc if you don't want to trigger the OnDrawControlPoints(dc) handler immediately - e.g. if you want to do a complete redraw of everything later anyway

        # change colour when select
        # shape.SetBrush(wx.WHITE_BRUSH) #wx.Brush("WHEAT", wx.SOLID))
        # canvas.Refresh(False) # works
        # canvas.Redraw(dc) # works too
        # shape.Draw(dc) # works too, most efficient

        # canvas.Refresh(False)   # t/f or don't use - doesn't seem to make a difference

        # self.UpdateStatusBar(shape)  # only available in the shape evt handler (this method used to live there...)

    def delete_shape_view(self, shape):
        # View
        self.app.run.CmdDeselectAllShapes()
        for line in shape.GetLines()[:]:
            line.Delete()
        shape.Delete()

    def Clear(self):
        self.frame.SetStatusText("Draw: Clear")
        self.GetDiagram().DeleteAllShapes()

        dc = wx.ClientDC(self)
        self.GetDiagram().Clear(
            dc
        )  # Clears screen - don't prepare the dc or it will only clear the top scrolled bit (see my mailing list discussion)

        self.displaymodel.Clear()

        if "wxMac" in wx.PlatformInfo:  # Hack on Mac so that onKeyChar bindings take hold properly.
            wx.CallAfter(self.SetFocus)
        elif (
            "wxGTK" in wx.PlatformInfo
        ):  # Hack on Linux so that onKeyChar bindings take hold properly.
            wx.CallLater(1500, self.app.context.wxapp.multiText.SetFocus)
            wx.CallLater(1500, self.SetFocus)

    def NewEdgeMarkFrom(self):
        selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
        if not selected:
            self.frame.SetStatusText("Please select a node")
            return

        self.new_edge_from = selected[0].node
        self.frame.SetStatusText("From %s" % self.new_edge_from.id)

    def NewEdgeMarkTo(self, edge_type="composition"):
        selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
        if not selected:
            self.frame.SetStatusText("Please select a node")
            return

        tonode = selected[0].node
        self.frame.SetStatusText("To %s" % tonode.id)

        if self.new_edge_from == None:
            self.frame.SetStatusText("Please set from node first")
            return

        if self.new_edge_from.id == tonode.id:
            self.frame.SetStatusText("Can't link to self")
            return

        if not self.displaymodel.graph.FindNodeById(self.new_edge_from.id):
            self.frame.SetStatusText("From node %s doesn't seem to be in graph anymore!" % self.new_edge_from.id)
            return

        edge = self.displaymodel.graph.AddEdge(
            tonode, self.new_edge_from, weight=None
        )  # swap direction as is a directional composition.
        # TODO should also arguably add to umlworkspace's associations_composition or associations_generalisation list (or create a new one for unlabelled associations like the one we are creating here)
        # edge['uml_edge_type'] = ''
        edge["uml_edge_type"] = edge_type
        self.CreateUmlEdge(edge)
        self.mega_refresh()

    def CreateImageShape(self, F):
        # shape = ogl.BitmapShape()
        shape = BitmapShapeResizable()
        img = wx.Image(F, wx.BITMAP_TYPE_ANY)

        # adjusted_img = img.AdjustChannels(factor_red = 1., factor_green = 1., factor_blue = 1., factor_alpha = 0.5)
        # adjusted_img = img.Rescale(10,10)
        adjusted_img = img

        bmp = wx.Bitmap(adjusted_img)
        shape.SetBitmap(bmp)

        self.GetDiagram().AddShape(shape)
        shape.Show(True)

        evthandler = UmlShapeHandler(
            self.log, self.frame, self
        )  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        self.new_evthandler_housekeeping(evthandler)

        setpos(shape, 0, 0)
        # setpos(shape, node.left, node.top)
        # node.width, node.height = shape.GetBoundingBoxMax()
        # node.shape = shape
        # shape.node = node
        return shape

    def CreateUmlShape(self, node):
        def newRegion(font, name, textLst, maxWidth, totHeight=10):
            # Taken from Boa, but put into the canvas class instead of the scrolled window class.
            region = ogl.ShapeRegion()

            if len(textLst) == 0:
                return region, maxWidth, 0

            dc = wx.ClientDC(self)  # self is the canvas
            dc.SetFont(font)

            for text in textLst:
                w, h = dc.GetTextExtent(text)
                if w > maxWidth:
                    maxWidth = w
                totHeight = totHeight + h + 0  # interline padding

            region.SetFont(font)
            region.SetText("\n".join(textLst))
            region.SetName(name)

            return region, maxWidth, totHeight

        shape = DividedShape(width=99, height=98, canvas=self)
        maxWidth = 10  # min node width, grows as we update it with text widths

        """
        Future: Perhaps be able to show regions or not. Might need to totally
        reconstruct the shape.
        """
        # if not self.showAttributes: classAttrs = [' ']
        # if not self.showMethods: classMeths = [' ']

        # Create each region.  If height returned is 0 this means don't create this region.
        regionName, maxWidth, nameHeight = newRegion(
            self.font1, "class_name", [node.classname], maxWidth
        )
        regionAttribs, maxWidth, attribsHeight = newRegion(
            self.font2, "attributes", node.attrs, maxWidth
        )
        regionMeths, maxWidth, methsHeight = newRegion(self.font2, "methods", node.meths, maxWidth)

        # Work out total height of shape
        totHeight = nameHeight + attribsHeight + methsHeight

        # Set regions to be a proportion of the total height of shape
        regionName.SetProportions(0.0, 1.0 * (nameHeight / float(totHeight)))
        regionAttribs.SetProportions(0.0, 1.0 * (attribsHeight / float(totHeight)))
        regionMeths.SetProportions(0.0, 1.0 * (methsHeight / float(totHeight)))

        # Add regions to the shape
        shape.AddRegion(regionName)
        if attribsHeight:  # Dont' make a region unless we have to
            shape.AddRegion(regionAttribs)
        if methsHeight:  # Dont' make a region unless we have to
            shape.AddRegion(regionMeths)

        shape.SetSize(maxWidth + 10, totHeight + 10)
        shape.SetCentreResize(
            False
        )  # Specify whether the shape is to be resized from the centre (the centre stands still) or from the corner or side being dragged (the other corner or side stands still).

        regionName.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ)
        shape.region1 = (
            regionName
        )  # Andy added, for later external reference to classname from just having the shape instance.

        shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetPen(wx.BLACK_PEN)  # Controls the color of the border of the shape
        shape.SetBrush(wx.Brush("WHEAT", wx.SOLID))
        setpos(shape, node.left, node.top)
        self.GetDiagram().AddShape(
            shape
        )  # self.AddShape is ok too, ShapeCanvas's AddShape is delegated back to Diagram's AddShape.  ShapeCanvas-->Diagram
        shape.Show(True)

        evthandler = UmlShapeHandler(
            self.log, self.frame, self
        )  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        self.new_evthandler_housekeeping(evthandler)

        shape.FlushText()

        # Don't set the node left,top here as the shape needs to conform to the node.
        # On the other hand the node needs to conform to the shape's width,height.
        # ACTUALLY I now do set the pos of the shape, see above,
        # just before the AddShape() call.
        #
        node.width, node.height = (
            shape.GetBoundingBoxMax()
        )  # TODO: Shouldn't this be in node coords not world coords?
        node.shape = shape
        shape.node = node
        return shape

    def createNodeShape(self, node):  # FROM SPRING LAYOUT
        shape = ogl.RectangleShape(node.width, node.height)
        shape.AddText(node.id)
        setpos(shape, node.left, node.top)
        # shape.SetDraggable(True, True)
        self.AddShape(shape)
        node.shape = shape
        shape.node = node

        # wire in the event handler for the new shape
        evthandler = UmlShapeHandler(
            None, self.frame, self
        )  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        self.new_evthandler_housekeeping(evthandler)

    def createCommentShape(self, node):
        # shape = ogl.TextShape( node.width, node.height )
        shape = CommentShape(node.width, node.height)
        shape.SetCentreResize(
            False
        )  # Specify whether the shape is to be resized from the centre (the centre stands still) or from the corner or side being dragged (the other corner or side stands still).
        shape.GetRegions()[0].SetFormatMode(ogl.FORMAT_NONE)  # left justify
        shape.SetCanvas(self)
        shape.SetPen(wx.BLACK_PEN)
        shape.SetBrush(wx.LIGHT_GREY_BRUSH)
        shape.SetBrush(wx.YELLOW_BRUSH)
        font2 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        shape.SetFont(font2)
        for line in node.comment.split("\n"):
            shape.AddText(line)

        setpos(shape, node.left, node.top)
        # shape.SetSize(node.width, node.height)  # this is already done!?
        # shape.SetDraggable(True, True)
        self.AddShape(shape)
        node.shape = shape
        shape.node = node

        # wire in the event handler for the new shape
        evthandler = UmlShapeHandler(
            None, self.frame, self
        )  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        self.new_evthandler_housekeeping(evthandler)
        return shape

    def new_evthandler_housekeeping(self, evthandler):
        # notify app of this new evthandler so app can
        # assign the evthandler's .app attribute.
        # Or could have just done:
        #   evthandler.app = self.app
        # here.  But we may need observer for other things later.
        self.observers.NOTIFY_EVT_HANDLER_CREATED(evthandler)

    def CreateUmlEdge(self, edge):
        """
        @startuml

        class ArrowHead {
            _arrowType
            __init__(   type, end, size, xOffset, name, mf, arrowId)
        }
        class Shape {
            SetCanvas()
            SetPen()
            SetBrush()
        }
        class LineShape <<lib.ogl._lines.py>> {
            _from
            _to
            _arcArrows
            AddArrow(arrowtype)
            DrawArrow(self, dc, arrow, XOffset, proportionalOffset)
            MakeLineControlPoints(2)
        }
        class LineShapeCustom <<src.gui.uml_lines.py>> {
            DrawArrow(self, dc, arrow, XOffset, proportionalOffset)
        }

        Shape <|-- LineShape
        LineShape <|-- LineShapeCustom
        LineShape --> "0..*" ArrowHead : _arcArrows

        note as N1
            custom line drawing introduced
                ARROW_UML_GENERALISATION
                ARROW_UML_COMPOSITION
        end note

        N1 .. LineShapeCustom
        @enduml

        """
        from gui.uml_lines import LineShapeCustom, ARROW_UML_GENERALISATION, ARROW_UML_COMPOSITION

        fromShape = edge["source"].shape
        toShape = edge["target"].shape

        edge_label = edge.get("uml_edge_type", "")
        if edge_label == "generalisation":
            arrowtype = ARROW_UML_GENERALISATION  # used to be ogl.ARROW_ARROW
        elif edge_label == "composition":
            arrowtype = ARROW_UML_COMPOSITION  # used to be ogl.ARROW_FILLED_CIRCLE
        else:
            arrowtype = None

        if True or edge_label == "comment":
            line = ogl.LineShape()  # attempt to make a dotted line
        else:
            line = LineShapeCustom()  # used to be ogl.LineShape()

        line.SetCanvas(self)

        if edge_label == "association":
            line.SetPen(wx.Pen(colour=wx.BLACK, width=1, style=wx.SHORT_DASH)) # or try PENSTYLE_DOT
        else:
            line.SetPen(wx.BLACK_PEN)

        line.SetBrush(wx.BLACK_BRUSH)
        if arrowtype:
            line.AddArrow(arrowtype)
        line.MakeLineControlPoints(2)

        fromShape.AddLine(line, toShape)
        self.GetDiagram().AddShape(line)
        line.Show(True)

    def OnWheelZoom(self, event):
        # print "OnWheelZoom"
        if self.working:
            return
        self.working = True

        SCROLL_AMOUNT = 40
        if not event.ControlDown():
            oldscrollx = self.GetScrollPos(wx.HORIZONTAL)
            oldscrolly = self.GetScrollPos(wx.VERTICAL)
            if event.GetWheelRotation() < 0:
                self.Scroll(oldscrollx, oldscrolly + SCROLL_AMOUNT)
            else:
                self.Scroll(oldscrollx, max(0, oldscrolly - SCROLL_AMOUNT))
        else:
            if event.GetWheelRotation() < 0:
                self.app.run.CmdLayoutContract(remove_overlaps=not event.ShiftDown())
            else:
                self.app.run.CmdLayoutExpand(remove_overlaps=not event.ShiftDown())

        self.working = False

    def remove_overlaps(self, watch_removals=True):
        """
        Returns T/F if any overlaps found, so caller can decide whether to
        redraw the screen

        Called by

            CmdInsertUmlClass, CmdInsertImage, CmdLayoutExpandContractBase,
            umlcanvas.OnWheelZoom_OverlapRemoval_Defunct,
            umlcanvas.layout_and_position_shapes,
            UmlShapeHandler.OnEndDragLeft
            UmlShapeHandler.OnSizingEndDragLeft
            LayoutBlackboard.LayoutLoopTillNoChange
        """
        self.overlap_remover.RemoveOverlaps(watch_removals=watch_removals)
        return self.overlap_remover.GetStats()["total_overlaps_found"] > 0

    def mega_refresh(self, recalibrate=False, auto_resize_canvas=True):
        """
        Refresh canvas.  There are a lot of ways to trigger a refresh
        and this is one of them.  Often you don't need this call and just
        a subset of this functionality.  TODO understand this better.

        Was once called `stateofthenation`.

        Called by everyone!!??

            CmdFileLoadWorkspaceBase, CmdInsertComment, CmdEditUmlClass
            CmdLayoutExpandContractBase,
            CmdInsertUmlClass
            umlcanvas.NewEdgeMarkTo
            umlcanvas.OnWheelZoom_OverlapRemoval_Defunct
            LayoutBlackboard.LayoutThenPickBestScale
            LayoutBlackboard.Experiment1
            LayoutBlackboard.LayoutLoopTillNoChange
            LayoutBlackboard.ScaleUpMadly
            LayoutBlackboard.GetVitalStats  (only if animate is true)
            OverlapRemoval.RemoveOverlaps   ( refresh gui if self.gui and watch_removals)
            GraphSnapshotMgr.RestoreGraph

            these do an overlap removal first before calling here

            CmdInsertImage
            umlcanvas.layout_and_position_shapes,
            UmlShapeHandler.OnEndDragLeft
            UmlShapeHandler.OnSizingEndDragLeft

            recalibrate = True - called by core spring layout self.gui.mega_refresh()

        Args:
            recalibrate:
            auto_resize_canvas:

        Returns:
        """
        if recalibrate:  # was stateofthespring
            self.coordmapper.Recalibrate()
            self.AllToWorldCoords()

        dc = wx.ClientDC(self)
        self.PrepareDC(dc)

        for node in self.displaymodel.graph.nodes:
            node.shape.Move2(dc, node.left, node.top, display=False)
        self.Refresh()

        self.Update()  # or wx.SafeYield()  # Without this the nodes don't paint during a "L" layout (edges do!?)
        # You need to be yielding or updating on a regular basis, so that when your OS/window manager sends repaint messages to your app, it can handle them. See http://stackoverflow.com/questions/10825128/wxpython-how-to-force-ui-refresh
        if auto_resize_canvas:
            self.canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=True)

        # This cures so many phoenix refresh issues that I'm throwing it in here for fun too.
        self.frame.Layout()  # needed when running phoenix

    def layout_and_position_shapes(self):
        """
        Layouit and position shapes.

        Called by
            CmdLayout
            CmdFileImportBase

        Returns: -
        """
        self.canvas_resizer.frame_calibration(
            auto_resize_virtualcanvas=False
        )  # going to do a mega_refresh later so no point changing virt canvas now
        self.AllToLayoutCoords()
        self.layouter.layout(keep_current_positions=False, optimise=True)
        self.AllToWorldCoords()
        if self.remove_overlaps():
            self.mega_refresh()

    def get_umlboxshapes(self):
        """
        Return list of all uml classes and comment shapes

        TODO take into account images and other future shapes

        Returns: list of all shapes
        """
        # return [s for s in self.GetDiagram().GetShapeList() if not isinstance(s, ogl.LineShape)]
        # return [s for s in self.GetDiagram().GetShapeList() if isinstance(s, DividedShape)]
        return [
            s
            for s in self.GetDiagram().GetShapeList()
            if isinstance(s, DividedShape) or isinstance(s, CommentShape)
        ]

    umlboxshapes = property(get_umlboxshapes)

    def OnDestroy(self, evt):
        for shape in self.GetDiagram().GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)

    def OnLeftClick(self, x, y, keys):  # Override of ShapeCanvas method
        # keys is a bit list of the following: KEY_SHIFT  KEY_CTRL
        self.app.run.CmdDeselectAllShapes()

    def build_view(self, translatecoords=True):
        """
        Builds the shapes from the display model, attaching shapes to nodes
        and in the case of edge shapes, attaching them to ??

        This is an important method.

        Called by
            CmdFileLoadWorkspaceBase.load_model_from_text_and_build_shapes()

            CmdFileImportBase - and its subclasses
                class CmdFileImportFromFilePath(CmdFileImportBase):  # was class CmdFileImportSource(CmdBase):
                class CmdFileImportViaDialog(CmdFileImportBase):  # was class CmdFileImport(CmdBase):

            CmdBuildColourChartWorkspace

        Args:
            translatecoords: ?

        Returns:
        """
        if translatecoords:
            self.AllToWorldCoords()

        # Clear existing visualisation, including any attached edges/lines
        for node in self.displaymodel.graph.nodes:
            if node.shape:
                self.delete_shape_view(node.shape)
                node.shape = None

        # Create fresh visualisation
        for node in self.displaymodel.graph.nodes:
            assert not node.shape
            if isinstance(node, CommentNode) or hasattr(node, "comment"):
                shape = self.createCommentShape(node)
            else:
                shape = self.CreateUmlShape(node)
            self.displaymodel.classnametoshape[
                node.id
            ] = shape  # Record the name to shape map so that we can wire up the links later.

        for edge in self.displaymodel.graph.edges:
            self.CreateUmlEdge(edge)

