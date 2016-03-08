import wx

class ImageWindow(wx.ScrolledWindow):
    """Window for displaying a bitmapped Image"""

    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetScrollRate(5,5)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def SetBitmap(self, bitmap):
        self.bitmap = bitmap
        self.SetVirtualSize(bitmap.GetSize())

        # The following does nothing when called before
        # the app starts.
        cdc = wx.ClientDC(self)
        cdc.DrawBitmap(self.bitmap, 0, 0)
        
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.bitmap)

        ## I have tried it with and without the following two lines
        #x,y = self.GetViewStart()
        #dc.DrawBitmap(self.bitmap, x, y)
        dc = wx.BufferedPaintDC(self, self.bitmap, wx.BUFFER_VIRTUAL_AREA)

class TestFrame( wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1)

        # image is 3072 x 2700
        self.im1 = wx.Image("Images/fish1.png", wx.BITMAP_TYPE_ANY)
        self.bm = self.im1.ConvertToBitmap()
        self.wind = ImageWindow(self)
        self.wind.SetSize((600,400))
        self.wind.SetBitmap(self.bm)
        sizer = wx.BoxSizer ()
        sizer.Add(self.wind)
        self.SetSizer(sizer)
        self.Fit()
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
    def OnSize(self, event):
        self.wind.SetSize(self.GetSize ())

if __name__=='__main__':
    app = wx.PySimpleApp()
    f = TestFrame()
    f.Show()
    app.MainLoop()