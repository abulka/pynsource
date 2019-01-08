# common to ogl_scroll2 and ogl_official_demo1

import wx
import wx.lib.ogl as ogl
import random


def get_new_xy(shape):
    x = random.randint(1, 600)
    y = shape.GetY()
    width, height = shape.GetBoundingBoxMax()
    x += width / 2
    # y += height/2
    return x, y


"""
structure of classes is typically:
	wx.App -> wx.frame -> ogl.ShapeCanvas -> ogl.Diagram() -> shapes

"""

technique = "6"


def process_key(keycode, frame, canvas, shapes):

    if keycode == "m":

        shape = shapes[random.randint(0, len(shapes) - 1)]

        """
            prepareDc is related to scrolling and will adjust coords to take into account
            scrolled window scroll
            """
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        x, y = get_new_xy(shape)

        # shape.ClearText()
        # shape.AddText("%d,%d"%(x,y))

        global technique

        if technique == "2":
            """
                Effectiveness: Poor.  duplicates / smudges *everywhere* cos no clear

                Using shape.Move() to do the drawing. Note that shape.Move()
                will do a draw, unless you set display=False. The fact that we
                are passing in the existing x,y of the position the shape may
                seem redundant - which it is. But the shape.Move contains a call
                to self.Draw() which means we actually ARE triggering a shape
                draw Reason this smudges is that there is no .Clear going on.
                """
            #
            shape.SetX(x)
            shape.SetY(y)
            shape.Move(dc, shape.GetX(), shape.GetY())

        elif technique == "3":
            """
                Effectiveness: Poor.  duplicates / smudges cos no clear
                
                Using shape.Move() and moving the shape to the new coords.
                The default is display=True which means a draw occurs.
                """
            shape.Move(dc, x, y)

        elif technique == "4":
            """
                Effectiveness: Good. WOW this technique WORKS on scrolled area,
                bug fixed - BUT with provisos.

                Proviso: we remove the old shape with shape.Erase(dc) but
                this erase will clobber any overlapping shapes.
                """
            shape.Erase(dc)
            shape.Move(dc, x, y, display=True)

        elif technique == "1":
            """
                Effectiveness: Poor.  Scrolled area doesn't get cleared thus get
                duplicates / smudges there.
                
                We are not using shape.Move which means no draw is occurring
                within the move method. This is not a problem since the draw
                eventually happens in the diagram Redraw() (which loops and
                calls draw on each shape). The .Draw() methods operate correctly
                and draws on the canvas in any scrolled or non scrolled area,
                its just that we can't get rid of old rubbish using .Clear(dc).
                If .Clear(dc) at least cleared the currently visible scroll
                area, then that would be perfect. But it doesn't even though we
                have called canvas.PrepareDC(dc) which is supposed to do this.
                """
            shape.SetX(x)
            shape.SetY(y)
            shape.MoveLinks(dc)  # normally shape.Move() would have done this
            canvas.GetDiagram().Clear(dc)
            canvas.GetDiagram().Redraw(dc)

        elif technique == "5":
            """
                Effectiveness: Poor. smudges cos no clear not effective on
                scrolled areas. This is the long standing bug I was having.

                You might think that it is better perhaps to 
                    self.GetDiagram().Clear(dc)
                    self.GetDiagram().Redraw(dc)
                but this means you are drawing twice, once during the move and
                once in the redraw. you can move with display=False to avoid the
                extra draw.
                
                But the deeper problem is that the clear only clears the
                physical visible area and the scrolled off area still has
                content, so that when you scroll to it you get old rubbish
                there. e.g. if the shape that was moved was in the scrolled off
                area, you will see double - the old position and the new.
                """
            shape.Move(dc, x, y, display=False)
            canvas.GetDiagram().Clear(dc)
            canvas.GetDiagram().Redraw(dc)

        elif technique == "6":
            """
                Effectiveness: Excellent. BEST technique. this technique WORKS
                on scrolled area, bug fixed
                
                I discovered frame and canvas both have a Refresh() method.
                This seems to clear the whole virtual canvas area and repaints
                everything.
                
                OUTSTANDING QUESTION:
                Why isn't an eventual shape.draw() or diagram.redraw() needed
                anymore. DOES canvas.Refresh() SOMEHOW TRIGGER AN ACTUAL DRAW? I
                think yes. Tip: a Refresh() by default will erase the background
                before sending the paint event -- which then leads to a Draw.
                """
            shape.Move(dc, x, y, display=False)  # handles shape.MoveLinks(dc) internally too
            canvas.Refresh()  # or canvas.frame.Refresh()

        elif technique == "7":
            """
                Effectiveness: Very Bad - experimental only to demonstate a point.

                This technique shouldn't be used and only demonstrates the
                effect of .Clear(dc) after a .Refresh() - the clear only clears
                the physical visible area
                
                The .Refresh() above will be delayed till after the end of this
                method call, thus the subsequent .Clear(dc) below will take
                place first and then the erase/paint/draw cycle caused by the
                .Refresh() will kick in. Thus you won't see the effect of the
                clear. Unless you call canvas.Update() which lets wxpython
                "breathe" and allows the .Refresh() to occur immediately. Then
                you will see the effect of the clear.
                """
            shape.Move(dc, x, y, display=False)
            canvas.Refresh()
            canvas.Update()  # Allow .Refresh() to occur immediately

            canvas.GetDiagram().Clear(dc)

        elif technique == "8":
            """
                Effectiveness: Good - Traditional technique resurrected and repaired!

                Traditional non .Refresh() technique, but now taking into
                account R. Dunn's advice re NOT calling PrepareDC before a
                Clear() but of course calling it before the Move() and Redraw()
                Its arse about, but hey, it works!
                
                "The .Clear(dc) always clears the top, physical size window
                area - never the scrolled physical size window visible at the
                moment (even though I have called prepareDC !!). This I think may
                be a bug? And it never clears the whole virtual sized shape canvas
                area." - A. Bulka July 2012

                "Ok, I see it too. It's not quite expected but I'm not sure it's
                a bug as from some perspectives it is probably the correct thing
                to do... Anyway, a simple work around is to simply not call
                PrepareDC in that case. Then it will always be the physical
                window area that is cleared." - R. Dunn. July 2012.

                """
            dc = wx.ClientDC(canvas)
            canvas.GetDiagram().Clear(dc)

            canvas.PrepareDC(dc)
            shape.Move(dc, x, y, display=False)
            # you can even postpone the .PrepareDC(dc) till this point since no drawing has occurred yet
            canvas.GetDiagram().Redraw(dc)

        elif technique == "9":
            # SCRAPS FOR TESTING
            pass

            # WORKS
            # dc = wx.ClientDC(canvas)
            # canvas.GetDiagram().Clear(dc)
            #
            # shape.Move(dc, x, y, display=False)
            # canvas.PrepareDC(dc)
            # canvas.GetDiagram().Redraw(dc)

            # WRONG - need the .PrepareDC(dc) before the Move(dc, x, y) since by default it does a .Draw()
            # dc = wx.ClientDC(canvas)
            # canvas.GetDiagram().Clear(dc)
            #
            # shape.Move(dc, x, y)
            # canvas.PrepareDC(dc)
            # canvas.GetDiagram().Redraw(dc)

            # WRONG - without the Redraw, you only see the last moved shape, not all the shapes.
            # dc = wx.ClientDC(canvas)
            # canvas.GetDiagram().Clear(dc)
            #
            # canvas.PrepareDC(dc)
            # shape.Move(dc, x, y)

    elif keycode == "f":
        canvas.frame.SetDimensions(200, 200, 350, 350)  # get size with frame.GetSize()

    elif keycode == "r":
        canvas.frame.Refresh()

    elif keycode == "s":
        # Temporary frame resize hack to cause scrollbar to appear properly
        # probably causes .Refresh() but only if your ogl canvas is in a tab
        # of a notebook and there are at least two notebook pages. Whew!
        oldSize = frame.GetSize()
        frame.SetSize((oldSize[0] + 1, oldSize[1] + 1))
        frame.SetSize(oldSize)

    elif keycode == "c":
        # Aha - this does NOT clear the scrolled area!
        # even though I have prepareDC !!!!
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        canvas.GetDiagram().Clear(dc)

    elif keycode == "d":
        print("GetVirtualSize()", canvas.GetVirtualSize())
        print("frame.GetClientSize()", canvas.frame.GetClientSize())
        print("frame.GetSize()", canvas.frame.GetSize())

    elif keycode in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        technique = keycode

    elif keycode in ["b", "B"]:
        pass
