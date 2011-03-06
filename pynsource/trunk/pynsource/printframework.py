# Version 1.5 (clone of 1.4c with wx changes - Andy)

import  wx

class MyPrintout(wx.Printout):
    def __init__(self, canvas, log):
        wx.Printout.__init__(self)
        self.canvas = canvas
        self.log = log

    def OnBeginDocument(self, start, end):
        #self.log.WriteText("wxPrintout.OnBeginDocument\n")
        return super(MyPrintout, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        #self.log.WriteText("wxPrintout.OnEndDocument\n")
        super(MyPrintout, self).OnEndDocument()

    def OnBeginPrinting(self):
        #self.log.WriteText("wxPrintout.OnBeginPrinting\n")
        super(MyPrintout, self).OnBeginPrinting()

    def OnEndPrinting(self):
        #self.log.WriteText("wxPrintout.OnEndPrinting\n")
        super(MyPrintout, self).OnEndPrinting()

    def OnPreparePrinting(self):
        #self.log.WriteText("wxPrintout.OnPreparePrinting\n")
        super(MyPrintout, self).OnPreparePrinting()

    def HasPage(self, page):
        #self.log.WriteText("wxPrintout.HasPage: %d\n" % page)

        # If GetPageInfo is setup correctly, this can 
        # always return True.
        return True        

    def GetPageInfo(self):
        #self.log.WriteText("wxPrintout.GetPageInfo\n")
        # This will print just 1 page
        return (1, 1, 1, 1)
    
    def OnPrintPage(self, page):
        #self.log.WriteText("wxPrintout.OnPrintPage: %d\n" % page)
        dc = self.GetDC()

        #-------------------------------------------
        # One possible method of setting scaling factors...

        canvasMaxX = self.canvas.GetSize()[0]
        canvasMaxY = self.canvas.GetSize()[1]
        #self.GetShapeListInfo()
        canvasMaxX, canvasMaxY = self.AdjustMaxCoords(canvasMaxX, canvasMaxY)

        # Let's have at least 50 device units margin
        marginX = 50
        marginY = 50

        # Add the margin to the graphic size
        maxX = canvasMaxX + (2 * marginX)
        maxY = canvasMaxY + (2 * marginY)

        # Get the size of the DC in pixels
        (w, h) = dc.GetSizeTuple()

        # Calculate a suitable scaling factor
        scaleX = float(w) / maxX
        scaleY = float(h) / maxY

        # Use x or y scaling factor, whichever fits on the DC
        actualScale = min(scaleX, scaleY)

        # Calculate the position on the DC for centering the graphic
        posX = (w - (canvasMaxX * actualScale)) / 2.0
        posY = (h - (canvasMaxY * actualScale)) / 2.0

        # Set the scale and origin
        dc.SetUserScale(actualScale, actualScale)
        dc.SetDeviceOrigin(int(posX), int(posY))

        #-------------------------------------------

        self.canvas.Redraw(dc)
        #dc.DrawText("Page: %d" % page, marginX/2, maxY-marginY)

        return True

    def AdjustMaxCoords(self, maxX, maxY):
        shapelist = self.canvas.GetDiagram().GetShapeList()
        msg = "initial %d  %d\n" %(maxX, maxY)
        xs = []
        ys = []
        for shape in shapelist:
            width, height = shape.GetBoundingBoxMax()
            x1 = shape.GetX() - width / 2.0
            y1 = shape.GetY() - height / 2.0
            xs.append(x1+width)
            ys.append(y1+height)
            msg += "x = %d  shape.GetX() = %d width = %d  --- y = %d shape.GetY() = %d height = %d\n" % (x1, shape.GetX(), width, y1, shape.GetY(), height)
        msg += "max %d %d\n" % (max(xs), max(ys))
        #self.log.WriteText(msg)
        return max(xs), max(ys)
            
    def GetShapeListInfo_diagnostic(self):
        # Andy diagnostic.  Even lists lines and selected node effect shapes.
        shapelist = self.canvas.GetDiagram().GetShapeList()
        msg = ""
        for shape in shapelist:
            width, height = shape.GetBoundingBoxMax()
            msg += "shape %d width %d height %d\n" % (shape.GetId(), width, height)
        self.log.WriteText(msg)
