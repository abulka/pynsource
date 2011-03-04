''' This is copied from the wx demo, but contains some code
    we'll likely want to use in the reporting part of the
    framework.
'''

from wxPython.wx         import *
import wx

#----------------------------------------------------------------------
BUFFERED=False

class MyPrintout(wxPrintout):
    def __init__(self, canvas):
        wxPrintout.__init__(self)
        self.canvas = canvas
        #self.log = log

    def OnBeginDocument(self, start, end):
        #self.log.WriteText("wxPrintout.OnBeginDocument\n")
        return self.base_OnBeginDocument(start, end)

    def OnEndDocument(self):
        #self.log.WriteText("wxPrintout.OnEndDocument\n")
        self.base_OnEndDocument()

    def OnBeginPrinting(self):
        #self.log.WriteText("wxPrintout.OnBeginPrinting\n")
        self.base_OnBeginPrinting()

    def OnEndPrinting(self):
        #self.log.WriteText("wxPrintout.OnEndPrinting\n")
        self.base_OnEndPrinting()

    def OnPreparePrinting(self):
        #self.log.WriteText("wxPrintout.OnPreparePrinting\n")
        self.base_OnPreparePrinting()

    def HasPage(self, page):
        #self.log.WriteText("wxPrintout.HasPage: %d\n" % page)
        if page <= 2:
            return True
        else:
            return False

    def GetPageInfo(self):
        #self.log.WriteText("wxPrintout.GetPageInfo\n")
        return (1, 2, 1, 2)

    def OnPrintPage(self, page):
        #self.log.WriteText("wxPrintout.OnPrintPage: %d\n" % page)
        dc = self.GetDC()

        #-------------------------------------------
        # One possible method of setting scaling factors...

        maxX = self.canvas.getWidth()
        maxY = self.canvas.getHeight()

        # Let's have at least 50 device units margin
        marginX = 50
        marginY = 50

        # Add the margin to the graphic size
        maxX = maxX + (2 * marginX)
        maxY = maxY + (2 * marginY)

        # Get the size of the DC in pixels
        (w, h) = dc.GetSizeTuple()

        # Calculate a suitable scaling factor
        scaleX = float(w) / maxX
        scaleY = float(h) / maxY

        # Use x or y scaling factor, whichever fits on the DC
        actualScale = min(scaleX, scaleY)

        # Calculate the position on the DC for centering the graphic
        posX = (w - (self.canvas.getWidth() * actualScale)) / 2.0
        posY = (h - (self.canvas.getHeight() * actualScale)) / 2.0

        # Set the scale and origin
        dc.SetUserScale(actualScale, actualScale)
        dc.SetDeviceOrigin(int(posX), int(posY))

        #-------------------------------------------

        self.canvas.DoDrawing(dc, True)
        dc.DrawText("Page: %d" % page, marginX/2, maxY-marginY)

        return True


#----------------------------------------------------------------------


class TestPrintPanel(wxPanel):
    def __init__(self, parent):
        wxPanel.__init__(self, parent, -1)
        #self.log = log
        self.frame = parent


        self.printData = wxPrintData()
        self.printData.SetPaperId(wxPAPER_LETTER)

        self.box = wxBoxSizer(wxVERTICAL)
        self.canvas = MyCanvas(self)
        self.box.Add(self.canvas, 1, wxGROW)

        subbox = wxBoxSizer(wxHORIZONTAL)
        btn = wxButton(self, 1201, "Print Setup")
        EVT_BUTTON(self, 1201, self.OnPrintSetup)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        btn = wxButton(self, 1202, "Print Preview")
        EVT_BUTTON(self, 1202, self.OnPrintPreview)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        btn = wxButton(self, 1203, "Print")
        EVT_BUTTON(self, 1203, self.OnDoPrint)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        self.box.Add(subbox, 0, wxGROW)

        self.SetAutoLayout(True)
        self.SetSizer(self.box)


    def OnPrintSetup(self, event):
        printerDialog = wxPrintDialog(self)
        printerDialog.GetPrintDialogData().SetPrintData(self.printData)
        printerDialog.GetPrintDialogData().SetSetupDialog(True)
        printerDialog.ShowModal();
        self.printData = printerDialog.GetPrintDialogData().GetPrintData()
        printerDialog.Destroy()


    def OnPrintPreview(self, event):
