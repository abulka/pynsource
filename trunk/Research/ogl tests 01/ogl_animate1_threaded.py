# Andy's animation experiments
# learn about moving shapes and when refresh occurs

import wx
import wx.lib.ogl as ogl
import thread

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__( self,
                          None, -1, "Demo",
                          size=(500,300),
                          style=wx.DEFAULT_FRAME_STYLE )
        sizer = wx.BoxSizer( wx.VERTICAL )
        # put stuff into sizer

        self.oglcanvas = ogl.ShapeCanvas( self )
        sizer.Add( self.oglcanvas, 1, wx.GROW )

        self.oglcanvas.SetBackgroundColour( "LIGHT BLUE" )

        self.oglcanvas.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonEvent)

        diagram = ogl.Diagram()
        self.oglcanvas.SetDiagram( diagram )
        diagram.SetCanvas( self.oglcanvas )

        shape = ogl.CircleShape( 60.0 )
        self.mycircle = shape
        shape.SetX( 25.0 )             
        shape.SetY( 25.0 )             
        self.oglcanvas.AddShape( shape )
        diagram.ShowAll( 1 )           

        # apply sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Show(1)

        self.Start()

    def Start(self):
        self.need_abort = False
        thread.start_new_thread(self.DoSomeLongTask, ())
        
    def OnRightButtonEvent(self, event):
        if event.ShiftDown():
            print "aborting"
            self.need_abort = True
        else:
            self.Start()

    def DoSomeLongTask(self):
        import time

        for i in range(1,40):
            if self.need_abort:
                print "aborted."
                return
            wx.CallAfter(self.DoStuff)
            time.sleep(0.2)   # lets events through to the main wx thread and paints/messages get through ok
        print "Done."
            

    def DoStuff(self):
        print ".",
        TECHNIQUE = "simple" # "hybrid" # "smart" # "simple"
        shape = self.mycircle
        
        
        if TECHNIQUE == "simple":
            """
            Drawing Technique 1 - simplest.  Set x and redraw entire diagram.
            """
            shape.SetX(shape.GetX() + 5)
    
            canvas = shape.GetCanvas()
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            canvas.GetDiagram().Clear(dc)    # must have this to avoid smearing
            canvas.GetDiagram().Redraw(dc)
            
        elif TECHNIQUE == "smart":
            """
            Drawing Technique 2 - smartest. Set x/y via shape.Move(dc) and it
            draws. canvas.Refresh(...) invalidates old area. The only flaw is
            that you have to calculate the bounding area of old location.

            Note somewin.Refresh() is a call deep into wx itself. Not a method
            on shapecanvas but on wx.window itself. Marks the specified
            rectangle (or the whole window) as "dirty" so it will be repainted.
            Causes an EVT_PAINT event to be generated and sent to the window.
            !!!! doesn't this then potentially trigger an OnPaint and a redraw
            of the whole window anyway? Anyway, try commenting Refresh() out and
            see what happends - smearing!
            
            Also if after the move/refresh combo you don't hit the main message
            loop soon enough, then you will see one animation frame worth of smearing
            hence use wx.SafeYield() depending on where all this is being called from.
            """
            bx = shape.GetX()
            by = shape.GetY()
            bw, bh = shape.GetBoundingBoxMax()
            oldrect = wx.Rect(int(bx-bw/2)-1, int(by-bh/2)-1, int(bw)+2, int(bh)+2)
    
            canvas = shape.GetCanvas()  # ANDY NOTE - this is the ogl shapecanvas window
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
    
            shape.Move(dc, shape.GetX() + 15, shape.GetY(), display = True) # Redraw if display is TRUE.
            canvas.Refresh(False, oldrect)  # Refresh(self, bool eraseBackground=True, Rect rect=None)
            
            #wx.SafeYield() # give paint messages a chance to get through - don't need this in threaded version 
    
        elif TECHNIQUE == "hybrid":
            """
            Drawing Technique 3 - hybrid and silly. Set x/y via shape.Move(dc)
            and then diagram.Clear(dc) followed by diagram.Redraw(dc). What's
            the point of the shape.Move(dc) if you are going to erase everything
            anyway!! The only thing it does for you is set the x,y which is
            better done using the imple technique, above.
            """
            canvas = shape.GetCanvas()
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
    
            shape.Move(dc, shape.GetX() + 5, shape.GetY(), display = True) # Redraw if display is TRUE.  Doesn't seem to make a difference?
    
            canvas.GetDiagram().Clear(dc)    # must have this to avoid smearing
            canvas.GetDiagram().Redraw(dc)         

        
app = wx.PySimpleApp()
ogl.OGLInitialize()
frame = AppFrame()
app.MainLoop()
app.Destroy()