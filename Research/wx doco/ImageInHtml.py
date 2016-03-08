# http://wiki.wxpython.org/wxHTML

import wx
import  wx.lib.wxpTag

# The html page as a python string literal
page = r"""
<HTML>
<BODY>
<H1>Embedding an Image in wxHTML</H1>

<H3> As a wx.StaticBitmap: </H3>

<center>
  <wxp module="ImageInHtml" class="Bitmap1">
  </wxp>
</center>


<H3> Using a MemoryFSHandler: </H3>
<center>
<img src="memory:smalltest.png">
</center>

</BODY>
</HTML>
"""


class Bitmap1(wx.StaticBitmap):
    """
    A custom StaticBitmap class that holds your image. 
    """
    def __init__(self, *args, **kwargs):
        """
        The __init__ is called by the HtmlWindow, it takes all the usual
        wx.Window parameters, then the custom bitmap is added to the key
        word arguments.
        """
        bmp = smalltest.GetBitmap()
        kwargs['bitmap'] = bmp
        wx.StaticBitmap.__init__(self, *args, **kwargs)

class DemoFrame(wx.Frame):
    """ This window displays a HtmlWindow """
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        htmlwin = wx.html.HtmlWindow(self)
        htmlwin.SetPage(page)

       
class MyApp(wx.App):
    """
    A little test wx.App
    """
    def OnInit(self):
        # add the image to the MemoryFileSystem:
        mfs = wx.MemoryFSHandler()
        wx.FileSystem_AddHandler(mfs)
        mfs.AddFile("smalltest.png", smalltest.GetImage(), wx.BITMAP_TYPE_PNG)


        # Initializing the Frame
        frame = DemoFrame(None, title="HTML Tester Window", size = (500,500))
        self.SetTopWindow(frame)
        
        frame.Show(True)
        return True

## This is the image data itself, created with the img2py utility that
## ships with wxPython
from wx.lib.embeddedimage import PyEmbeddedImage
smalltest = PyEmbeddedImage(
    "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")


if __name__ == "__main__" :
    app = MyApp(0)
    app.MainLoop()