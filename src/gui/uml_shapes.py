# gui_umlshapes

from gui.settings import PRO_EDITION, LOCAL_OGL
import wx
if PRO_EDITION:
    import ogl2 as ogl
else:
    if LOCAL_OGL:
        import ogl
    else:
        import wx.lib.ogl as ogl


class DiamondShape(ogl.PolygonShape):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        if w == 0.0:
            w = 60.0
        if h == 0.0:
            h = 60.0

        points = [(0.0, -h / 2.0), (w / 2.0, 0.0), (0.0, h / 2.0), (-w / 2.0, 0.0)]

        self.Create(points)


# class RoundedRectangleShape(ogl.RectangleShape):
#     def __init__(self, w=0.0, h=0.0):
#         ogl.RectangleShape.__init__(self, w, h)
#         self.SetCornerRadius(-0.3)
#
#
# class CompositeDivisionShape(ogl.CompositeShape):
#     def __init__(self, canvas):
#         ogl.CompositeShape.__init__(self)
#
#         self.SetCanvas(canvas)
#
#         # create a division in the composite
#         self.MakeContainer()
#
#         # add a shape to the original division
#         shape2 = ogl.RectangleShape(40, 60)
#         self.GetDivisions()[0].AddChild(shape2)
#
#         # now divide the division so we get 2
#         self.GetDivisions()[0].Divide(wx.HORIZONTAL)
#
#         # and add a shape to the second division (and move it to the
#         # centre of the division)
#         shape3 = ogl.CircleShape(40)
#         shape3.SetBrush(wx.CYAN_BRUSH)
#         self.GetDivisions()[1].AddChild(shape3)
#         shape3.SetX(self.GetDivisions()[1].GetX())
#
#         for division in self.GetDivisions():
#             division.SetSensitivityFilter(0)
#
#
# class CompositeShape(ogl.CompositeShape):
#     def __init__(self, canvas):
#         ogl.CompositeShape.__init__(self)
#
#         self.SetCanvas(canvas)
#
#         constraining_shape = ogl.RectangleShape(120, 100)
#         constrained_shape1 = ogl.CircleShape(50)
#         constrained_shape2 = ogl.RectangleShape(80, 20)
#
#         constraining_shape.SetBrush(wx.BLUE_BRUSH)
#         constrained_shape2.SetBrush(wx.RED_BRUSH)
#
#         self.AddChild(constraining_shape)
#         self.AddChild(constrained_shape1)
#         self.AddChild(constrained_shape2)
#
#         constraint = ogl.Constraint(
#             ogl.CONSTRAINT_MIDALIGNED_BOTTOM,
#             constraining_shape,
#             [constrained_shape1, constrained_shape2],
#         )
#         self.AddConstraint(constraint)
#         self.Recompute()
#
#         # If we don't do this, the shapes will be able to move on their
#         # own, instead of moving the composite
#         constraining_shape.SetDraggable(False)
#         constrained_shape1.SetDraggable(False)
#         constrained_shape2.SetDraggable(False)
#
#         # If we don't do this the shape will take all left-clicks for itself
#         constraining_shape.SetSensitivityFilter(0)


class DividedShape(ogl.DividedShape):
    def __init__(self, width, height, canvas):
        ogl.DividedShape.__init__(self, width, height)

    def BuildRegions(self, canvas):
        region1 = ogl.ShapeRegion()
        region1.SetText("DividedShape")
        region1.SetProportions(0.0, 0.2)
        region1.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ)
        self.AddRegion(region1)

        region2 = ogl.ShapeRegion()
        region2.SetText("This is Region number two.")
        region2.SetProportions(0.0, 0.3)
        region2.SetFormatMode(ogl.FORMAT_NONE)
        # region2.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ|ogl.FORMAT_CENTRE_VERT)
        self.AddRegion(region2)

        region3 = ogl.ShapeRegion()

        region3.SetText("blah\nblah\nblah blah")
        region3.SetProportions(0.0, 0.5)
        region3.SetFormatMode(ogl.FORMAT_NONE)
        self.AddRegion(region3)

        # Andy Added
        self.region1 = region1  # for external access...
        self.region2 = region2  # for external access...
        self.region3 = region3  # for external access...

        self.SetRegionSizes()
        self.ReformatRegions(canvas)

    def FlushText(self):
        # Taken from Boa
        """This method retrieves the text from the shape
        regions and draws it. There seems to be a problem that
        the text is not normally drawn. """
        canvas = self.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        count = 0
        for region in self.GetRegions():
            region.SetFormatMode(4)
            self.FormatText(dc, region.GetText(), count)
            count = count + 1

    def ReformatRegions(self, canvas=None):
        rnum = 0
        if canvas is None:
            canvas = self.GetCanvas()
        dc = wx.ClientDC(canvas)  # used for measuring
        for region in self.GetRegions():
            text = region.GetText()
            # print("ReformatRegions", text)
            self.FormatText(dc, text, rnum)
            rnum += 1

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        ogl.DividedShape.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
        self.SetRegionSizes()
        self.ReformatRegions()
        self.GetCanvas().Refresh()


