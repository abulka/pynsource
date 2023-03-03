from view.display_model import DisplayModel
from view.display_model import CommentNode
from .uml_shapes import *
from .coord_utils import setpos, getpos, Move2, ZoomInfo
from layout.snapshots import GraphSnapshotMgr
from layout.layout_spring import GraphLayoutSpring
from layout.overlap_removal import OverlapRemoval
from layout.coordinate_mapper import CoordinateMapper
from .canvas_resizer import CanvasResizer
from common.architecture_support import *
from gui.shape_menu_mgr import MENU_ID_CANCEL_LINE
import time
import pprint
from gui.settings import PRO_EDITION, NATIVE_LINES_OGL_LIKE, ASYNC_BACKGROUND_REFRESH, LOCAL_OGL
from gui.settings_wx import DEFAULT_COMMENT_FONT_SIZE, DEFAULT_CLASS_HEADING_FONT_SIZE, DEFAULT_CLASS_ATTRS_METHS_FONT_SIZE
import wx
from common.approx_equal import approx_equal
from typing import List, Set, Dict, Tuple, Optional

if PRO_EDITION:
    import ogl2 as ogl
    from ogl2 import Connectable, Resizeable, Selectable, Attributable
    from .uml_shape_handler import UmlShapeHandlerOglTwo
else:
    if LOCAL_OGL:
        import ogl
    else:
        import wx.lib.ogl as ogl
    from gui.repair_ogl import repairOGL
    repairOGL()
    from .uml_shape_handler import UmlShapeHandler

ogl.Shape.Move2 = Move2  # moves to the top left coordinate (not the silly centre x,y)
from gui.uml_lines import LineShapeUml, ARROW_UML_GENERALISATION, ARROW_UML_COMPOSITION

if PRO_EDITION:

    # class UmlBlock(ogl.Block):
    #     def __init__(self):
    #         super().__init__()
    #         self.AddAttribute("attrs")
    #         self.AddAttribute("methods")
    #         self.code = ""
    #         self.label = "class name here"

    class UmlShapeHandler:  # Mock
        def __init__(self, log, frame, shapecanvas): pass
        def SetShape(self, shape): pass
        def SetPreviousHandler(self, eh): pass


    class DividedShapeOglTwo(UmlShapeHandlerOglTwo, DividedShape):
        # Ensure UmlShapeHandlerOglTwo is first so it's methods take priority MRO

        def __init__(self, width, height, canvas, log, frame):
            DividedShape.__init__(self, width=width, height=height, canvas=canvas)
            UmlShapeHandlerOglTwo.__init__(self, log, frame, canvas)


    class CommentShapeOglTwo(UmlShapeHandlerOglTwo, CommentShape, Connectable, Resizeable, Selectable, Attributable):

        def __init__(self, width, height, canvas, log, frame):

            # super().init()  - don't do this we want to bypass CommentShape init altogether
            # and do an init based on ogltwo x,y,x2,y2
            ogl.RectangleShape.__init__(self, 10, 10, 10+width, 10+height)
            UmlShapeHandlerOglTwo.__init__(self, log, frame, canvas)

            # ANDY #####
            Resizeable.__init__(self)
            Connectable.__init__(self)
            Attributable.__init__(self)

            # MUST put UmlShapeHandlerOglTwo FIRST in the inheritance chain so that it's
            # OnEndDragLeft method gets called instead of ShapeEvtHandler's stub OnEndDragLeft (MRO)
            # self.ping()

        def draw(self, dc):
            super().draw(dc)
            self.OnDraw(dc) # hacky way to add the comment corner fold drawing stuff,
                            # without changing the wx.ogl based CommentShape code.
                            # the OnDraw will percolate to RectangleShape and stop there.
            self.OnDrawContents(dc)  # need to call explicitly cos not composite?

    class LineShapeUmlOglTwo(UmlShapeHandlerOglTwo, LineShapeUml):
        # Ensure UmlShapeHandlerOglTwo is first so it's methods take priority MRO

        def __init__(self, log, frame, canvas):
            LineShapeUml.__init__(self)
            UmlShapeHandlerOglTwo.__init__(self, log, frame, canvas)


