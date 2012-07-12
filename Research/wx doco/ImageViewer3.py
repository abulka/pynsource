import wx, os

class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):

        wx.Frame.__init__(self, *args, **kwargs)
        # there needs to be an "Images" directory with one or more jpegs in it in the
        # current working directory for this to work
        #self.jpgs = GetJpgList("./Images") # get all the jpegs in the Images directory
        self.jpgs = GetJpgList("./Images") # get all the jpegs in the Images directory
        self.CurrentJpg = 0

        self.MaxSizeZ = 200
        
        b = wx.Button(self, label= "Display next")
        self.Bind(wx.EVT_BUTTON, self.DisplayNext)
        # starting with an EmptyBitmap, the real one will get put there
        # by the call to .DisplayNext()
        self.Image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(self.MaxSizeZ, self.MaxSizeZ))
        self.DisplayNext()

        # Using a Sizer to handle the layout: I never like to use absolute postioning
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(b, 0, wx.CENTER|wx.ALL, 10)

        # adding stretchable space before and after centers the image.
        box.Add((1,1),1)
        box.Add(self.Image, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ADJUST_MINSIZE, 10)
        box.Add((1,1),1)

        self.SetSizerAndFit(box)

        wx.EVT_CLOSE(self, self.OnCloseWindow)
        

    def DisplayNext(self, event=None):
        
        #if self.Image:
        #    #self.box.Destroy() # ANDY
        #    self.Image.Create(self.MaxSizeZ, self.MaxSizeZ, clear=True)
        
        # load the image
        Img = wx.Image(self.jpgs[self.CurrentJpg], wx.BITMAP_TYPE_JPEG)

        # scale the image, preserving the aspect ratio
        W = Img.GetWidth()
        H = Img.GetHeight()
        if W > H:
            NewW = self.MaxSizeZ
            NewH = self.MaxSizeZ * H / W
        else:
            NewH = self.MaxSizeZ
            NewW = self.MaxSizeZ * W / H
        Img = Img.Scale(NewW,NewH)

        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        self.Image.SetBitmap(wx.BitmapFromImage(Img))

        # You can fit the frame to the image, if you want.
        self.Fit()
        self.Layout()   # ANDY

        self.CurrentJpg += 1
        if self.CurrentJpg > len(self.jpgs) -1:
            self.CurrentJpg = 0

    def OnCloseWindow(self, event):
        self.Destroy()


def GetJpgList(dir):
    jpgs = [f for f in os.listdir(dir) if f[-4:] == ".jpg"]
    print "JPGS are:", jpgs

    return [os.path.join(dir, f) for f in jpgs]

class App(wx.App):
    def OnInit(self):
        frame = TestFrame(None, title="wxBitmap Test")
        frame.Show(True)
        return True

if __name__ == "__main__":
    app = App(0)
    app.MainLoop()