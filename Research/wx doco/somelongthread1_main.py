# simple front end to long running thread - so can have two frames at once
# which is what is problematic under linux and mac os x

import wx
import wx.lib.ogl as ogl

from somelongthread1 import MainFrame

class MainHost(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(250, 150))

        self.add_ogl_canvas()
        
        self.Centre()
        self.Show(True)

        wx.FutureCall(500, self.DrawLine)
        wx.FutureCall(1000, self.OpenSecondFrameWithThreadInside)

    def add_ogl_canvas(self):
        # Add OGL
        
        sizer = wx.BoxSizer( wx.VERTICAL )
        # put stuff into sizer

        self.canvas = canvas = ogl.ShapeCanvas( self )
        sizer.Add( canvas, 1, wx.GROW )

        canvas.SetBackgroundColour( "LIGHT BLUE" ) #

        diagram = ogl.Diagram()
        canvas.SetDiagram( diagram )
        diagram.SetCanvas( canvas )

        def setpos(shape, x, y):
            width, height = shape.GetBoundingBoxMax()
            shape.SetX( x + width/2 )
            shape.SetY( y + height/2 )
        def getpos(shape):
            width, height = shape.GetBoundingBoxMax()
            x = shape.GetX()
            y = shape.GetY()
            return (x - width/2, y - height/2)
        
        shape = ogl.RectangleShape( 60, 60 )
        setpos(shape, 0, 0)
        canvas.AddShape( shape )
        shape = ogl.RectangleShape( 60, 60 )
        setpos(shape, 60, 0)
        canvas.AddShape( shape )

        shape = ogl.RectangleShape( 60, 60 )
        setpos(shape, 120, 0)
        canvas.AddShape( shape )

        # Next row
        
        shape = ogl.RectangleShape( 100, 100 )
        setpos(shape, 0, 60)
        canvas.AddShape( shape )

        shape = ogl.RectangleShape( 100, 100 )
        setpos(shape, 100, 60)
        canvas.AddShape( shape )

        print [getpos(shape) for shape in canvas.GetDiagram().GetShapeList()]
        
        diagram.ShowAll( 1 )

        # apply sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        #self.Show(1)        
        

    def DrawLine(self):
        dc = wx.ClientDC(self.canvas)
        dc.DrawLine(50, 60, 190, 60)
        
        dc.DrawArc(50, 50, 50, 10, 20, 20) 
        dc.DrawEllipticArc(10,10, 50, 20, 0, 180)
        
        points = [wx.Point(10,10),wx.Point(15,55),wx.Point(40,30)]
        dc.DrawSpline(points)


    def OpenSecondFrameWithThreadInside(self):
        # Add opening of second frame here.
        #
        f = MainFrame(self, -1)
        f.Show(True)
        
        #b = LayoutBlackboard(graph=self.context.model.graph, umlwin=self.context.umlwin)
        #f.SetBlackboardObject(b)
        f.OnStart(None)
        

app = wx.App()
ogl.OGLInitialize()
MainHost(None, -1, 'Line')
app.MainLoop()

