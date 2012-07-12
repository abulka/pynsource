# doodle.py

'''
This module contains the DoodleWindow class which is a window that you
can do simple drawings upon.
'''

import wx


class DoodleWindow(wx.Window):
    colours = ['Black', 'Yellow', 'Red', 'Green', 'Blue', 'Purple',
        'Brown', 'Aquamarine', 'Forest Green', 'Light Blue', 'Goldenrod',
        'Cyan', 'Orange', 'Navy', 'Dark Grey', 'Light Grey']

    thicknesses = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128]

    def __init__(self, parent):
        super(DoodleWindow, self).__init__(parent,
            style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.initDrawing()
        self.makeMenu()
        self.bindEvents()
        self.initBuffer()

    def initDrawing(self):
        self.SetBackgroundColour('WHITE')
        self.currentThickness = self.thicknesses[0]
        self.currentColour = self.colours[0]
        self.lines = []
        self.previousPosition = (0, 0)

    def bindEvents(self):
        for event, handler in [ \
                (wx.EVT_LEFT_DOWN, self.onLeftDown), # Start drawing
                (wx.EVT_LEFT_UP, self.onLeftUp),     # Stop drawing 
                (wx.EVT_MOTION, self.onMotion),      # Draw
                (wx.EVT_RIGHT_UP, self.onRightUp),   # Popup menu
                (wx.EVT_SIZE, self.onSize),          # Prepare for redraw
                (wx.EVT_IDLE, self.onIdle),          # Redraw
                (wx.EVT_PAINT, self.onPaint),        # Refresh
                (wx.EVT_WINDOW_DESTROY, self.cleanup)]:
            self.Bind(event, handler)

    def initBuffer(self):
        ''' Initialize the bitmap used for buffering the display. '''
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.drawLines(dc, *self.lines)
        self.reInitBuffer = False

    def makeMenu(self):
        ''' Make a menu that can be popped up later. '''
        self.menu = wx.Menu()
        self.idToColourMap = self.addCheckableMenuItems(self.menu,
            self.colours)
        self.bindMenuEvents(menuHandler=self.onMenuSetColour,
            updateUIHandler=self.onCheckMenuColours,
            ids=self.idToColourMap.keys())
        self.menu.Break() # Next menu items go in a new column of the menu
        self.idToThicknessMap = self.addCheckableMenuItems(self.menu,
            self.thicknesses)
        self.bindMenuEvents(menuHandler=self.onMenuSetThickness,
            updateUIHandler=self.onCheckMenuThickness,
            ids=self.idToThicknessMap.keys())

    @staticmethod
    def addCheckableMenuItems(menu, items):
        ''' Add a checkable menu entry to menu for each item in items. This
            method returns a dictionary that maps the menuIds to the
            items. '''
        idToItemMapping = {}
        for item in items:
            menuId = wx.NewId()
            idToItemMapping[menuId] = item
            menu.Append(menuId, str(item), kind=wx.ITEM_CHECK)
        return idToItemMapping

    def bindMenuEvents(self, menuHandler, updateUIHandler, ids):
        ''' Bind the menu id's in the list ids to menuHandler and
            updateUIHandler. '''
        sortedIds = sorted(ids)
        firstId, lastId = sortedIds[0], sortedIds[-1]
        for event, handler in \
                [(wx.EVT_MENU_RANGE, menuHandler),
                 (wx.EVT_UPDATE_UI_RANGE, updateUIHandler)]:
            self.Bind(event, handler, id=firstId, id2=lastId)

    # Event handlers:

    def onLeftDown(self, event):
        ''' Called when the left mouse button is pressed. '''
        self.currentLine = []
        self.previousPosition = event.GetPositionTuple()
        self.CaptureMouse()

    def onLeftUp(self, event):
        ''' Called when the left mouse button is released. '''
        if self.HasCapture():
            self.lines.append((self.currentColour, self.currentThickness,
                self.currentLine))
            self.currentLine = []
            self.ReleaseMouse()

    def onRightUp(self, event):
        ''' Called when the right mouse button is released, will popup
            the menu. '''
        self.PopupMenu(self.menu)

    def onMotion(self, event):
        ''' Called when the mouse is in motion. If the left button is
            dragging then draw a line from the last event position to the
            current one. Save the coordinants for redraws. '''
        if event.Dragging() and event.LeftIsDown():
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            currentPosition = event.GetPositionTuple()
            lineSegment = self.previousPosition + currentPosition
            self.drawLines(dc, (self.currentColour, self.currentThickness,
                [lineSegment]))
            self.currentLine.append(lineSegment)
            self.previousPosition = currentPosition

    def onSize(self, event):
        ''' Called when the window is resized. We set a flag so the idle
            handler will resize the buffer. '''
        self.reInitBuffer = True

    def onIdle(self, event):
        ''' If the size was changed then resize the bitmap used for double
            buffering to match the window size.  We do it in Idle time so
            there is only one refresh after resizing is done, not lots while
            it is happening. '''
        if self.reInitBuffer:
            self.initBuffer()
            self.Refresh(False)

    def onPaint(self, event):
        ''' Called when the window is exposed. '''
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        dc = wx.BufferedPaintDC(self, self.buffer)

    def cleanup(self, event):
        if hasattr(self, "menu"):
            self.menu.Destroy()
            del self.menu

    # These two event handlers are called before the menu is displayed
    # to determine which items should be checked.
    def onCheckMenuColours(self, event):
        colour = self.idToColourMap[event.GetId()]
        event.Check(colour == self.currentColour)

    def onCheckMenuThickness(self, event):
        thickness = self.idToThicknessMap[event.GetId()]
        event.Check(thickness == self.currentThickness)

    # Event handlers for the popup menu, uses the event ID to determine
    # the colour or the thickness to set.
    def onMenuSetColour(self, event):
        self.currentColour = self.idToColourMap[event.GetId()]

    def onMenuSetThickness(self, event):
        self.currentThickness = self.idToThicknessMap[event.GetId()]

    # Other methods
    @staticmethod
    def drawLines(dc, *lines):
        ''' drawLines takes a device context (dc) and a list of lines
        as arguments. Each line is a three-tuple: (colour, thickness,
        linesegments). linesegments is a list of coordinates: (x1, y1,
        x2, y2). '''
        dc.BeginDrawing()
        for colour, thickness, lineSegments in lines:
            pen = wx.Pen(wx.NamedColour(colour), thickness, wx.SOLID)
            dc.SetPen(pen)
            for lineSegment in lineSegments:
                dc.DrawLine(*lineSegment)
        dc.EndDrawing()


class DoodleFrame(wx.Frame):
    def __init__(self, parent=None):
        super(DoodleFrame, self).__init__(parent, title="Doodle Frame",
            size=(800,600),
            style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        doodle = DoodleWindow(self)


if __name__ == '__main__':
    app = wx.App()
    frame = DoodleFrame()
    frame.Show()
    app.MainLoop()