class DividedShapeSmall(DividedShape):
    def __init__(self, width, height, canvas):
        DividedShape.__init__(self, width, height, canvas)

    def BuildRegions(self, canvas):
        region1 = ogl.ShapeRegion()
        region1.SetText("wxDividedShapeSmall")
        region1.SetProportions(0.0, 0.9)
        region1.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ)
        self.AddRegion(region1)

        self.region1 = region1  # for external access...

        self.SetRegionSizes()
        self.ReformatRegions(canvas)

    def ReformatRegions(self, canvas=None):
        rnum = 0
        if canvas is None:
            canvas = self.GetCanvas()
        dc = wx.ClientDC(canvas)  # used for measuring
        for region in self.GetRegions():
            text = region.GetText()
            self.FormatText(dc, text, rnum)
            rnum += 1

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        ogl.DividedShape.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
        self.SetRegionSizes()
        self.ReformatRegions()
        self.GetCanvas().Refresh()


class BitmapShapeResizable(ogl.BitmapShape):
    """Draws a bitmap (andy's attempt at a resizable one)."""

    def __init__(self):
        ogl.BitmapShape.__init__(self)
        self._ori_bmp = None  # ANDY ADDED

    def ResetSize(self):  # ANDY ADDED
        if self._bitmap.IsOk():  # Returns True if bitmap data is present.
            w = int(self._ori_bmp.GetWidth()) # python 3.10 needs int
            h = int(self._ori_bmp.GetHeight()) # python 3.10 needs int
            self.SetSize(w, h)

    def SetSize(self, w, h, recursive=True):
        if self._bitmap.IsOk():

            # ANDY ADDED
            if self._bitmap.GetWidth() != w or self._bitmap.GetHeight() != h:
                img = self._ori_bmp.ConvertToImage()
                adjusted_img = img.Rescale(int(w), int(h), wx.IMAGE_QUALITY_HIGH) # python 3.10 needs ints
                bitmap = wx.Bitmap(adjusted_img)
                self._bitmap = (
                    bitmap
                )  # shape.SetBitmap(bitmap)  # don't call SetBitmap() cos it will infinite loop.  Plus don't want to destroy ori bmp info
            ##########

            w = self._bitmap.GetWidth()
            h = self._bitmap.GetHeight()

        self.SetAttachmentSize(w, h)

        self._width = w
        self._height = h

        self.SetDefaultRegionSize()

    def SetBitmap(self, bitmap):  # Override
        ogl.BitmapShape.SetBitmap(self, bitmap)
        self._ori_bmp = bitmap  # ANDY ADDED


# Comment Shape

# class DiamondShape(ogl.PolygonShape):
#     def __init__(self, w=0.0, h=0.0):
#         ogl.PolygonShape.__init__(self)
#         if w == 0.0:
#             w = 60.0
#         if h == 0.0:
#             h = 60.0
#
#         points = [ (0.0,    -h/2.0),
#                    (w/2.0,  0.0),
#                    (0.0,    h/2.0),
#                    (-w/2.0, 0.0),
#                    ]
#
#         self.Create(points)


class CommentShape(ogl.RectangleShape):
    def __init__(self, w=0.0, h=0.0):
        ogl.RectangleShape.__init__(self, w, h)
        # self.SetCornerRadius(-0.3)

    def OnDraw(self, dc):
        """The draw handler."""
        ogl.RectangleShape.OnDraw(self, dc)

        # print("drawing comment shape....")

        x1 = int(self._xpos - self._width / 2.0)
        y1 = int(self._ypos - self._height / 2.0)
        x2 = x1 + self._width
        y2 = y1 + self._height

        # simple box corner, but need to erase top right triangle portion of it - see below
        dc.DrawRectangle(int(x2 - 10), int(y1), 10, 10)

        """
        Bit of a hacky way of doing it - draw a triangle to make it appear that the
        top right corner of the desktop is visible, whereas it is not.
        The proper solution is not to draw a rectangle for the comment shape in the first place
        and leave the top right corner undrawn.  This will do for now, though.
        """
        my_points = [(x2, y1), (x2 - 10, y1), (x2, y1 + 10), (x2, y1)]
        uml_canvas_blue = wx.TheColourDatabase.Find("LIGHT BLUE")
        dc.SetBrush(wx.Brush(uml_canvas_blue))  # fill
        dc.SetPen(wx.Pen(uml_canvas_blue, 1, wx.PENSTYLE_SOLID))  # line
        dc.DrawPolygon(my_points)

        dc.SetPen(wx.Pen(wx.BLACK, 1, wx.PENSTYLE_SOLID))  # line
        dc.DrawLine(int(x2 - 10), int(y1), int(x2), int(y1 + 10))
