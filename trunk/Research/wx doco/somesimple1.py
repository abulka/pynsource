# simple

import wx

class Line(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(250, 150))

        wx.FutureCall(1000, self.DrawLine)

        self.Centre()
        self.Show(True)

    def DrawLine(self):
        dc = wx.ClientDC(self)
        dc.DrawLine(50, 60, 190, 60)
        
        #dc.DrawArc(50, 50, 50, 10, 20, 20) 
        #dc.DrawEllipticArc(10,10, 50, 20, 0, 180)
        
        points = [wx.Point(10,10),wx.Point(15,55),wx.Point(40,30)]
        dc.DrawSpline(points)


app = wx.App()
Line(None, -1, 'Line')
app.MainLoop()
