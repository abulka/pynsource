"""
Simple ogl scrolling canvas to test redraw algorithms and the potentially buggy
behaviour of .Clear(dc) in not taking into account the scroll.

Sent to https://groups.google.com/forum/?hl=en&fromgroups#!searchin/wxpython-users/dc.Clear():$20is$20this$20a$20bug$20or$20am$20I$20doing$20something$20wrong?/wxpython-users/X840K1bA5R4/kf29SKR5X40J

"""

import wx
import wx.lib.ogl as ogl
import random
import time

class MyShapeCanvas(ogl.ShapeCanvas):
    def __init__(self, parent, frame):
        ogl.ShapeCanvas.__init__(self, parent)
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE")
        self.SetDiagram(ogl.Diagram())
        self.GetDiagram().SetCanvas(self)

WINDOW_SIZE = (600, 400)
VIRTUAL_SIZE_X = 1200
VIRTUAL_SIZE_Y = 800

class MainApp(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, -1, "test2 scroll drawing", pos=(450,450), size=WINDOW_SIZE,
                        style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.DEFAULT_FRAME_STYLE)
        self.shapecanvas = MyShapeCanvas(self.frame, self.frame)
        self.shapecanvas.frame = self.frame
        
        self.shapecanvas.SetScrollbars(1, 1, VIRTUAL_SIZE_X, VIRTUAL_SIZE_Y)
        self.Bind(wx.EVT_CHAR, self.onKeyChar)

        ogl.OGLInitialize()  # creates some pens and brushes that the OGL library uses.
        self.frame.Show(True)
        wx.CallAfter(self.BootStrap)
        return True

    def BootStrap(self):
        # Add some shapes
        y = 30
        for x in range(30, 1200, 70):
            shape = ogl.RectangleShape( 60, 60 )
            shape.SetX(x)
            shape.SetY(y)
            self.shapecanvas.AddShape( shape )
            y += 70
        self.shapecanvas.GetDiagram().ShowAll( 1 )

    def onKeyChar(self, event):
        canvas = self.shapecanvas
        keycode = chr(event.GetKeyCode())
        if keycode == 'c':
            # The .Clear(dc) below always clears the top, physical size window
            # area - never the scrolled physical size window visible at the
            # moment (even though I have called prepareDC !!). This I think may
            # be a bug? And it never clears the whole virtual sized shape canvas
            # area.
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            canvas.GetDiagram().Clear(dc)

def main():
    application = MainApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()