#        self.log.WriteText("OnPrintPreview\n")
        printout = MyPrintout(self.canvas)
        printout2 = MyPrintout(self.canvas)
        self.preview = wxPrintPreview(printout, printout2, self.printData)
        if not self.preview.Ok():
            #self.log.WriteText("Houston, we have a problem...\n")
            return

        frame = wxPreviewFrame(self.preview, self.frame, "This is a print preview")

        frame.Initialize()
        frame.SetPosition(self.frame.GetPosition())
        frame.SetSize(self.frame.GetSize())
        frame.Show(True)



    def OnDoPrint(self, event):
        pdd = wxPrintDialogData()
        pdd.SetPrintData(self.printData)
        printer = wxPrinter(pdd)
        printout = MyPrintout(self.canvas)
        if not printer.Print(self.frame, printout):
            wxMessageBox("There was a problem printing.\nPerhaps your current printer is not set correctly?", "Printing", wxOK)
        else:
            self.printData = printer.GetPrintDialogData().GetPrintData()
        printout.Destroy()


class MyCanvas(wxScrolledWindow):
    def __init__(self, parent, id = -1, size = wxDefaultSize):
        wxScrolledWindow.__init__(self, parent, id, wxPoint(0, 0), size, wxSUNKEN_BORDER)

        self.lines = []
        self.maxWidth  = 1000
        self.maxHeight = 1000
        self.x = self.y = 0
        self.curLine = []
        self.drawing = False

        self.SetBackgroundColour("WHITE")
        self.SetCursor(wxStockCursor(wxCURSOR_PENCIL))
        #bmp = images.getTest2Bitmap()
        #mask = wxMaskColour(bmp, wxBLUE)
        #bmp.SetMask(mask)
        #self.bmp = bmp

        self.SetScrollbars(20, 20, self.maxWidth/20, self.maxHeight/20)

        if BUFFERED:
            # Initialize the buffer bitmap.  No real DC is needed at this point.
            self.buffer = wxEmptyBitmap(self.maxWidth, self.maxHeight)
            dc = wxBufferedDC(None, self.buffer)
            dc.SetBackground(wxBrush(self.GetBackgroundColour()))
            dc.Clear()
            self.DoDrawing(dc)

        EVT_LEFT_DOWN(self, self.OnLeftButtonEvent)
        EVT_LEFT_UP(self,   self.OnLeftButtonEvent)
        EVT_MOTION(self,    self.OnLeftButtonEvent)
        EVT_PAINT(self, self.OnPaint)
        ##EVT_MOUSEWHEEL(self, self.OnWheel)


    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight


    def OnPaint(self, event):
        if BUFFERED:
            # Create a buffered paint DC.  It will create the real
            # wxPaintDC and then blit the bitmap to it when dc is
            # deleted.  Since we don't need to draw anything else
            # here that's all there is to it.
            dc = wxBufferedPaintDC(self, self.buffer)
        else:
            dc = wxPaintDC(self)
            self.PrepareDC(dc)
            # since we're not buffering in this case, we have to
            # paint the whole window, potentially very time consuming.
            self.DoDrawing(dc)


    def DoDrawing(self, dc, printing=False):
        dc.BeginDrawing()
        dc.SetPen(wxPen('RED'))
        dc.DrawRectangle(5, 5, 50, 50)

        dc.SetBrush(wxLIGHT_GREY_BRUSH)
        dc.SetPen(wxPen('BLUE', 4))
        dc.DrawRectangle(15, 15, 50, 50)

        dc.SetFont(wxFont(14, wxSWISS, wxNORMAL, wxNORMAL))
        dc.SetTextForeground(wxColour(0xFF, 0x20, 0xFF))
        te = dc.GetTextExtent("Hello World")
        dc.DrawText("Hello World", 60, 65)

        dc.SetPen(wxPen('VIOLET', 4))
        dc.DrawLine(5, 65+te[1], 60+te[0], 65+te[1])

        lst = [(100,110), (150,110), (150,160), (100,160)]
        dc.DrawLines(lst, -60)
        dc.SetPen(wxGREY_PEN)
        dc.DrawPolygon(lst, 75)
        dc.SetPen(wxGREEN_PEN)
        dc.DrawSpline(lst+[(100,100)])

        #dc.DrawBitmap(self.bmp, 200, 20, True)
        dc.SetTextForeground(wxColour(0, 0xFF, 0x80))
        dc.DrawText("a bitmap", 200, 85)

