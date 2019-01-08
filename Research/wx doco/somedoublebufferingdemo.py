# -*- coding: iso-8859-1 -*-#

#!/usr/bin/env python

import wx
import random

# This has been set up to optionally use the wx.BufferedDC if
# USE_BUFFERED_DC is True, it will be used. Otherwise, it uses the raw
# wx.Memory DC , etc.

USE_BUFFERED_DC = False
# USE_BUFFERED_DC = True


class BufferedWindow(wx.Window):

    """

    A Buffered window class.

    To use it, subclass it and define a Draw(DC) method that takes a DC
    to draw to. In that method, put the code needed to draw the picture
    you want. The window will automatically be double buffered, and the
    screen will be automatically updated when a Paint event is received.

    When the drawing needs to change, you app needs to call the
    UpdateDrawing() method. Since the drawing is stored in a bitmap, you
    can also save the drawing to file by calling the
    SaveToFile(self, file_name, file_type) method.

    """

    def __init__(self, *args, **kwargs):
        # make sure the NO_FULL_REPAINT_ON_RESIZE style flag is set.
        kwargs["style"] = (
            kwargs.setdefault("style", wx.NO_FULL_REPAINT_ON_RESIZE) | wx.NO_FULL_REPAINT_ON_RESIZE
        )
        wx.Window.__init__(self, *args, **kwargs)

        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_SIZE(self, self.OnSize)

        # OnSize called to make sure the buffer is initialized.
        # This might result in OnSize getting called twice on some
        # platforms at initialization, but little harm done.
        self.OnSize(None)
        self.paint_count = 0

    def Draw(self, dc):
        ## just here as a place holder.
        ## This method should be over-ridden when subclassed
        pass

    def OnPaint(self, event):
        # All that is needed here is to draw the buffer to screen
        if USE_BUFFERED_DC:
            dc = wx.BufferedPaintDC(self, self._Buffer)
        else:
            dc = wx.PaintDC(self)
            dc.DrawBitmap(self._Buffer, 0, 0)

    def OnSize(self, event):
        # The Buffer init is done here, to make sure the buffer is always
        # the same size as the Window
        # Size  = self.GetClientSizeTuple()
        Size = self.ClientSize

        # Make new offscreen bitmap: this bitmap will always have the
        # current drawing in it, so it can be used to save the image to
        # a file, or whatever.
        self._Buffer = wx.EmptyBitmap(*Size)
        self.UpdateDrawing()

    def SaveToFile(self, FileName, FileType=wx.BITMAP_TYPE_PNG):
        ## This will save the contents of the buffer
        ## to the specified file. See the wxWindows docs for
        ## wx.Bitmap::SaveFile for the details
        self._Buffer.SaveFile(FileName, FileType)

    def UpdateDrawing(self):
        """
        This would get called if the drawing needed to change, for whatever reason.

        The idea here is that the drawing is based on some data generated
        elsewhere in the system. If that data changes, the drawing needs to
        be updated.

        This code re-draws the buffer, then calls Update, which forces a paint event.
        """
        dc = wx.MemoryDC()
        dc.SelectObject(self._Buffer)
        self.Draw(dc)
        del dc  # need to get rid of the MemoryDC before Update() is called.
        self.Refresh()
        self.Update()


class DrawWindow(BufferedWindow):
    def __init__(self, *args, **kwargs):
        ## Any data the Draw() function needs must be initialized before
        ## calling BufferedWindow.__init__, as it will call the Draw
        ## function.
        self.DrawData = {}
        BufferedWindow.__init__(self, *args, **kwargs)

    def Draw(self, dc):
        dc.SetBackground(wx.Brush("White"))
        dc.Clear()  # make sure you clear the bitmap!

        # Here's the actual drawing code.
        for key, data in list(self.DrawData.items()):
            if key == "Rectangles":
                dc.SetBrush(wx.BLUE_BRUSH)
                dc.SetPen(wx.Pen("VIOLET", 4))
                for r in data:
                    dc.DrawRectangle(*r)
            elif key == "Ellipses":
                dc.SetBrush(wx.Brush("GREEN YELLOW"))
                dc.SetPen(wx.Pen("CADET BLUE", 2))
                for r in data:
                    dc.DrawEllipse(*r)
            elif key == "Polygons":
                dc.SetBrush(wx.Brush("SALMON"))
                dc.SetPen(wx.Pen("VIOLET RED", 4))
                for r in data:
                    dc.DrawPolygon(r)


class TestFrame(wx.Frame):
    def __init__(self, parent=None):
        wx.Frame.__init__(
            self,
            parent,
            size=(500, 500),
            title="Double Buffered Test",
            style=wx.DEFAULT_FRAME_STYLE,
        )

        ## Set up the MenuBar
        MenuBar = wx.MenuBar()

        file_menu = wx.Menu()

        item = file_menu.Append(wx.ID_EXIT, text="&Exit")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        MenuBar.Append(file_menu, "&File")

        draw_menu = wx.Menu()
        item = draw_menu.Append(wx.ID_ANY, "&New Drawing", "Update the Drawing Data")
        self.Bind(wx.EVT_MENU, self.NewDrawing, item)
        item = draw_menu.Append(wx.ID_ANY, "&Save Drawing\tAlt-I", "")
        self.Bind(wx.EVT_MENU, self.SaveToFile, item)
        MenuBar.Append(draw_menu, "&Draw")

        self.SetMenuBar(MenuBar)
        self.Window = DrawWindow(self)
        self.Show()
        # Initialize a drawing -- it has to be done after Show() is called
        #   so that the Windows has teh right size.
        self.NewDrawing()

    def OnQuit(self, event):
        self.Close(True)

    def NewDrawing(self, event=None):
        self.Window.DrawData = self.MakeNewData()
        self.Window.UpdateDrawing()

    def SaveToFile(self, event):
        dlg = wx.FileDialog(
            self,
            "Choose a file name to save the image as a PNG to",
            defaultDir="",
            defaultFile="",
            wildcard="*.png",
            style=wx.SAVE,
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.Window.SaveToFile(dlg.GetPath(), wx.BITMAP_TYPE_PNG)
        dlg.Destroy()

    def MakeNewData(self):
        ## This method makes some random data to draw things with.
        MaxX, MaxY = self.Window.GetClientSizeTuple()
        DrawData = {}

        # make some random rectangles
        l = []
        for i in range(5):
            w = random.randint(1, MaxX / 2)
            h = random.randint(1, MaxY / 2)
            x = random.randint(1, MaxX - w)
            y = random.randint(1, MaxY - h)
            l.append((x, y, w, h))
        DrawData["Rectangles"] = l

        # make some random ellipses
        l = []
        for i in range(5):
            w = random.randint(1, MaxX / 2)
            h = random.randint(1, MaxY / 2)
            x = random.randint(1, MaxX - w)
            y = random.randint(1, MaxY - h)
            l.append((x, y, w, h))
        DrawData["Ellipses"] = l

        # Polygons
        l = []
        for i in range(3):
            points = []
            for j in range(random.randint(3, 8)):
                point = (random.randint(1, MaxX), random.randint(1, MaxY))
                points.append(point)
            l.append(points)
        DrawData["Polygons"] = l

        return DrawData


class DemoApp(wx.App):
    def OnInit(self):
        frame = TestFrame()
        self.SetTopWindow(frame)

        return True


if __name__ == "__main__":
    app = DemoApp(0)
    app.MainLoop()
