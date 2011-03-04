# Version 1.3a


from wxPython.wx import wxPrintout


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
        
##        if page <= 2:
##            return True
##        else:
##            return False

        # If GetPageInfo is setup correctly, this can 
        # always return True.
        return True        

    def GetPageInfo(self):
        #self.log.WriteText("wxPrintout.GetPageInfo\n")
##        return (1, 2, 1, 2)
        # This will print just 1 page
        return (1, 1, 1, 1)
    
    def OnPrintPage(self, page):
        #self.log.WriteText("wxPrintout.OnPrintPage: %d\n" % page)
        dc = self.GetDC()

        #-------------------------------------------
        # One possible method of setting scaling factors...

        maxX = self.canvas.GetSize()[0]
        maxY = self.canvas.GetSize()[1]

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
        posX = (w - (self.canvas.GetSize()[0] * actualScale)) / 2.0
        posY = (h - (self.canvas.GetSize()[1] * actualScale)) / 2.0

        # Set the scale and origin
        dc.SetUserScale(actualScale, actualScale)
        dc.SetDeviceOrigin(int(posX), int(posY))

        #-------------------------------------------

        #self.canvas.DoDrawing(dc, True)
        self.canvas.Redraw(dc)
        dc.DrawText("Page: %d" % page, marginX/2, maxY-marginY)

        return True

