import wx
from OGLlike import menuMaker, rand_bounds, rand_brush
from OGLlike import Diagram, Shape, ShapeCanvas, Connectable, Resizeable, Selectable

"""
Example of using my enhanced OGLlike library from the outside/another file.

Here I define a randomly coloured ellipse shape.

The next aim is to create a composite UML shape, however since I
found a fix to the ogl drag problem today, the urgency of continued
development of OGLlike has dissipated, for now.
"""


class EllipseShapeColoured(Shape):
    def __init__(self, x=20, y=20, x2=90, y2=90):
        Shape.__init__(self, [x, x2], [y, y2])
        self._width = x2 - x
        self._height = y2 - y

    def GetWidth(self):
        return self.x[1] - self.x[0]

    def GetHeight(self):
        return self.y[1] - self.y[0]

    def draw(self, dc):

        # Drawn so it fits inside rectangle
        dc.SetBrush(self.which_brush)
        dc.DrawEllipse(self.x[0], self.y[0], self.GetWidth(), self.GetHeight())

    def HitTest(self, x, y):
        # Crude copy of Rectangle test
        if x < self.x[0]:
            return False
        if x > self.x[1]:
            return False
        if y < self.y[0]:
            return False
        if y > self.y[1]:
            return False
        return True


class EllipseShapeAndy(EllipseShapeColoured, Connectable, Resizeable, Selectable):
    def __init__(self):
        x, y, x2, y2 = rand_bounds()
        EllipseShapeColoured.__init__(self, x, y, x2, y2)
        Resizeable.__init__(self)
        Connectable.__init__(self)
        # Attributable.__init__(self)
        # self.AddAttributes(['label', 'pen', 'fill', 'input', 'output'])
        # self.label = 'Block'
        self.which_brush = rand_brush()


class MyAppFrame(wx.Frame):
    def __init__(self, diagram):
        wx.Frame.__init__(self, None, -1, "Random coloured Ellipses using OGLlike", size=(500, 300))

        self.file = None
        menus = {}

        menus["&Add"] = [
            # ('Code\tCtrl+n', "Block that holds Python code", self.newCodeBlock),
            # ('Container\tCtrl+f', 'Container of blocks', self.newContBlock),
            # ('Point', 'Playing with points', self.newPointShape),
            # ('Lines', 'Plotting', self.newLinesShape),
            ("Ellipse\tCtrl+l", "Ellipse", self.newEllipseShape)
        ]

        menus["&Zoom"] = [
            ("Zoom In\tCtrl+o", "zoom in", self.zoomin),
            ("Zoom Out\tCtrl+p", "zoom out", self.zoomout),
        ]

        menuMaker(self, menus)

        # Canvas Stuff
        self.canvas = ShapeCanvas(self, -1)
        self.canvas.SetDiagram(diagram)
        self.canvas.SetBackgroundColour(wx.WHITE)

        self.canvas.SetScrollbars(1, 1, 600, 400)
        self.canvas.SetVirtualSize((600, 400))

        self.Show(True)

        # CMD-W to close Frame by attaching the key bind event to accellerator table
        randomId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=randomId)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("W"), randomId)])
        self.SetAcceleratorTable(accel_tbl)

    def OnCloseWindow(self, event):
        self.Destroy()

    def zoomin(self, event):
        self.canvas.scalex = max(self.canvas.scalex + 0.05, 0.3)
        self.canvas.scaley = max(self.canvas.scaley + 0.05, 0.3)

        # ANDY
        self.canvas.SetVirtualSize((1900, 1600))

        self.canvas.Refresh()

    def zoomout(self, event):
        self.canvas.scalex = self.canvas.scalex - 0.05
        self.canvas.scaley = self.canvas.scaley - 0.05
        self.canvas.Refresh()

    def newEllipseShape(self, event):
        # x, y, x2, y2 = rand_bounds()
        # i = EllipseShape(x, y, x2, y2)
        i = EllipseShapeAndy()  # random happens within
        self.canvas.InsertShape(i, 9999)
        self.canvas.deselect()
        self.canvas.Refresh()


class MainApp(wx.App):
    def OnInit(self):
        frame = MyAppFrame(Diagram())
        return True


##########################################

app = MainApp(0)
app.MainLoop()
