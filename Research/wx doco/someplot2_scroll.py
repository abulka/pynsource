import wx
import math

SCROLLBAR_WIDTH = 15


class CoordPanel(wx.ScrolledWindow):

    """A Cartesian coordinate panel.  Points can be plotted in Cartesian
coordinates; scrolling is enabled."""

    def __init__(
        self,
        parent,
        id=-1,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.HSCROLL | wx.VSCROLL,
        name="scrolledWindow",
        xRange=(-10, 10),
        yRange=(-10, 10),
        full_window=wx.DefaultSize,
        x_major=5,
        x_minor=1,
        y_major=5,
        y_minor=1,
    ):
        """
xRange and yRange define the [xmin, xmax]x[ymin, ymax] size of the
window.  full_window defines the total (virtual) number of pixels in the
window.  x_major and x_minor specify the major and minor tick marks in
the x-direction; likewise for y_major and y_minor."""

        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.UX, self.UY = full_window
        width, height = size
        if self.UX < width:
            self.UX = width
        if self.UY < height:
            self.UY = height
        self.SetScrollbars(pixelsPerUnitX=1, pixelsPerUnitY=1, noUnitsX=self.UX, noUnitsY=self.UY)

        self.xRange = xRange
        self.yRange = yRange
        self.SetScales()

        self.ticks = (x_major, x_minor, y_major, y_minor)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.NewAxes(None)
        self.NewGraph()

    def SetScales(self):
        """Set the ratio of pixels to units in the x and y directions."""

        first, last = self.xRange
        if first >= last:
            raise ValueError("Illegal xRange: %s" % (str(xRange)))
        self.dx = last - first

        first, last = self.yRange
        if first >= last:
            raise ValueError("Illegal yRange: %s" % (str(yRange)))
        self.dy = last - first

        self._ppx = self.UX / self.dx
        self._ppy = self.UY / self.dy

    def to_canvas(self, point):
        """Return canvas coords for cartesian pt (x0,y0)"""

        x0, y0 = point
        x = (x0 - self.xRange[0]) * self._ppx
        y = -(y0 - self.yRange[0]) * self._ppy + self.UY
        return (x, y)

    def to_cartesian(self, point):
        """Return cartesian coords for canvas pt (x0,y0)"""

        x0, y0 = point
        x = x0 / self._ppx + self.xRange[0]
        y = (self.UY - y0) / self._ppy + self.yRange[0]
        return (x, y)

    def DrawLine(self, x0, y0, x1, y1, pen):
        """Draw a line specified in Cartesian coordinates."""

        x0, y0 = self.to_canvas((x0, y0))
        x1, y1 = self.to_canvas((x1, y1))
        dc = wx.MemoryDC()
        dc.SelectObject(self._Graph)
        dc.SetPen(pen)
        dc.DrawLine(x0, y0, x1, y1)

    def DrawPoint(self, x0, y0, pen):
        """Draw a point specified in Cartesian coordinates."""

        x0, y0 = self.to_canvas((x0, y0))
        dc = wx.MemoryDC()
        dc.SelectObject(self._Graph)
        dc.SetPen(pen)
        dc.DrawPoint(x0, y0)

    def NewAxes(self, ticks=None):
        """Draw x- and y-axes with major and minor marks as specified by ticks,
a tuple of (x_major, x_minor, y_major, y_minor)."""

        self.TurnAxesOn()
        if ticks == None:
            ticks = self.ticks
        x_major, x_minor, y_major, y_minor = ticks

        self._Window = wx.EmptyBitmap(self.UX, self.UY)
        dc = wx.MemoryDC()
        dc.SetBackground(wx.LIGHT_GREY_BRUSH)
        dc.Clear()
        dc.SelectObject(self._Window)
        pen = wx.Pen("green", 1, wx.SOLID)
        dc.SetPen(pen)
        x0, y0 = self.to_canvas((self.xRange[0], 0))
        x1, y1 = self.to_canvas((self.xRange[1], 0))
        dc.DrawLine(x0, y0, x1, y1)

        x0, y0 = self.to_canvas((0, self.yRange[0]))
        x1, y1 = self.to_canvas((0, self.yRange[1]))
        dc.DrawLine(x0, y0, x1, y1)

        x = math.ceil(self.xRange[0] / x_minor) * x_minor
        endx = self.xRange[1]
        while x < endx:
            x0, y0 = self.to_canvas((x, 0))
            if x % x_major == 0:
                dc.DrawLine(x0, y0 + 8, x0, y0 - 8)
            else:
                dc.DrawLine(x0, y0 + 3, x0, y0 - 3)
            x += x_minor

        y = math.ceil(self.yRange[0] / y_minor) * y_minor
        endy = self.yRange[1]
        while y < endy:
            x0, y0 = self.to_canvas((0, y))
            if y % y_major == 0:
                dc.DrawLine(x0 + 8, y0, x0 - 8, y0)
            else:
                dc.DrawLine(x0 + 3, y0, x0 - 3, y0)
            y += y_minor

    def NewGraph(self):
        """Clear the graph area."""
        self._Graph = wx.EmptyBitmap(self.UX, self.UY)

    def TurnAxesOn(self):
        """Enable the axes on the display."""
        self._showaxes = True
        self.Refresh()

    def TurnAxesOff(self):
        """Disable the axes from the display."""
        self._showaxes = False
        self.Refresh()

    def ToggleAxes(self):
        """Toggle display of the axes."""
        self._showaxes = not self._showaxes
        self.Refresh()

    def OnPaint(self, event):
        """Show axes (if enabled) and graph."""
        dc = wx.BufferedPaintDC(self)
        self.DoPrepareDC(dc)
        if self._showaxes:
            dc.DrawBitmap(self._Window, 0, 0, useMask=False)
            self._Graph.SetMask(wx.Mask(self._Graph))
            dc.DrawBitmap(self._Graph, 0, 0, useMask=True)
        else:
            dc.DrawBitmap(self._Graph, 0, 0)

    def OnSize(self, event):
        """Resize graph area, stretching if necessary."""
        w, h = self.GetParent().GetClientSize()
        self.SetClientSize((w - SCROLLBAR_WIDTH, h - SCROLLBAR_WIDTH))
        if w <= self.UX and h <= self.UY:
            pass
        else:
            self.SetClientSize((w, h))
            self.UX = w
            self.UY = h
            self.SetScales()
            self.NewAxes()
            self.NewGraph()
            self.Refresh()