##         dc.SetFont(wxFont(14, wxSWISS, wxNORMAL, wxNORMAL))
##         dc.SetTextForeground("BLACK")
##         dc.DrawText("TEST this STRING", 10, 200)
##         print dc.GetFullTextExtent("TEST this STRING")

        font = wxFont(20, wxSWISS, wxNORMAL, wxNORMAL)
        dc.SetFont(font)
        dc.SetTextForeground(wxBLACK)
        for a in range(0, 360, 45):
            dc.DrawRotatedText("Rotated text...", 300, 300, a)

        dc.SetPen(wxTRANSPARENT_PEN)
        dc.SetBrush(wxBLUE_BRUSH)
        dc.DrawRectangle(50,500,50,50)
        dc.DrawRectangle(100,500,50,50)

        dc.SetPen(wxPen('RED'))
        dc.DrawEllipticArc(200, 500, 50, 75, 0, 90)

        if not printing:
            # This has troubles when used on a print preview in wxGTK,
            # probably something to do with the pen styles and the scaling
            # it does...
            y = 20
            for style in [wxDOT, wxLONG_DASH, wxSHORT_DASH, wxDOT_DASH, wxUSER_DASH]:
                pen = wxPen("DARK ORCHID", 1, style)
                if style == wxUSER_DASH:
                    pen.SetCap(wxCAP_BUTT)
                    pen.SetDashes([1,2])
                    pen.SetColour("RED")
                dc.SetPen(pen)
                dc.DrawLine(300, y, 400, y)
                y = y + 10

        dc.SetBrush(wxTRANSPARENT_BRUSH)
        dc.SetPen(wxPen(wxColour(0xFF, 0x20, 0xFF), 1, wxSOLID))
        dc.DrawRectangle(450, 50, 100, 100)
        old_pen = dc.GetPen()
        new_pen = wxPen("BLACK", 5)
        dc.SetPen(new_pen)
        dc.DrawRectangle(470, 70, 60, 60)
        dc.SetPen(old_pen)
        dc.DrawRectangle(490, 90, 20, 20)

        self.DrawSavedLines(dc)
        dc.EndDrawing()


    def DrawSavedLines(self, dc):
        dc.SetPen(wxPen('MEDIUM FOREST GREEN', 4))
        for line in self.lines:
            for coords in line:
                apply(dc.DrawLine, coords)


    def SetXY(self, event):
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):
        xView, yView = self.GetViewStart()
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        return (event.GetX() + (xView * xDelta),
                event.GetY() + (yView * yDelta))

    def OnLeftButtonEvent(self, event):
        if event.LeftDown():
            self.SetFocus()
            self.SetXY(event)
            self.curLine = []
            self.CaptureMouse()
            self.drawing = True

        elif event.Dragging() and self.drawing:
            if BUFFERED:
                # If doing buffered drawing, create the buffered DC, giving it
                # it a real DC to blit to when done.
                cdc = wxClientDC(self)
                self.PrepareDC(cdc)
                dc = wxBufferedDC(cdc, self.buffer)
            else:
                dc = wxClientDC(self)
                self.PrepareDC(dc)

            dc.BeginDrawing()
            dc.SetPen(wxPen('MEDIUM FOREST GREEN', 4))
            coords = (self.x, self.y) + self.ConvertEventCoords(event)
            self.curLine.append(coords)
            apply(dc.DrawLine, coords)
            self.SetXY(event)
            dc.EndDrawing()


        elif event.LeftUp() and self.drawing:
            self.lines.append(self.curLine)
            self.curLine = []
            self.ReleaseMouse()
            self.drawing = False


## This is an example of what to do for the EVT_MOUSEWHEEL event,
## but since wxScrolledWindow does this already it's not
## necessary to do it ourselves.

##     wheelScroll = 0
##     def OnWheel(self, evt):
##         delta = evt.GetWheelDelta()
##         rot = evt.GetWheelRotation()
##         linesPer = evt.GetLinesPerAction()
##         print delta, rot, linesPer
##         ws = self.wheelScroll
##         ws = ws + rot
##         lines = ws / delta
##         ws = ws - lines * delta
##         self.wheelScroll = ws
##         if lines != 0:
##             lines = lines * linesPer
##             vsx, vsy = self.GetViewStart()
##             scrollTo = vsy - lines
##             self.Scroll(-1, scrollTo)


if __name__ == "__main__":
        # instantiate a simple app object:
        app = wx.PySimpleApp()
        frame = wx.Frame(None, -1, "test")
        panel = TestPrintPanel(frame)
        frame.Show(1)
        app.MainLoop()
