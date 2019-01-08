#!/usr/bin/env python

"""
This demo shows how to use a ScaledBitmap2 (which is like a scaled bitmap,
but uses memory more efficiently for large images and high zoom levels.

It also draws random points on top of the image, because someone on the 
wxPython mailing list asked for that...


"""

## Set a path to an Image file here:
ImageFile = "Moo.jpg" 


import wx
import random
## import the installed version
from wx.lib.floatcanvas import NavCanvas, FloatCanvas

## import a local version
#import sys
#sys.path.append("../")
#from floatcanvas import NavCanvas, FloatCanvas

class DrawFrame(wx.Frame):

    """
    A frame used for the FloatCanvas Demo

    """

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.CreateStatusBar()

        # Add the Canvas
        Canvas = NavCanvas.NavCanvas(self,
                                     ProjectionFun = None,
                                     BackgroundColor = "DARK SLATE BLUE",
                                     ).Canvas
        Canvas.MaxScale=4 # sets the maximum zoom level
        self.Canvas = Canvas

        FloatCanvas.EVT_MOTION(self.Canvas, self.OnMove ) 

        
        # create the image:
        image = wx.Image(ImageFile)
        self.width, self.height = image.GetSize()
        img = Canvas.AddScaledBitmap( image,
                                      (0,0),
                                      Height=image.GetHeight(),
                                      Position = 'tl',
                                      )

        #Box.Bind(FloatCanvas.EVT_FC_LEFT_DOWN, self.Binding)
        
        ## now set up a timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.AddPoint, self.timer)


        
        self.Show()
        Canvas.ZoomToBB()
        self.timer.Start(20)

    def AddPoint(self, evt=None):
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        self.Canvas.AddPoint((x,-y), Diameter=8) # minus y, because floatcanvas uses y-up
        self.Canvas.Draw()
        wx.GetApp().Yield(onlyIfNeeded=True)
        
    def OnMove(self, event):
        """
        Updates the status bar with the world coordinates

        """
        self.SetStatusText("%i, %i"%tuple(event.Coords))

    def Binding(self, event):
        print("Writing a png file:")
        self.Canvas.SaveAsImage("junk.png")
        print("Writing a jpeg file:")
        self.Canvas.SaveAsImage("junk.jpg",wx.BITMAP_TYPE_JPEG)


app = wx.App(False)
F = DrawFrame(None, title="FloatCanvas Demo App", size=(700,700) )
app.MainLoop()
    
    
    
    









