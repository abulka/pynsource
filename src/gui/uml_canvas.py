from view.display_model import DisplayModel
from view.display_model import CommentNode
from .uml_shapes import *
from .coord_utils import setpos, getpos, Move2
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
from gui.shape_menu_mgr import MENU_ID_CANCEL_LINE

repairOGL()

ogl.Shape.Move2 = Move2


class UmlCanvas(ogl.ShapeCanvas):

    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)
        # ShapeCanvasAndy.__init__(self, parent)  # ANDY HACK OGL
        # self.scalex =2.0  # ANDY HACK OGL
        # self.scaley =2.0  # ANDY HACK OGL

        self.observers = multicast()
        self.app = None  # assigned later by app boot

        # set below
        self.canvas_resizer = None
        self.displaymodel = None
        self.layout = None

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
        # flag to communicate with layout engine.  aborting keypress in gui should set this to true

        self.new_edge_from = None  # the 'from' node when creating new edges manually via UI

        self._kill_layout = False

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

        self.displaymodel = DisplayModel(self)
        self.snapshot_mgr = GraphSnapshotMgr(graph=self.displaymodel.graph, umlcanvas=self)
        self.coordmapper = CoordinateMapper(self.displaymodel.graph, self.GetSize())
        self.layouter = GraphLayoutSpring(self.displaymodel.graph, gui=self)
        self.overlap_remover = OverlapRemoval(self.displaymodel.graph, margin=50, gui=self)

        self.focus_canvas()

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

    def CreateUmlShape(self, node, update_existing_shape:DividedShape=None):
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

        if update_existing_shape:
            shape = update_existing_shape
        else:
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
        print("shape.region1", shape.region1)

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
        # prev handler happens to be <gui.uml_shapes.DividedShape> - this handler wiring is tricky
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        self.new_evthandler_housekeeping(evthandler)

        shape.FlushText()

        # Don't set the node left,top here as the shape needs to conform to the node.
        # On the other hand the node needs to conform to the shape's width,height.
        # ACTUALLY I now do set the pos of the shape, see above,
        # just before the AddShape() call.
        #
        # TODO: Shouldn't this be in node coords not world coords?
        node.width, node.height = shape.GetBoundingBoxMax()

        node.shape = shape
        shape.node = node

        return shape

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

    def CreateUmlEdgeShape(self, edge):
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

        if edge_label == "association":
            line = ogl.LineShape()  # attempt to make a dotted line
        else:
            line = LineShapeCustom()  # used to be ogl.LineShape()

        line.SetCanvas(self)
        edge["shape"] = line

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

    def focus_canvas(self):
        """ accelerator stuff
        this is what is called when shape is deselected
        the only acceleration should be to cancel the pending line drawing
        """
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, ord('X'), MENU_ID_CANCEL_LINE),
        ])
        self.frame.SetAcceleratorTable(accel_tbl)
        self.frame.Bind(wx.EVT_MENU, self.OnCancelLine, id=MENU_ID_CANCEL_LINE)

    def SelectNodeNow(self, shape):
        canvas = shape.GetCanvas()

        self.app.run.CmdDeselectAllShapes()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        # Could pass None as dc if you don't want to trigger the OnDrawControlPoints(dc) handler
        # immediately - e.g. if you want to do a complete redraw of everything later anyway
        shape.Select(True, dc)

        # change colour when select
        # shape.SetBrush(wx.WHITE_BRUSH) #wx.Brush("WHEAT", wx.SOLID))
        # canvas.Refresh(False) # works
        # canvas.Redraw(dc) # works too
        # shape.Draw(dc) # works too, most efficient

        # canvas.Refresh(False)   # t/f or don't use - doesn't seem to make a difference

        # self.UpdateStatusBar(shape)  # only available in the shape evt handler (this method used to live there...)

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

    def delete_shape_view(self, shape):
        # View
        self.app.run.CmdDeselectAllShapes()
        for line in shape.GetLines()[:]:
            line.Delete()
        shape.Delete()

    def OnLeftClick(self, x, y, keys):  # Override of ShapeCanvas method
        # keys is a bit list of the following: KEY_SHIFT  KEY_CTRL
        self.app.run.CmdDeselectAllShapes()
        self.focus_canvas()

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
        These are secret keycodes not exposed on any/the main menu
        Normally shortcuts added on the main menu work fine.  But popup menu items are done via
        accelerator table, which gets first pick of the key, otherwise the key comes here
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

        if keycode in ["", ""]:
            pass

        # These are now handled by the global accelerator table.
        #
        # if keycode in ["q", "Q"]:
        #     self.NewEdgeMarkFrom()
        #
        # elif keycode in ["w", "W"]:
        #     self.NewEdgeMarkTo(edge_type="composition")
        #
        # elif keycode in ["e", "E"]:
        #     self.NewEdgeMarkTo(edge_type="generalisation")
        #
        # elif keycode in ["a", "A"]:
        #     self.NewEdgeMarkTo(edge_type="association")
        #

        elif keycode in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            todisplay = ord(keycode) - ord("1")
            self.snapshot_mgr.Restore(todisplay)

        elif keycode == "P":
            self.Refresh()

        elif keycode in ["d", "D"]:
            self.app.run.CmdDumpDisplayModel()

        elif keycode == "s":
            self.CmdTrimScrollbars()

        elif keycode == "G":  # and event.ShiftDown() and event.ControlDown():
            self.app.run.CmdBuildColourChartWorkspace()

        elif keycode in ["h", "H"]:
            self.app.run.CmdColourSequential(color_range_offset=(keycode == "H"))

        self.working = False

        # event.Skip()  # makes an annoying beep if enabled

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

    def OnDestroy(self, evt):
        for shape in self.GetDiagram().GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)

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

    def NewEdgeMarkFrom(self):
        selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
        if not selected:
            self.frame.SetStatusText("Please select a node")
            return

        if self.new_edge_from:
            print("warning, new_edge_from already set")
        self.new_edge_from = selected[0].node
        self.frame.SetStatusText(f"Line begun from \"{self.new_edge_from.id}\" - now select destination node and r.click to join")

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
        edge["uml_edge_type"] = edge_type
        self.CreateUmlEdgeShape(edge)
        self.new_edge_from = None  # reset from after each connection, for UI clarity
        self.mega_refresh()

    def OnCancelLine(self, event):
        if True or self.new_edge_from:
            print("Line drawing cancelled")
        self.new_edge_from = None
        self.frame.SetStatusText("")

    def new_evthandler_housekeeping(self, evthandler):
        # notify app of this new evthandler so app can
        # assign the evthandler's .app attribute.
        # Or could have just done:
        #   evthandler.app = self.app
        # here.  But we may need observer for other things later.
        self.observers.NOTIFY_EVT_HANDLER_CREATED(evthandler)

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

    def AllToLayoutCoords(self):
        self.coordmapper.AllToLayoutCoords()

    def AllToWorldCoords(self):
        self.coordmapper.AllToWorldCoords()