class GraphPanel(CoordPanel):

    """
A demo subclass of CoordPanel that graphs a single function.
Left-click draws the function in dot mode; right click in line mode.
The middle mouse button toggles the axes on and off."""

    def __init__(
        self,
        parent,
        id=-1,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.HSCROLL | wx.VSCROLL,
        name="scrolledWindow",
        xRange=(-10, 10),
        yRange=(-10, 10),
        full_window=wx.DefaultSize,
        x_major=5,
        x_minor=1,
        y_major=5,
        y_minor=1,
        func=lambda x: x * x,
    ):
        CoordPanel.__init__(
            self,
            parent,
            id,
            pos,
            size,
            style,
            name,
            xRange,
            yRange,
            full_window,
            x_major,
            x_minor,
            y_major,
            y_minor,
        )
        self.Bind(wx.EVT_LEFT_UP, self.MouseClick)
        self.Bind(wx.EVT_RIGHT_UP, self.MouseClick)
        self.Bind(wx.EVT_MIDDLE_UP, lambda e: self.ToggleAxes())
        self.last_style = None
        self.func = func

    def DrawDotFunc(self, func):
        """Draw function in dot style."""
        self.last_style = "dot"
        x = self.xRange[0]
        dx = 0.1
        pen = wx.Pen("green", 1, wx.SOLID)
        while x < self.xRange[1]:
            try:
                y = func(x)
            except:
                pass
            else:
                self.DrawPoint(x, y, pen)
            x += dx

    def DrawLineFunc(self, func):
        """Draw function in connected-line style."""
        self.last_style = "line"
        x = self.xRange[0]
        dx = 0.1
        pen = wx.Pen("green", 1, wx.SOLID)

        old_x = x
        try:
            old_y = func(x)
        except:
            old_y = 0
        while x < self.xRange[1]:
            try:
                y = func(x)
            except:
                pass
            else:
                self.DrawLine(x, y, old_x, old_y, pen)
                old_y = y
            old_x = x

            x += dx

    def MouseClick(self, event):
        if not event:
            print("there!")
            return
        self.last_event = event
        self.NewGraph()
        if event.LeftUp():
            self.DrawDotFunc(self.func)
        elif event.RightUp():
            self.DrawLineFunc(self.func)
        self.Refresh()

    def OnSize(self, event):
        w, h = self.GetParent().GetClientSize()
        self.SetClientSize((w - SCROLLBAR_WIDTH, h - SCROLLBAR_WIDTH))
        if w <= self.UX and h <= self.UY:
            pass
        else:
            self.SetClientSize((w, h))
            self.UX = w
            self.UY = h
            self.SetScrollbars(
                pixelsPerUnitX=1, pixelsPerUnitY=1, noUnitsX=self.UX, noUnitsY=self.UY
            )
            self.SetScales()
            if self._showaxes:
                self.NewAxes()
            self.NewGraph()

            if self.last_style == "dot":
                self.DrawDotFunc(self.func)
            elif self.last_style == "line":
                self.DrawLineFunc(self.func)
            self.Refresh()


if __name__ == "__main__":
    app = wx.PySimpleApp(0)

    app.frame = wx.Frame(parent=None)
    app.frame.sizer = wx.BoxSizer(orient=wx.VERTICAL)
    app.frame.SetSizer(app.frame.sizer)
    app.coords = GraphPanel(
        parent=app.frame, size=(390, 400), full_window=(500, 500), func=lambda x: x * x
    )
    app.frame.sizer.Add(app.coords)
    app.frame.Bind(wx.EVT_SIZE, app.coords.OnSize)

    app.frame.SetTitle("Coordinate Canvas 1.0")
    app.frame.Show()
    app.MainLoop()