class UmlCanvas(ogl.ShapeCanvas):
    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)

        # self.observers = multicast()  # not used anymore, but see app.py to resurrect

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

        # self.Bind(wx.EVT_SCROLLWIN, self.onScroll)  # not usually needed, testing only

        # These are the fonts for the divided shape regions 0 (the class name) and region 1, 2
        # (the attributes and methods).
        self.font1 = wx.Font(DEFAULT_CLASS_HEADING_FONT_SIZE, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.font2 = wx.Font(DEFAULT_CLASS_ATTRS_METHS_FONT_SIZE, wx.MODERN, wx.NORMAL, wx.NORMAL, False)

        self.working = False
        # flag to communicate with layout engine.  aborting keypress in gui should set this to true

        self.new_edge_from = None  # the 'from' node when creating new edges manually via UI

        self._kill_layout = False
        self.mega_refresh_flag = False

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

    def join_shapes(self, fromShape, toShape, edge_type="association"):  # override ogltwo version
        """
        Overrides the method in the ogltwo, so that we create a graph edge entry and umledge instead
        of the low level native line shapes.

        Args:
            fromShape:
            toShape:

        Returns:

        """
        assert PRO_EDITION
        # print("join shapes on umlcanvas called")
        if not hasattr(fromShape, "node") or not hasattr(toShape, "node"):
            super().join_shapes(fromShape, toShape)
            print("aborted high level join cos no nodes detected - revert to low level join")
        else:
            from_node = fromShape.node
            to_node = toShape.node

            # swap direction as is a directional composition.
            edge = self.displaymodel.graph.AddEdge(to_node, from_node, weight=None)
            edge["uml_edge_type"] = edge_type  # association, generalisation, composition
            self.CreateUmlEdgeShape(edge)
            # self.new_edge_from = None  # reset from after each connection, for UI clarity
            self.mega_refresh()

    def Clear(self):
        self.GetDiagram().DeleteAllShapes()

        dc = wx.ClientDC(self)
        self.GetDiagram().Clear(
            dc
        )  # Clears screen - don't prepare the dc or it will only clear the top scrolled bit (see my mailing list discussion)

        self.displaymodel.Clear()

        if "wxMac" in wx.PlatformInfo:  # Hack on Mac so that onKeyChar bindings take hold properly.
            wx.CallAfter(self.SetFocus)
        # elif (
        #     "wxGTK" in wx.PlatformInfo
        # ):  # Hack on Linux so that onKeyChar bindings take hold properly.
        #     wx.CallLater(1500, self.app.context.wxapp.multiText.SetFocus)
        #     wx.CallLater(1500, self.SetFocus)

    def CreateUmlShape(self, node, update_existing_shape: DividedShape = None):

        # if PRO_EDITION:
        #     shape = UmlBlock()
        #     # self.canvas.AddShape(i)
        #     self.InsertShape(shape, 999)
        #     shape.label = node.classname
        #     shape.move_to(node.left, node.top)
        #     shape.SetSize(node.width, node.height)
        #     shape.SetCanvas(self)
        #     node.shape = shape
        #     shape.node = node
        #     self.deselect()
        #     self.Refresh()
        #     return shape

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
            if PRO_EDITION:
                # shape = DividedShapeOglTwo(width=99, height=98, canvas=self)
                shape = DividedShapeOglTwo(width=99, height=98, canvas=self, log=self.log, frame=self.frame)
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

        shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetPen(wx.BLACK_PEN)  # Controls the color of the border of the shape
        shape.SetBrush(wx.Brush("WHEAT", wx.SOLID))

        if not update_existing_shape:
            setpos(shape, node.left, node.top)
            # print("setpos being called on shape", node.left, node.top)
            assert getpos(shape) == (node.left, node.top)
            # should we also update node positions to match the shape positions?

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
        # self.new_evthandler_housekeeping(evthandler)

        shape.FlushText()
        # assert approx_equal(getpos(shape)[0], node.left, 5) and approx_equal(getpos(shape)[1], node.top, 5), f"shape at {getpos(shape)} should be at {(node.left, node.top)}"

        # Don't set the node left,top here as the shape needs to conform to the node.
        # On the other hand the node needs to conform to the shape's width,height.
        # ACTUALLY I now do set the pos of the shape, see above,
        # just before the AddShape() call.
        #
        # TODO: Shouldn't this be in node coords not world coords?
        node.width, node.height = shape.GetBoundingBoxMax()
        # print("shape at", shape._xpos, shape._ypos, "getpos says", getpos(shape), "node was", node.left, node.top)

        node.shape = shape
        shape.node = node

        return shape


    def CreateUmlModuleShape(self, node, update_existing_shape: DividedShape = None):
        shape = self.CreateUmlShape(node, update_existing_shape)

        # change the colour to indicate its a module
        # shape.SetBrush(wx.Brush("DARK TURQUOISE", wx.SOLID))
        shape.SetBrush(wx.Brush("LIGHT BLUE", wx.SOLID))


    def createCommentShape(self, node):

        # if PRO_EDITION:
        #     shape = UmlBlock()
        #     # self.canvas.AddShape(i)
        #     shape.fill = ["YELLOW"]
        #     self.InsertShape(shape, 999)
        #     # shape.label = "this is some comment\nthis is some comment222" # node.classname
        #     shape.label = "this is some comment" # node.classname  # TODO MULTILINE and regions
        #     shape.move_to(node.left, node.top)
        #     shape.SetSize(node.width, node.height)
        #     shape.SetCanvas(self)
        #     node.shape = shape
        #     shape.node = node
        #     self.deselect()
        #     self.Refresh()
        #     return shape



        # shape = ogl.TextShape( node.width, node.height )
        if PRO_EDITION:
            # shape = CommentShapeOglTwo(node.width, node.height)
            shape = CommentShapeOglTwo(node.width, node.height, canvas=self, log=self.log, frame=self.frame)
            # shape.ping()
        else:
            shape = CommentShape(node.width, node.height)
        shape.SetCentreResize(
            False
        )  # Specify whether the shape is to be resized from the centre (the centre stands still) or from the corner or side being dragged (the other corner or side stands still).
        shape.GetRegions()[0].SetFormatMode(ogl.FORMAT_NONE)  # left justify
        shape.SetCanvas(self)
        shape.SetPen(wx.BLACK_PEN)
        shape.SetBrush(wx.YELLOW_BRUSH)
        font2 = wx.Font(DEFAULT_COMMENT_FONT_SIZE, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        shape.SetFont(font2)
        if PRO_EDITION:
            # so ogl2 respects the change - need to investigate
            # how wx.ogl and ogl2 differ re this stuff and why ogl2 needs this
            # certainly ogl2 has font for shape and font for each region, yet
            # somehow wx.ogl is smarter and one call for the shape fixes the region shape
            # fot but in ogl2 it doesn't and this extra call is needed.
            shape.GetRegions()[0].SetFont(font2)
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
        # self.new_evthandler_housekeeping(evthandler)
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
        # self.new_evthandler_housekeeping(evthandler)

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
        # self.new_evthandler_housekeeping(evthandler)

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
        class LineShapeUml <<src.gui.uml_lines.py>> {
            DrawArrow(self, dc, arrow, XOffset, proportionalOffset)
        }

        Shape <|-- LineShape
        LineShape <|-- LineShapeUml
        LineShape --> "0..*" ArrowHead : _arcArrows

        note as N1
            custom line drawing introduced
                ARROW_UML_GENERALISATION
                ARROW_UML_COMPOSITION
        end note

        N1 .. LineShapeUml
        @enduml

        """
        fromShape = edge["source"].shape
        toShape = edge["target"].shape
        # print("edge target shape is", edge["target"])

        # ANDY HACK

        if PRO_EDITION and NATIVE_LINES_OGL_LIKE:
            self.join_shapes(fromShape, toShape)
            return

        edge_label = edge.get("uml_edge_type", "")
        if edge_label == "generalisation":
            arrowtype = ARROW_UML_GENERALISATION  # used to be ogl.ARROW_ARROW
        elif edge_label == "composition":
            arrowtype = ARROW_UML_COMPOSITION  # used to be ogl.ARROW_FILLED_CIRCLE
        else:
            arrowtype = None

        if PRO_EDITION:
            line = LineShapeUmlOglTwo(self.log, self.frame, canvas=self)
        else:
            line = LineShapeUml()

        line.SetCanvas(self)
        edge["shape"] = line

        if edge_label == "association":
            line.SetPen(
                wx.Pen(colour=wx.BLACK, width=1, style=wx.SHORT_DASH)
            )  # or try PENSTYLE_DOT
        else:
            line.SetPen(wx.BLACK_PEN)

        line.SetBrush(wx.BLACK_BRUSH)
        if arrowtype:
            line.AddArrow(arrowtype)
        line.MakeLineControlPoints(2)

        # print(f"line created: GetBoundingBoxMax {line.GetBoundingBoxMax()} line getpos() {getpos(line)} fromShape x/ypos {fromShape._xpos}, {fromShape._ypos} toShape x/ypos {toShape._xpos}, {toShape._ypos}")
        fromShape.AddLine(line, toShape)
        # print(f"fromShape.AddLine: GetBoundingBoxMax {line.GetBoundingBoxMax()} line getpos() {getpos(line)}")
        self.GetDiagram().AddShape(line)
        line.Show(True)

        # New - add shape handler to lines - should probably add its own custom shape handler
        shape = line
        # wire in the event handler for the new shape
        evthandler = UmlShapeHandler(
            None, self.frame, self
        )  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        # self.new_evthandler_housekeeping(evthandler)

    def focus_canvas(self):
        """ accelerator stuff
        this is what is called when shape is deselected
        the only acceleration should be to cancel the pending line drawing
        """
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL, ord("X"), MENU_ID_CANCEL_LINE)])
        self.frame.SetAcceleratorTable(accel_tbl)
        self.frame.Bind(wx.EVT_MENU, self.OnCancelLine, id=MENU_ID_CANCEL_LINE)

    def SelectNodeNow(self, shape):
        canvas = shape.GetCanvas()
        assert canvas is not None

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

        if not PRO_EDITION:  # fix selection change refresh bug on linux & windows
            self.Draw()  # don't do self.mega_refresh() because it causes "drag unselected shape snaps back bug"
            self.Refresh()

        # self.UpdateStatusBar(shape)  # only available in the shape evt handler (this method used to live there...)

    def mega_refresh(self, recalibrate=False, auto_resize_canvas=True):
        if ASYNC_BACKGROUND_REFRESH:
            print("mega_refresh (outer) called")
            self.mega_refresh_flag = True
        else:
            self._mega_refresh(recalibrate, auto_resize_canvas)

    def _mega_refresh(self, recalibrate=False, auto_resize_canvas=True):
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
        if not PRO_EDITION:
            """
            Critical call, that draws shapes to dc, this is what mouse motion deep in wx.ogl is doing
            Not needed in ogl2 because there is no use of double buffering and we draw everything
            in one hit during a paint.  Though some of the residual ogl library code is still being used
            and might need a proper call to draw?
            """
            self.Draw()

        """
        Pretty sure Update() not doing anything useful anymore and is not needed.
        
        Calling this method immediately repaints the invalidated area of the window and all of 
        its children recursively (this normally only happens when the flow of control returns to 
        the event loop). 
        
        Notice that this function doesn’t invalidate any area of the window so nothing happens if 
        nothing has been invalidated (i.e. marked as requiring a redraw). Use Refresh first if 
        you want to immediately redraw the window unconditionally. 

        https://wxpython.org/Phoenix/docs/html/wx.Window.html?highlight=wx.window#wx.Window.Update
        
        You need to be yielding or updating on a regular basis, so that when your OS/window 
        manager sends repaint messages to your app, it can handle them. See 
        http://stackoverflow.com/questions/10825128/wxpython-how-to-force-ui-refresh 
        
        Note that we have a wx.SafeYield() at the bottom of this method which is essential for
        ongoing refresh during layout.
        """
        # self.Update()

        if auto_resize_canvas:
            zoom_info = self.prepare_zoom_info()
            self.canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=True,
                                                                   zoom_info=zoom_info)

        # This cures so many phoenix refresh issues that I'm throwing it in here for fun too.
        # self.extra_refresh()

        self.Refresh()  # better place for refresh, also fixes problems when bundled and wx.ogl mode

        if 'wxMSW' in wx.PlatformInfo:
            """
            'wxMac': needed to see interim layout results if in a compute loop - but when using it in wxasync mode messes with 
                     async and eventing leading to slowdown (causes gradual slowdown of wxpython events due to the wx.SafeYield())
            'wxGTK': causes keychar bind breakage issue in linux
            'wxMSW': can see interim layout results ok without it, used to need it to stop blurring of lines during layout 
                     but cannot see this problem anymore, so we could potentially no use this call at all - leave it in for now for windows only
            """
            wx.SafeYield()

    def prepare_zoom_info(self, delta=None):
        if PRO_EDITION:
            return ZoomInfo(scale=self.scalex, delta=delta)
        else:
            return None

    def mega_from_blackboard(self):
        MAX_SNAPSHOTS_TO_ANIMATE = 1
        for snapshot_num in reversed(
            range(min(len(self.snapshot_mgr.snapshots), MAX_SNAPSHOTS_TO_ANIMATE))
        ):
            self.snapshot_mgr.Restore(snapshot_num)
            if MAX_SNAPSHOTS_TO_ANIMATE > 1:
                time.sleep(0.05)

    def extra_refresh(self):
        """
        Draws all shapes onto the buffered dc, which is only needed for wx.ogl not for ogl2
        which doesn't use buffered dc and does most of its drawing on the dc offered by paint.

        Historical note: when I first ported to phoenix I fixed a lot of new refresh problems
        by calling self.frame.Layout() which was effective, but the wrong solution.  A simple
        Draw() would have done it.  The layout solution was an accidental discovery and presumably
        also has unnecessary overhead as it triggers the sizers in the frame, and also triggers an
        on resize frame.
        """
        if not PRO_EDITION:
            self.Draw()
            # self.frame.Layout()  # needed when running phoenix

    def layout_and_position_shapes(self):
        """
        Layout and position shapes.

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

            # First attempt
            # try:
            #     line.Delete()
            # except ValueError:
            #     # I wonder why wx.ogl didn't need this.  Probably the unlink() call repaired and
            #     # cleared the _lines
            #     print("already deleted line!", line)  # both shapes point to same line, one exists

            # # Cleaner attempt
            line.Delete()

        shape.Delete()

    def OnLeftClick(self, x, y, keys):
        """Override of ShapeCanvas method - does not exist in ogltwo, see OnLeftUp() below"""
        # keys is a bit list of the following: KEY_SHIFT  KEY_CTRL
        assert not PRO_EDITION
        self.app.run.CmdDeselectAllShapes()
        self.focus_canvas()

    def OnLeftUp(self, event):
        """ogltwo equivalent to OnLeftClick above, no need to deselect all shapes cos that's
        automatically done in the base ogltwo shape canvas.
        """
        assert PRO_EDITION
        shape = self.getCurrentShape(event)
        if shape is None:  # clicked on empty space
            self.focus_canvas()
        super().OnLeftUp(event)

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()  # http://www.wxpython.org/docs/api/wx.KeyEvent-class.html

        if self.working:
            event.Skip()
            return
        self.working = True

        if keycode == wx.WXK_ESCAPE:
            self.frame.SetStatusText("ESC key detected: Layout Aborted")
            self.kill_layout = True

            # # HACK PLAY
            # shape = RectangleShapeAndy(50,50)
            # self.AddShape(shape)
            # shape.SetX(random.randint(40,80))
            # shape.SetY(random.randint(40,80))
            # shape.Show(True)
            # self.Refresh()
            # # END HACK PLAY

        # These are done via the main menu - no need to replicate with another
        # different set of keys, here
        #
        # if keycode == wx.WXK_RIGHT:
        #     self.app.run.CmdLayoutExpand(remove_overlaps=not event.ShiftDown())
        #
        # elif keycode == wx.WXK_LEFT:
        #     self.app.run.CmdLayoutContract(remove_overlaps=not event.ShiftDown())

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
        # print("keycode", keycode)
        consumed = False

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
            self.snapshot_mgr.Restore(todisplay)  # snapshot 1 becomes 0 as a param
            self.mega_refresh()
            consumed = True

        elif keycode == "r":
            print("Refresh()")
            self.Refresh()
            consumed = True

        elif keycode == "R":
            print("menu Refresh()")
            self.app.run.CmdRefreshUmlWindow()
            consumed = True


        elif keycode in ["d", "D"]:
            self.app.run.CmdDumpDisplayModel(parse_models=keycode == "D")
            consumed = True

        elif keycode in ["I"]:
            self.app.context.wxapp.MessageBox(pprint.pformat(self.app.context.wxapp.cwd_info))
            consumed = True

        elif keycode == "s":
            self.CmdTrimScrollbars()
            consumed = True

        #
        # Developer keys - creates a workspace filled with coloured shapes
        #                   and lets you cycle through them.  Useful for deciding on colours.
        #
        # elif keycode == "G":  # and event.ShiftDown() and event.ControlDown():
        #     self.app.run.CmdBuildColourChartWorkspace()
        #
        # elif keycode in ["h", "H"]:
        #     self.app.run.CmdColourSequential(color_range_offset=(keycode == "H"))

        self.working = False

        if not consumed:  # avoid forwarding if consumed, otherwise makes an annoying beep on Mac
            event.Skip()  # needed for Linux menu shortcuts to work!

    def OnWheelZoom(self, event):
        if self.working:
            print("OnWheelZoom (uml_canvas) - working")
            return
        self.working = True

        # self._report_mouse_position()

        try:
            if event.ControlDown() and PRO_EDITION:
                # zoom
                amount = 0.04
                if event.GetWheelRotation() < 0:
                    self.zoom_out(amount)
                else:
                    self.zoom_in(amount)
            elif event.ShiftDown():
                # Layout expansion and contraction
                if event.GetWheelRotation() < 0:
                    self.app.run.CmdLayoutContract(remove_overlaps=not event.ShiftDown())
                else:
                    self.app.run.CmdLayoutExpand(remove_overlaps=not event.ShiftDown())
            else:
                # Normal panning scroll - both vertical and horizontal

                # print(f"OnWheelZoom (uml_canvas) {event} "
                #       f"GetWheelRotation={event.GetWheelRotation():2} "
                #       f"GetWheelAxis={event.GetWheelAxis():2} "
                #       f"self.GetScrollPos(wx.HORIZONTAL)={self.GetScrollPos(wx.HORIZONTAL)} "
                #       f"self.GetScrollPos(wx.VERTICAL)={self.GetScrollPos(wx.VERTICAL)} "
                #       f"GetScrollRange(wx.HORIZONTAL)={self.GetScrollRange(wx.HORIZONTAL)} "
                #       f"GetScrollRange(wx.VERTICAL)={self.GetScrollRange(wx.VERTICAL)}"
                #       )

                # self.Scroll(0, self.GetScrollRange(wx.VERTICAL))  # force scroll to bottom

                if event.GetWheelAxis() == wx.MOUSE_WHEEL_VERTICAL:
                    v = event.GetWheelRotation()
                    if "wxMac" in wx.PlatformInfo:  # natural scrolling - should get from system
                        v = -v
                    self.Scroll(self.GetScrollPos(wx.HORIZONTAL),
                                self.GetScrollPos(wx.VERTICAL) + v)
                else:
                    self.Scroll(self.GetScrollPos(wx.HORIZONTAL) + event.GetWheelRotation(),
                                self.GetScrollPos(wx.VERTICAL))
        except Exception as e:
            print(getattr(e, "message", repr(e)))
        finally:
            self.working = False

    def _float_point_to_int(self, point: Tuple[float, float]) -> Tuple[int, int]:
        return tuple([int(coord) for coord in point])

    def _report_mouse_position(self):
        self.frame.SetStatusText(
            f"Mouse Pos: {self._float_point_to_int(self.mouse_pos_in_client_coords())}")

    # Uncomment these as needed

    # def OnMotion(self, event):  # testing only, reports mouse position as you move it
    #     assert PRO_EDITION
    #     super().OnMotion(event)  # keep things working esp. with ogltwo, not so imp with wx.ogl
    #     self._report_mouse_position()
    #     # self._dump_screen_info()
    #
    # def onScroll(self, event):  # testing only (also need to uncomment the Bind(wx.EVT_SCROLLWIN...
    #     self._dump_screen_info()
    #     # if event.Orientation == wx.SB_HORIZONTAL:
    #     #     print("Horizontal scroll to", event.Position, "origin", self.GetViewStart())
    #     # else:
    #     #     print("Vertical scroll to", event.Position, "origin", self.GetViewStart())
    #     event.Skip()  # keep things working

    def mouse_pos_in_client_coords(self):
        """Converts screen mouse position into client coords that takes into account scroll and zoom"""
        mouse_client_x, mouse_client_y = self.ScreenToClient(wx.GetMousePosition())
        scroll_pos_x, scroll_pos_y = self.GetViewStart()
        x = (mouse_client_x + scroll_pos_x) / self.scalex
        y = (mouse_client_y + scroll_pos_y) / self.scaley
        return x, y

    def _zoom(self, amount=0.25, set_to_scale=None, reset=False):
        old_scalex = self.scalex
        old_scaley = self.scaley
        if reset:
            self.scalex = 1.0
            self.scaley = 1.0
        elif set_to_scale:
            self.scalex = self.scaley = set_to_scale
        else:
            self.scalex = max(self.scalex + amount, 0.3)
            self.scaley = max(self.scaley + amount, 0.3)
        deltax = self.scalex - old_scalex
        # print("deltax", deltax, "old_scalex", old_scalex, "self.scalex", self.scalex)
        self.fix_scrollbars(deltax)
        self.Refresh()

    def zoom_out(self, amount=0.25):
        self._zoom(-amount)

    def zoom_in(self, amount=0.25):
        self._zoom(amount)

    def zoom_to_fit(self):

        # def calc1(margin=60):
        #     # initial attempt at fit to size - deprecated
        #     from common.printframework import MyPrintout
        #     printout = MyPrintout(self, self.log)
        #     shapes_bounds_x, shapes_bounds_y = printout._fit_diagram_to_paper(self.GetSize()[0], self.GetSize()[1])
        #     client_sizex, client_sizey = self.GetClientSize()
        #     client_sizex -= margin
        #     client_sizey -= margin
        #     return shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey

        # or

        def calc2(margin=20):
            # Idea: rather than subtracting from the client window
            # We can add to the total shape bounds like calc_allshapes_bounds() does with
            # margin of 20, which seems to work OK.
            shapes_bounds_x, shapes_bounds_y = self.canvas_resizer.calc_allshapes_bounds()
            client_sizex, client_sizey = self.GetClientSize()
            client_sizex -= margin
            client_sizey -= margin
            return shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey


        def calc_scale(shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey, debug=True):
            ratio_x = client_sizex / shapes_bounds_x
            ratio_y = client_sizey / shapes_bounds_y
            ratio = min(ratio_x, ratio_y)
            # new_scale = ratio / self.scalex
            new_scale = ratio
            if debug:
                print(
                    f"dBOUNDS {int(shapes_bounds_x)}, {int(shapes_bounds_y)} "
                    "Scale ", self.scalex,
                    "New Scale ", new_scale,
                    " | "
                    f"GetClientSize {self.GetClientSize()} "
                    f"ratio {ratio:5.4f} out of ({ratio_x:4.1f}, {ratio_y:3.1f}) | ",
                    f"DELTA {new_scale - self.scalex:3.1f}")
            return new_scale

        # def scan(_from, _to, want_value, func):
        #     # diagnostics - loop up finding successful margins for subtracting off shape bounds
        #     results = []
        #     for margin in range(_from, _to):
        #         shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey = func(margin)
        #         new_scale = calc_scale(shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey, debug=False)
        #         success = approx_equal(new_scale, want_value, 0.02)
        #         results.append(success)
        #     first_success = None
        #     last_success = None
        #     for index,success in enumerate(results):
        #         if success and first_success is None:
        #             first_success = index
        #         if not success and first_success is not None and last_success is None:
        #             last_success = index
        #     print(f"scan: {func.__name__} {_from} {_to} wanting {want_value} success range is {first_success}..{last_success}")
        #
        # Looping and testing to find best margin factors for algorithms 1 and 2
        #
        # sample uml diagram - comment0
        #
        # scan(0, 50, want_value=1.2, func=calc1)
        # scan(0, 50, want_value=1.2, func=calc2)
        #
        # sample uml diagram - uml00
        #
        # scan(0, 50, want_value=1.6, func=calc1)
        # scan(0, 50, want_value=1.6, func=calc2)
        #
        # sample uml diagram - uml01
        #
        # scan(0, 50, want_value=1.9, func=calc1)
        # scan(0, 50, want_value=1.9, func=calc2)
        #
        # Results:
        """
        sample uml diagram - comment0
        scan: calc1 0 50 wanting 1.2 success range is 25..46
        scan: calc2 0 50 wanting 1.2 success range is 1..23

        sample uml diagram - uml00
        scan: calc1 0 50 wanting 1.6 success range is None..None
        scan: calc2 0 50 wanting 1.6 success range is 23..39

        sample uml diagram - uml01
        scan: calc1 0 50 wanting 1.9 success range is 34..47
        scan: calc2 0 50 wanting 1.9 success range is 0..9

        Conclusion: use calc2 algorithm, with margin 20 - seems to work OK.
        """

        shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey = calc2()
        new_scale = calc_scale(shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey, debug=False)

        # Useful assertions when you have a particular zoom to fit scale you want when loading
        # a particular diagram.  Zoom manually to see what zoom you like and lock it in.  Then see
        # if zoom to fit gets anywhere close.
        #
        # for uml00
        # assert approx_equal(new_scale, 1.2, 0.02), f"scale should be about " \
        #                                           f"1.2 not {new_scale}"
        #
        # for comment0
        # assert approx_equal(new_scale, 1.6, 0.02), f"scale should be about " \
        #                                           f"1.6 not {new_scale}"

        self._zoom(set_to_scale=new_scale)

    def zoom_reset(self):
        self._zoom(reset=True)

    def fix_scrollbars(self, deltax=None):
        zoom_info = self.prepare_zoom_info(delta=deltax)
        self.canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=False,
                                                               zoom_info=zoom_info)

    def _dump_screen_info(self):
        print(" " * 41,
              f"thumb PAN ({self.GetViewStart()[0]:3d},{self.GetViewStart()[1]:3d})",
              #
              # Values that seem to never change
              #
              # f"GetClientAreaOrigin {self.GetClientAreaOrigin()} ",  # always 0,0
              # f"GetContentScaleFactor {self.GetContentScaleFactor()} ",  # always 2.0
              # f"GetMinClientSize {self.GetMinClientSize()} ",  # always (-1, -1)
              # f"GetMaxClientSize {self.GetMaxClientSize()} ",  # always (-1, -1)
              # f"GetPosition {self.GetPosition()} ",  # always (0, 0)
              # f"GetMaxSize {self.GetMaxSize()} ",  # always (-1, -1)
              # f"GetScaleX {self.GetScaleX()} ",  # always 1.0
              # f"frame.GetClientAreaOrigin {self.frame.GetClientAreaOrigin()} ",  # always seems to be 0, 0 - It may be different from (0, 0) if the frame has a toolbar.
              #
              # Values that change when move frame or resize frame
              #
              # f"GetSize {self.GetSize()} ",  # size of window, changes when resize frame
              # f"GetClientRect {self.GetClientRect()} ",  #  (0, 0, 989, 685) changes as resize frame
              # f"GetClientSize {self.GetClientSize()} ",  #  (989, 685) changes as resize frame
              # f"GetScreenPosition {self.GetScreenPosition()} ",  # (322, 218) changes when move frame
              # f"GetScreenRect {self.GetScreenRect()} ",  # (322, 218, 1004, 682) changes when move or resize frame
              # f"GetScrollPageSize(wx.HORIZONTAL) {self.GetScrollPageSize(wx.HORIZONTAL)} ",  # 1000 changes as resize frame
              # f"GetScrollPageSize(wx.VERTICAL) {self.GetScrollPageSize(wx.VERTICAL)} ",  # 679 changes as resize frame
              # f"GetScrollThumb(wx.HORIZONTAL) {self.GetScrollThumb(wx.HORIZONTAL)} ",  # always 1029 until resize frame
              # f"GetScrollThumb(wx.VERTICAL) {self.GetScrollThumb(wx.VERTICAL)} ",   # always 698 until resize frame
              #
              # duplicate info I already have
              #
              # f"GetScrollPos(wx.HORIZONTAL) {self.GetScrollPos(wx.HORIZONTAL)} ",  # same as GetViewStart
              # f"GetScrollPos(wx.VERTICAL) {self.GetScrollPos(wx.VERTICAL)} ",  # same as GetViewStart
              #
              # misc
              #
              # f"GetVirtualSize {self.GetVirtualSize()} ",  # increases as I zoom, cos I change it
              #
              # f"ClientToScreen((0,0) {self.ClientToScreen(0,0)} ",  # GetScreenPosition => (778, 402) same as ClientToScreen((0,0)) => (778, 402)
              # f"GetScreenPosition {self.GetScreenPosition()[1] - } ",  # (322, 218) changes when move frame
              # f"notebook.GetClientSize {self.app.context.wxapp.notebook.GetClientSize() if self.app.context.wxapp.notebook else 'no notebook'} ",  # (322, 218) changes when move frame
              # f"notebook.GetScreenPosition {self.app.context.wxapp.notebook.GetScreenPosition() if self.app.context.wxapp.notebook else 'no notebook'} ",
              # f"self.GetScreenPosition {self.GetScreenPosition()} ",
              #
              "")

    def OnDestroy(self, evt):
        for shape in self.GetDiagram().GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)

    def CmdTrimScrollbars(self):
        zoom_info = self.prepare_zoom_info()
        self.canvas_resizer.resize_virtual_canvas_tofit_bounds(
            shrinkage_leeway=0,
            bounds_dirty=True,
            zoom_info=zoom_info
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
        self.frame.SetStatusText(
            f'Line begun from "{self.new_edge_from.id}" - now select destination node and r.click to join'
        )

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
            self.frame.SetStatusText(
                "From node %s doesn't seem to be in graph anymore!" % self.new_edge_from.id
            )
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

    # def new_evthandler_housekeeping(self, evthandler):
    #     # notify app of this new evthandler so app can
    #     # assign the evthandler's .app attribute.
    #     # Or could have just done:
    #     #   evthandler.app = self.app
    #     # here.  But we may need observer for other things later.
    #     # TODO - 1. only reason event handler needs app is for OnLeftDoubleClick
    #     # TODO - 2. event handler or shape/event hdlr combo can get to app via self.umlcanvas.app
    #
    #     # self.observers.NOTIFY_EVT_HANDLER_CREATED(evthandler)  # TODO delete this complexity
    #     pass

    def get_umlboxshapes(self):
        """
        Return list of all uml classes and comment shapes

        TODO take into account images and other future shapes

        Returns: list of all shapes
        """
        # return [s for s in self.GetDiagram().GetShapeList() if not isinstance(s, ogl.LineShape)]
        # return [s for s in self.GetDiagram().GetShapeList() if isinstance(s, DividedShape)]
        if PRO_EDITION:
            return [
                s
                for s in self.GetDiagram().GetShapeList()
                # if isinstance(s, UmlBlock)
                if isinstance(s, (DividedShapeOglTwo, CommentShapeOglTwo))
            ]
        else:
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
            msg += f"node: Pos: ({node.left}, {node.top}) Size: (w={node.width}, h={node.height})"  # could also add canvas: {shape.GetCanvas()}
        self.frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d) %s center %s %s" % (x, y, width, height, msg, shape._xpos, shape._ypos))
