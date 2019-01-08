from wxPython.wx import *
from wxPython.ogl import *
import wx

import images

# ----------------------------------------------------------------------
# This creates some pens and brushes that the OGL library uses.

wxOGLInitialize()

# ----------------------------------------------------------------------


class DiamondShape(wxPolygonShape):
    def __init__(self, w=0.0, h=0.0):
        wxPolygonShape.__init__(self)
        if w == 0.0:
            w = 60.0
        if h == 0.0:
            h = 60.0

        ## Either wxRealPoints or 2-tuples of floats  works.

        # points = [ wxRealPoint(0.0,    -h/2.0),
        #          wxRealPoint(w/2.0,  0.0),
        #          wxRealPoint(0.0,    h/2.0),
        #          wxRealPoint(-w/2.0, 0.0),
        #          ]
        points = [(0.0, -h / 2.0), (w / 2.0, 0.0), (0.0, h / 2.0), (-w / 2.0, 0.0)]

        self.Create(points)


# ----------------------------------------------------------------------


class RoundedRectangleShape(wxRectangleShape):
    def __init__(self, w=0.0, h=0.0):
        wxRectangleShape.__init__(self, w, h)
        self.SetCornerRadius(-0.3)


# ----------------------------------------------------------------------


class DividedShape(wxDividedShape):
    def __init__(self, width, height, canvas):
        wxDividedShape.__init__(self, width, height)

        region1 = wxShapeRegion()
        region1.SetText("wxDividedShape")
        region1.SetProportions(0.0, 0.2)
        region1.SetFormatMode(FORMAT_CENTRE_HORIZ)
        self.AddRegion(region1)

        region2 = wxShapeRegion()
        region2.SetText("This is Region number two.")
        region2.SetProportions(0.0, 0.3)
        region2.SetFormatMode(FORMAT_CENTRE_HORIZ | FORMAT_CENTRE_VERT)
        self.AddRegion(region2)

        region3 = wxShapeRegion()

        region3.SetText("blah\nblah\nblah blah")
        region3.SetProportions(0.0, 0.5)
        region3.SetFormatMode(FORMAT_NONE)
        self.AddRegion(region3)

        self.region3 = region3  # for external access...

        self.SetRegionSizes()
        self.ReformatRegions(canvas)

    def ReformatRegions(self, canvas=None):
        rnum = 0
        if canvas is None:
            canvas = self.GetCanvas()
        dc = wxClientDC(canvas)  # used for measuring
        for region in self.GetRegions():
            text = region.GetText()
            self.FormatText(dc, text, rnum)
            rnum += 1

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        self.base_OnSizingEndDragLeft(pt, x, y, keys, attch)
        self.SetRegionSizes()
        self.ReformatRegions()
        self.GetCanvas().Refresh()


# ----------------------------------------------------------------------


