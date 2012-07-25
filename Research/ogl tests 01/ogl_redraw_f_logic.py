# common to ogl_scroll2 and ogl_official_demo1

import wx
import wx.lib.ogl as ogl
import random

def get_new_xy(shape):
    x = random.randint(1,600)
    y = shape.GetY()
    width, height = shape.GetBoundingBoxMax()
    x += width/2
    #y += height/2
    return x,y

"""
structure of classes is typically:
	wx.App -> wx.frame -> ogl.ShapeCanvas -> ogl.Diagram() -> shapes

"""

technique = '7'

def process_key(keycode, frame, canvas, shapes):
        
        if keycode == 'm':
         
            shape = shapes[random.randint(0,len(shapes)-1)]
            
            """
            prepareDc is related to scrolling and will adjust coords to take into account
            scrolled window scroll
            """
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)

            x,y = get_new_xy(shape)

            #shape.ClearText()
            #shape.AddText("%d,%d"%(x,y))            
            
            global technique
            if technique == '1':
                """
                We are not using shape.Move which means no
                draw is occurring within the move method.
                
                But the draw eventually happens in the diagram Redraw()
                (which loops and calls draw on each shape)
                
                a draw means its drawn on the canvas in any scrolled or non scrolled area
                """
                # Scrolled area doesn't get cleared thus get
                # duplicates / smudges there
                shape.SetX(x)
                shape.SetY(y)
                canvas.GetDiagram().Clear(dc)
                canvas.GetDiagram().Redraw(dc)
                
            elif technique == '2':
                """
                Using shape.Move()
                
                shape.Move will do a draw, unless you set display=False
                
                The fact that we are moving to the position the shape
                already is may seem redundant - which it is.  But the
                shape.Move contains a call to self.draw which means
                we are triggering the shape draw
                """
                # duplicates / smudges *everywhere* cos no clear
                shape.SetX(x)
                shape.SetY(y)
                shape.Move(dc, shape.GetX(), shape.GetY())
        
            elif technique == '3':
                """
                Using shape.Move() and moving the shape to the new coords.
                The default is display=True which means a draw occurs.
                """
                # duplicates / smudges cos no clear
                shape.Move(dc, x, y)

            elif technique == '4':
                """
                you can remove the old shape with 
                shape.Erase(dc)
                but this erase will clobber any overlapping shapes.
                """
                # WOW this technique WORKS on scrolled area, bug fixed - BUT with provisos.
                shape.Erase(dc)
                shape.Move(dc, x, y, display=True)

            elif technique == '5':
                """
                better perhaps to 
                        self.GetDiagram().Clear(dc)
                        self.GetDiagram().Redraw(dc)
                but this means you are drawing twice, once during the move and once in the redraw.
                you can move with display=False to avoid the extra draw.
                
                But the deeper problem
                is that the clear only clears the physical visible area and the scrolled off area
                still has content, so that when you scroll to it you get old rubbish there. e.g.
                if the shape that was moved was in the scrolled off area, you will see double - the
                old position and the new.
                """
                shape.Move(dc, x, y, display=False)
                canvas.GetDiagram().Clear(dc)
                canvas.GetDiagram().Redraw(dc)

            elif technique == '6':
                """
                Then I discovered frame and canvas both have a Refresh() method.  This seems to clear
                the whole virtual canvas area and repaints everything.
                """
                # WOW this technique WORKS on scrolled area, bug fixed
                shape.Move(dc, x, y)
                canvas.frame.Refresh()
            
            elif technique == '7':
                # WOW this technique WORKS on scrolled area, bug fixed, handles links too
                shape.Move(dc, x, y)
                shape.MoveLinks(dc)
                canvas.Refresh()

        elif keycode == 'f':
            canvas.frame.SetDimensions(200, 200, 350, 350) # get size with frame.GetSize()
            
        elif keycode == 'r':
            canvas.frame.Refresh()
            
        elif keycode == 'c':
            # Aha - this does NOT clear the scrolled area!
            # even though I have prepareDC !!!!
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            canvas.GetDiagram().Clear(dc)
            
        elif keycode == 'd':
            print "GetVirtualSize()", canvas.GetVirtualSize()
            print "frame.GetClientSize()", canvas.frame.GetClientSize()
            print "frame.GetSize()", canvas.frame.GetSize()
        
        elif keycode in ['1','2','3','4','5','6','7','8']:
            technique = keycode

        elif keycode in ['b', 'B']:
            pass
