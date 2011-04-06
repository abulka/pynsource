import wx
import wx.lib.ogl as ogl


class DiamondShape(ogl.PolygonShape):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        if w == 0.0:
            w = 60.0
        if h == 0.0:
            h = 60.0

        points = [ (0.0,    -h/2.0),
                   (w/2.0,  0.0),
                   (0.0,    h/2.0),
                   (-w/2.0, 0.0),
                   (0.0,    h/3.0),
                   
                   ]

        self.Create(points)

class Andy1Shape(ogl.PolygonShape):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        points = [ (0.0,    -h/2.0),
                   (w/2.0,  0.0),
                   (0.0,    h/2.0),
                   (-w/2.0, 0.0),
                   ]
        self.Create(points)
        
        
class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__( self,
                          None, -1, "Demo",
                          size=(500,400),
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
        
        shape = ogl.RectangleShape( 160, 60 )
        shape.SetTextColour('RED')
        setpos(shape, 160, 50)
        canvas.AddShape( shape )
        shape.AddText("Hello there")


        print [getpos(shape) for shape in canvas.GetDiagram().GetShapeList()]
        
        
        F = 'img_uml01.png'
        # wx.ImageFromBitmap(bitmap) and wx.BitmapFromImage(image)
        shape = ogl.BitmapShape()
        img = wx.Image(F, wx.BITMAP_TYPE_ANY)
        bmp = wx.BitmapFromImage(img)
        shape.SetBitmap(bmp)
        setpos(shape, 100, 260)
        canvas.AddShape( shape )
        
        
        shape = DiamondShape()
        setpos(shape, 10, 260)
        canvas.AddShape( shape )
        
        shape = Andy1Shape(100,40)
        setpos(shape,11, 111)
        canvas.AddShape( shape )

        
        
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