class MyEvtHandler(wxShapeEvtHandler):
    def __init__(self, log, frame):
        wxShapeEvtHandler.__init__(self)
        self.log = log
        self.statbarFrame = frame

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        width, height = shape.GetBoundingBoxMax()
        self.statbarFrame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)" % (x, y, width, height))

    def OnLeftClick(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        print(shape.__class__, shape.GetClassName())
        canvas = shape.GetCanvas()
        dc = wxClientDC(canvas)
        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(False, dc)
            canvas.Redraw(dc)
        else:
            redraw = False
            shapeList = canvas.GetDiagram().GetShapeList()
            toUnselect = []
            for s in shapeList:
                if s.Selected():
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            shape.Select(True, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)
                canvas.Redraw(dc)

        self.UpdateStatusBar(shape)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        self.base_OnEndDragLeft(x, y, keys, attachment)
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        self.UpdateStatusBar(shape)

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        self.base_OnSizingEndDragLeft(pt, x, y, keys, attch)
        self.UpdateStatusBar(self.GetShape())

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        self.base_OnMovePost(dc, x, y, oldX, oldY, display)
        self.UpdateStatusBar(self.GetShape())

    def OnRightClick(self, *dontcare):
        self.log.WriteText("%s\n" % self.GetShape())


# ----------------------------------------------------------------------


class TestWindow(wxShapeCanvas):
    scrollStepX = 10
    scrollStepY = 10

    def __init__(self, parent, log, frame):
        wxShapeCanvas.__init__(self, parent)

        maxWidth = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth / 20, maxHeight / 20)

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE")  # wxWHITE)
        self.diagram = wxDiagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.shapes = []
        self.save_gdi = []

        rRectBrush = wxBrush("MEDIUM TURQUOISE", wxSOLID)
        dsBrush = wxBrush("WHEAT", wxSOLID)

        ds0 = self.MyAddShape(DividedShape(100, 150, self), 50, 145, wxBLACK_PEN, dsBrush, "")
        ds1 = self.MyAddShape(DividedShape(140, 150, self), 195, 445, wxBLACK_PEN, dsBrush, "")
        ds2 = self.MyAddShape(DividedShape(440, 150, self), 495, 145, wxBLACK_PEN, dsBrush, "")

        for i in range(1, 20):
            self.MyAddShape(DividedShape(440, 150, self), 50, 445, wxBLACK_PEN, dsBrush, "")

        dc = wxClientDC(self)
        self.PrepareDC(dc)
        for x in range(len(self.shapes)):
            fromShape = self.shapes[x]
            if x + 1 == len(self.shapes):
                toShape = self.shapes[0]
            else:
                toShape = self.shapes[x + 1]
            line = wxLineShape()
            line.SetCanvas(self)

            if toShape == ds1:
                line.SetPen(wxBLACK_PEN)
                line.SetBrush(wxBLACK_BRUSH)
                line.AddArrow(ARROW_FILLED_CIRCLE)
            else:
                line.SetPen(wxBLACK_PEN)
                line.SetBrush(wxBLACK_BRUSH)
                line.AddArrow(ARROW_ARROW)
            line.MakeLineControlPoints(2)
            fromShape.AddLine(line, toShape)
            self.diagram.AddShape(line)
            line.Show(True)

            # for some reason, the shapes have to be moved for the line to show up...
            fromShape.Move(dc, fromShape.GetX(), fromShape.GetY())

        # ANDY EXTRA STUFF

        def_area = """
DoSomething()
DoSomething2()
DoSomething3()
DoSomething32()
DoSomething322()
DoSomething13()
DoSomething113()
DoSomething233()
DoSomething2343()
        """
        ds1.region3.SetText(def_area)
        ds1.SetCentreResize(
            0
        )  # Specify whether the shape is to be resized from the centre (the centre stands still) or from the corner or side being dragged (the other corner or side stands still).
        # for some reason, the shapes have to be resized to re-format theior container text
        # ds1.SetSize(200, 500)
        print(ds1.GetBoundingBoxMax())
        ds1.SetSize(ds1.GetBoundingBoxMax()[0] + 1, ds1.GetBoundingBoxMax()[1])
        ds1.ReformatRegions()
        # self.redraw()

        # Layout
        self.ArrangeShapes()

        EVT_WINDOW_DESTROY(self, self.OnDestroy)

    def redraw(self):
        diagram = self.GetDiagram()
        canvas = diagram.GetCanvas()
        dc = wxClientDC(canvas)
        canvas.PrepareDC(dc)
        for shape in self.shapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
            shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)

    def ArrangeShapes(self):

        dc = wxClientDC(self)
        self.PrepareDC(dc)

        LEFTMARGIN = 50
        TOPMARGIN = 50
        positions = []

        x = LEFTMARGIN
        y = TOPMARGIN

        maxx = 0
        verticalWhiteSpace = 400
        count = 0
        for classShape in self.shapes:
            count += 1
            if count == 3:
                count = 0
                x = LEFTMARGIN
                y = y + verticalWhiteSpace

            whiteSpace = 50  # (width - currentWidth)/(len(self.shapes)-1.0 or 2.0)
            shapeX, shapeY = self.getShapeSize(classShape)
            # snap to diagram grid coords
            csX, csY = self.diagram.Snap((shapeX / 2.0) + x, (shapeY / 2.0) + y)
            # don't display until finished
            positions.append((csX, csY))
            x = x + shapeX + whiteSpace
            if x > maxx:
                maxx = x + 500

        assert len(positions) == len(self.shapes)

        height = y + 500
        width = maxx
        self.setSize(
            wxSize(int(width + 50), int(height + 50))
        )  # fudge factors to keep some extra space

        for (pos, classShape) in zip(positions, self.shapes):
            x, y = pos
            classShape.Move(dc, x, y, false)

        return

        whiteSpaceFactor = 1.4
        # calculate total width and total height
        width = 0
        height = 0
        widths = []
        heights = []
        for shape in self.shapes:
            currentWidth = 0
            currentHeight = 0
            x, y = shape.GetX(), shape.GetY()
            if y > currentHeight:
                currentHeight = y
            currentWidth = currentWidth + x
            # update totals
            if currentWidth > width:
                width = currentWidth
            height = height + currentHeight
            # store generation info
            widths.append(currentWidth)
            heights.append(currentHeight)
        # add in some whitespace so we can see lines...
        width = width * whiteSpaceFactor
        rawHeight = height
        height = height * whiteSpaceFactor
        verticalWhiteSpace = (height - rawHeight) / (len(self.shapes) - 1.0 or 2.0)
        # self.setSize(wxSize(int(width+50), int(height+50))) # fudge factors to keep some extra space
        print("massive size is", int(width + 50), int(height + 50))
        # DONT ACTUALLY DO ANYTHING WITH THIS INFO - yet.

        # distribute each generation across the width
        # and the generations across height
        y = 0
        """
        Converted to python3 but not converted to phoenix, thus not run for a long time.  Plus this 
        is a dangling conversion error that still would need to be understood and fixed.
        
        RefactoringTool: ### In file Research/ogl tests 01/andyOgl02_oldwx.py ###
        RefactoringTool: Line 348: cannot convert map(None, ...) with multiple arguments because map() now truncates to the shortest sequence
        RefactoringTool: Line 348: cannot convert map(None, ...) with multiple arguments because map() now truncates to the shortest sequence
        """
        for currentWidth, currentHeight, shape in map(None, widths, heights, self.shapes):
            x = 0
            # whiteSpace is the space between any two elements...
            whiteSpace = (width - currentWidth) / (len(self.shapes) - 1.0 or 2.0)
            for classShape in self.shapes:
                shapeX, shapeY = self.getShapeSize(classShape)
                # snap to diagram grid coords
                csX, csY = self.diagram.Snap((shapeX / 2.0) + x, (shapeY / 2.0) + y)
                # don't display until finished
                classShape.Move(dc, csX, csY, false)
                x = x + shapeX + whiteSpace
            y = y + currentHeight + verticalWhiteSpace

    def getShapeSize(self, shape):
        """Return the size of a shape's representation, an abstraction point"""
        return shape.GetBoundingBoxMax()

    def setSize(self, size):
        nvsx, nvsy = size.x / self.scrollStepX, size.y / self.scrollStepY
        self.Scroll(0, 0)
        self.SetScrollbars(self.scrollStepX, self.scrollStepY, nvsx, nvsy)
        canvas = self
        canvas.SetSize(canvas.GetVirtualSize())

    def MyAddShape(self, shape, x, y, pen, brush, text):
        shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        if pen:
            shape.SetPen(pen)
        if brush:
            shape.SetBrush(brush)
        if text:
            shape.AddText(text)
        # shape.SetShadowMode(SHADOW_RIGHT)
        self.diagram.AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler(self.log, self.frame)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)
        return shape

    def OnDestroy(self, evt):
        # Do some cleanup
        for shape in self.diagram.GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)
                shape.Destroy()
        self.diagram.Destroy()

    def OnBeginDragLeft(self, x, y, keys):
        self.log.write("OnBeginDragLeft: %s, %s, %s\n" % (x, y, keys))

    def OnEndDragLeft(self, x, y, keys):
        self.log.write("OnEndDragLeft: %s, %s, %s\n" % (x, y, keys))


