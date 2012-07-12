# mouse chasing circle
# http://wiki.wxpython.org/wxOGL

import wx
import wx.lib.ogl as ogl
import time

CLICK_TO_DRAG = False

if CLICK_TO_DRAG:
        class MyEvtHandler(ogl.ShapeEvtHandler):
                """
                Overwrite the default event handler to implement some custom features. 
                """
                def __init__(self):
                        ogl.ShapeEvtHandler.__init__(self)
        
                def OnLeftClick(self, x, y, keys = 0, attachment = 0):
                        """
                        The dragging is done here. 
                        """
                        shape = self.GetShape()
                        print shape.__class__, shape.GetClassName(), shape.a
                        canvas = shape.GetCanvas()
                        dc = wx.ClientDC(canvas)
                        canvas.PrepareDC(dc)
        
                        if shape.Selected():
                                shape.Select(False, dc)
                                canvas.Redraw(dc)
                        else:
                                redraw = False
                                shapeList = canvas.GetDiagram().GetShapeList()
                                toUnselect = []
                                for s in shapeList:
                                        if s.Selected():
                                                toUnselect.append(s)
        
                                shape.Select(True, dc)
        
                                if toUnselect:
                                        for s in toUnselect:
                                                s.Select(False, dc)
                                        canvas.Redraw(dc)
        


class OGLCanvas(ogl.ShapeCanvas):
        def __init__(self, parent, frame):
                ogl.ShapeCanvas.__init__(self, parent)

                self.SetBackgroundColour("LIGHT BLUE")
                self.diagram = ogl.Diagram()
                self.SetDiagram(self.diagram)
                self.diagram.SetCanvas(self)

                self.circle = ogl.CircleShape(100)
                #self.circle.SetCanvas(self)            # not necessary !! - should adjust the wiki at http://wiki.wxpython.org/wxOGL
                self.circle.a="Circle identified"
                self.diagram.AddShape(self.circle)
                self.circle.Show(True)

                self.working = False  # ANDY

                if CLICK_TO_DRAG:
                        self.evthandler = MyEvtHandler()
                        self.evthandler.SetShape(self.circle)
                        self.evthandler.SetPreviousHandler(self.circle.GetEventHandler())
                        self.circle.SetEventHandler(self.evthandler)
                else:
                        self.Bind(wx.EVT_MOTION, self.OnMotion, self)

        def OnMotion(self, event):
                if self.working:        # wx.Yield() re-entry protection.  Don't need this if use wx.SafeYield()  # http://wxpython-users.1045709.n5.nabble.com/wx-Yield-wx-SafeYield-wx-App-Yield-td2371477.html
                        event.Skip()
                        return
                self.working = False
                
                shape = self.circle

                bx = shape.GetX()
                by = shape.GetY()
                bw, bh = shape.GetBoundingBoxMax()
                oldrect = wx.Rect(int(bx-bw/2)-1, int(by-bh/2)-1, int(bw)+2, int(bh)+2)

                canvas = shape.GetCanvas()  # ANDY NOTE - this is the ogl shapecanvas window
                dc = wx.ClientDC(canvas)
                canvas.PrepareDC(dc)

                shape.Move(dc, event.GetPosition()[0], event.GetPosition()[1], display = True) # Redraw if display is TRUE.

                """
                ANDY NOTE:
                
                somewin.Refresh() is a call deep into wx itself.
                
                Mark the specified rectangle (or the whole window) as "dirty" so it
                will be repainted.  Causes an EVT_PAINT event to be generated and sent
                to the window.
                
                try commenting it out and see what happends - smearing!
                """
                canvas.Refresh(False, oldrect)  # Refresh(self, bool eraseBackground=True, Rect rect=None)

                # but the YieldIfNeeded() fights back against the sleep() and
                # the screen refreshes - any pending window events will be
                # dispatched (permitting the window to refresh, process button
                # presses, etc...). since all events go through during the
                # wxYield() you need to protect against trying to run the same
                # operation twice.
                wx.Yield()
                #wx.SafeYield()
                
                time.sleep(0.2)  # introduce a slight lag here (or even before the refresh) and a slight smearing will occur
                
                





                """
                ANDY experimental redraw the entire thing test - works but slower performance
                """
                #dc = wx.ClientDC(self)
                ##self.PrepareDC(dc)
                #self.GetDiagram().Clear(dc)    # must have this to avoid smearing
                #self.GetDiagram().Redraw(dc)                




                event.Skip()
                self.working = False

class OGLFrame(wx.Frame):
        def __init__(self, *args, **kwds):
                wx.Frame.__init__(self, *args, **kwds)

                self.SetTitle("OGL TEST")
                self.SetBackgroundColour(wx.Colour(8, 197, 248))
                self.canvas = OGLCanvas(self, self)

if __name__ == "__main__":
        app = wx.PySimpleApp(False)
        wx.InitAllImageHandlers()
        ogl.OGLInitialize()
        frame = OGLFrame(None, -1, "")
        app.SetTopWindow(frame)
        frame.Show(True)
        app.MainLoop()