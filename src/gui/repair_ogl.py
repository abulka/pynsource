"""
Monkey Patch Repair of OGL Version. 1.1
Andy Bulka 2018.
abulka@gmail.com

The Problem
-----------
OGL doesn't draw shape outlines whilst interactively dragging shapes. Easily reproducible in the
official demos in the OGL section. You can drag/move shapes as normal, but you can't actually
see the shape outline move as you drag it. A disconcerting user experience. You only see the
shape in the new position when you drop (finish the drag move).
Ticket Submitted: See http://trac.wxwidgets.org/ticket/16311

The underlying cause
--------------------
The underlying cause of the problem is that ogl relies on dc.ClientDC to draw a drag outline
during drag and resize operations, but dc.ClientDC no longer works in phoenix esp. on Mac due
to underlying changes in operating system rendering technologies, apparently.
Discussion: https://groups.google.com/forum/#!topic/wxpython-mac/eprj62WlJAg

The solution
------------
This repair function replaces or enhances some specific methods of
    ogl.ShapeCanvas - on every mouse movement we get a true Refresh() and thus an
                      opportunity to re-paint the whole diagram properly using wx.PaintDC
    ogl.Shape - drag and resize operations cause the shape to actually move position or resize
                throughout the drag movement, thus allowing the shape to be drawn in
                its new position during each OnMouseEvent event's Refresh().
                A drag outline is no longer attempted.

As per the wxpython doco "A wx.ClientDC must be constructed if an application wishes to paint on
the client area of a window from outside an EVT_PAINT() handler.  To draw on a window from
within an EVT_PAINT() handler, construct a wx.PaintDC object instead."
The fix thus injects a much needed Refresh() after each OnMouseEvent which triggers a paint
which uses dc.PaintDC - which does work OK (unlike dc.ClientDC).

Whilst these repair changes are arguably inefficient they do actually solve the problem of
a broken ogl, and arguably achieve a nicer drag and resize effect - as you see the
actual shape being dragged, not just an outline.  And today's modern computers laugh
at the workload.

Installation
------------
Simply copy this file into your wxpython python project then add the following code to your project:

    from repair_ogl import repairOGL
    repairOGL()

For example, to fix the official wxwidgets demo available from https://extras.wxpython.org/wxPython4/extras/
edit the file "wxPython-demo-4.0.3/demo/OGL.py" and insert the above code fragment at the top.
Then run the demo as usual.

    cd wxPython-demo-4.0.3/demo
    pythonw demo.py

To find the OGL demo amongst all the examples click on OGL under the "Miscellaneous" category.

Future
------
Some operations still have redraw problems:

    - Dragging the region dividers of composite UML shapes.
    - Resizing the red Polygon in the official OGL demo.
    - Other cases?

These should be easy enough to track down and monkey patch in the same way as I have done here. The
basic idea is to find out which events are being called during these operations and patch them to
do the functionality of the associated 'End*' event instead of attempting a drag outline draw,
which fails.

Please contribute these fixes via github pull requests to

https://github.com/abulka/pynsource/blob/master/src/gui/repair_ogl.py

or email the updated repair_ogl.py file to me at abulka@gmail.com.

I am open to the idea that this module makes its way into the official wxPython-demo distribution
though arguably the actual relevant ogl files

    ...site-packages/wx/lib/ogl/canvas.py
    ...site-packages/wx/lib/ogl/basic.py

could be permanently changed using the code from this monkey path file, thus making the need for
the repair unecessary.  Probably this could happen once all the cases have been repaired and the
community is happy there are no unwanted side effects.

Background
----------
The initial reason for these changes is because I use ogl heavily in my
Pynsource UML tool for Python at http://www.pynsource.com
"""

from gui.settings import LOCAL_OGL
import wx
if LOCAL_OGL:
    import ogl
    print("Repair OGL - Using local ogl")
else:
    import wx.lib.ogl as ogl


def repairOGL():

    # general refresh hack

    old_OnMouseEvent = ogl.canvas.ShapeCanvas.OnMouseEvent

    def new_OnMouseEvent(self, event):

        # Original event handler causes a self.Draw() on the canvas
        # which clears the background canvas and does a self.GetDiagram().Redraw(dc)
        old_OnMouseEvent(self, event)

        if event.Dragging():
            # looks like a wx.ScrolledWindow C++ low level call - this is the magic that is needed
            self.Refresh()
        else:
            # wasted refresh avoided because not dragging...
            pass

    # moving

    def new_OnBeginDragLeft(self, x, y, keys=0, attachment=0):
        self.begin_drag_mouse_point = (x, y)
        self.begin_drag_shape_centre_point = (self.GetX(), self.GetY())

    def new_OnDragLeft(self, draw, x, y, keys=0, attachment=0):
        dx = self.begin_drag_mouse_point[0] - x
        dy = self.begin_drag_mouse_point[1] - y
        dc = wx.ClientDC(self.GetCanvas())
        self.GetCanvas().PrepareDC(dc)
        self.Move(
            dc,
            self.begin_drag_shape_centre_point[0] - dx,
            self.begin_drag_shape_centre_point[1] - dy,
        )

    def new_OnEndDragLeft(self, x, y, keys=0, attachment=0):
        pass

    # sizing

    old_OnSizingBeginDragLeft = ogl.basic.Shape.OnSizingBeginDragLeft
    old_OnSizingDragLeft = ogl.basic.Shape.OnSizingDragLeft
    old_OnSizingEndDragLeft = ogl.basic.Shape.OnSizingEndDragLeft

    def new_OnSizingBeginDragLeft(self, pt, x, y, keys=0, attachment=0):
        old_OnSizingBeginDragLeft(self, pt, x, y, keys=0, attachment=0)
        old_OnSizingDragLeft(self, pt, None, x, y, keys=0, attachment=0)  # 'draw' param is None

    def new_OnSizingDragLeft(self, pt, draw, x, y, keys=0, attachment=0):
        old_OnSizingDragLeft(self, pt, draw, x, y, keys=0, attachment=0)
        old_OnSizingEndDragLeft(self, pt, x, y, keys=0, attachment=0)

    # monkey patch new methods to replace existing ogl class methods

    ogl.canvas.ShapeCanvas.OnMouseEvent = new_OnMouseEvent
    ogl.basic.Shape.OnBeginDragLeft = new_OnBeginDragLeft
    ogl.basic.Shape.OnDragLeft = new_OnDragLeft
    ogl.basic.Shape.OnEndDragLeft = new_OnEndDragLeft
    ogl.basic.Shape.OnSizingBeginDragLeft = new_OnSizingBeginDragLeft
    ogl.basic.Shape.OnSizingDragLeft = new_OnSizingDragLeft