# ----------------------------------------------------------------------


def runTest(frame, nb, log):
    win = TestWindow(nb, log, frame)
    return win


# ----------------------------------------------------------------------


class __Cleanup:
    cleanup = wxOGLCleanUp

    def __del__(self):
        self.cleanup()


# when this module gets cleaned up then wxOGLCleanUp() will get called
__cu = __Cleanup()


overview = """\
The Object Graphics Library is a library supporting the creation and
manipulation of simple and complex graphic images on a canvas.

"""


# if __name__ == '__main__':
#    import sys,os
#    import run
#    run.main(['', os.path.basename(sys.argv[0])])


class Log:
    def WriteText(self, text):
        if text[-1:] == "\n":
            text = text[:-1]
        wx.LogMessage(text)

    write = WriteText


class BoaApp(wxApp):
    def OnInit(self):
        wxInitAllImageHandlers()

        # self.main = wxFrame1.create(None)

        # self.main = TestWindow(parent=self, log=None, frame=None)

        self.name = "Andy app"

        frame = wx.Frame(
            None,
            -1,
            "RunDemo: " + self.name,
            pos=(50, 50),
            size=(0, 0),
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.DEFAULT_FRAME_STYLE,
        )
        frame.CreateStatusBar()
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(101, "E&xit\tAlt-X", "Exit demo")
        wx.EVT_MENU(self, 101, self.OnButton)
        menuBar.Append(menu, "&File")
        frame.SetMenuBar(menuBar)
        frame.Show(True)
        wx.EVT_CLOSE(frame, self.OnCloseFrame)

        # win = self.demoModule.runTest(frame, frame, Log())
        win = runTest(frame, frame, Log())

        # a window will be returned if the demo does not create
        # its own top-level window
        if win:
            # so set the frame to a good size for showing stuff
            frame.SetSize((640, 480))
            win.SetFocus()
            self.window = win

        else:
            # otherwise the demo made its own frame, so just put a
            # button in this one
            if hasattr(frame, "otherWin"):
                b = wx.Button(frame, -1, " Exit ")
                frame.SetSize((200, 100))
                wx.EVT_BUTTON(frame, b.GetId(), self.OnButton)
            else:
                # It was probably a dialog or something that is already
                # gone, so we're done.
                frame.Destroy()
                return True

        self.SetTopWindow(frame)

        # self.main.Show()
        # self.SetTopWindow(self.main)

        return True

    def OnButton(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.window.ShutdownDemo()
        evt.Skip()


def main():
    application = BoaApp(0)
    application.MainLoop()


if __name__ == "__main__":
    main()
