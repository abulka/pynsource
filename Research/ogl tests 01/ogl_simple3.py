import wx
import wx.lib.ogl as ogl

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__( self,
                          None, -1, "Demo",
                          size=(300,200),
                          style=wx.DEFAULT_FRAME_STYLE )
        sizer = wx.BoxSizer( wx.VERTICAL )
        # put stuff into sizer

        canvas = ogl.ShapeCanvas( self )
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
        self.Show(1)



app = wx.PySimpleApp()
ogl.OGLInitialize()
frame = AppFrame()
app.MainLoop()
app.Destroy()
