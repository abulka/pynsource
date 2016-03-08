#!/usr/bin/env python2.2

#-----------------------------------------------------------------------------
# Name:        wxPlotter.py
# Purpose:
#
# Author:      RJS
#
# Created:     2009/7/21
# Licence:     Use as you wish.
#-----------------------------------------------------------------------------

"""
    This is a simple light weight plotting module that can be used with Boa or
    easily integrated into your own wxPython application.  The emphasis is on
small
    size and fast plotting for large data sets.  It has a reasonable number of
    features to do line and scatter graphs easily. 

    Based on wxPlotCanvas and wxPyPlot
    Written by K.Hinsen, R. Srinivasan;
    Ported to wxPython Harm van der Heijden, feb 1999,     Gordon Williams
    Upgraded to wx2.8 by RJS
"""

import wx
import time, string
import numpy
from numpy import array as numpy_array
try:
    True
except NameError:
    True = 1==1
    False = 1==0

#
# Plotting classes...
#
class PolyPoints:
    """Base Class for lines and markers
        - All methods are private.
    """

    def __init__(self, points, attr):
        self.points = numpy_array(points)
        self.currentScale= (1,1)
        #self.currentShift= (0,0)
        self.scaled = self.points
        self.attributes = {}
        self.attributes.update(self._attributes)
        for name, value in attr.items():
            if name not in self._attributes.keys():
                raise KeyError, "Style attribute incorrect. Should be one of %s" %self._attributes.keys()
            self.attributes[name] = value

    def boundingBox(self):
        if len(self.points) == 0:
            #no curves to draw
            #defaults to (-1,-1) and (1,1) but axis can be set in Draw
            minXY= numpy_array([-1,-1])
            maxXY= numpy_array([ 1, 1])
        else:
            minXY= numpy.minimum.reduce(self.points)
            maxXY= numpy.maximum.reduce(self.points)
        return minXY, maxXY

    def scaleAndShift(self, scale=(1,1), shift=(0,0)):
        if len(self.points) == 0:
            #no curves to draw
            return
        if scale is not self.currentScale:
            #update point scaling
            self.scaled = scale*self.points+shift
            #self.currentScale= scale
            #self.currentShift= shift
        #else unchanged use the current scaling

class PolyLine(PolyPoints):
    """Class to define line type and style
        - All methods except __init__ are private.
    """

    _attributes = {'colour': 'black',
                   'width': 1,
                   'style': wx.SOLID}

    def __init__(self, points, **attr):
        """Creates PolyLine object
            points - sequence (array, tuple or list) of (x,y) points making up line
            **attr - key word attributes
                Defaults:
                    'colour'= 'black',          - wx.Pen Colour any wxNamedColour
                    'width'= 1,                 - Pen width
                    'style'= wx.SOLID,           - wx.Pen style
        """
        PolyPoints.__init__(self, points, attr)

    def draw(self, dc, coord= None):
        colour = self.attributes['colour']
        width = self.attributes['width'] 
        style= self.attributes['style']
        dc.SetPen(wx.Pen(wx.NamedColour(colour), int(width), style))
        dc.DrawLines(self.scaled)

    def getSymExtent(self):
        """Width and Height of Marker"""
        h= self.attributes['width'] 
        w= 5 * h
        return (w,h)

class PolyMarker(PolyPoints):
    """Class to define marker type and style
        - All methods except __init__ are private.
    """

    _attributes = {'colour': 'black',
                   'width': 1,
                   'size': 2,
                   'fillcolour': None,
                   'fillstyle': wx.SOLID,
                   'marker': 'circle'}

    def __init__(self, points, **attr):
        """Creates PolyMarker object
        points - sequence (array, tuple or list) of (x,y) points
        **attr - key word attributes
            Defaults:
                'colour'= 'black',          - wx.Pen Colour any wxNamedColour
                'width'= 1,                 - Pen width
                'size'= 2,                  - Marker size
                'fillcolour'= same as colour,      - wx.Brush Colour any wxNamedColour
                'fillstyle'= wx.SOLID,    - wx.Brush fill style (use wx.TRANSPARENT for no fill)
                'marker'= 'circle'          - Marker shape

            Marker Shapes:
                - 'circle'
                - 'dot'
                - 'square'
                - 'triangle'
                - 'triangle_down'
                - 'cross'
                - 'plus'
        """

        PolyPoints.__init__(self, points, attr)

    def draw(self, dc, coord= None):
        colour = self.attributes['colour']
        width = self.attributes['width']
        size = self.attributes['size'] 
        fillcolour = self.attributes['fillcolour']
        fillstyle = self.attributes['fillstyle']
        marker = self.attributes['marker']

        dc.SetPen(wx.Pen(wx.NamedColour(colour),int(width)))
        if fillcolour:
            dc.SetBrush(wx.Brush(wx.NamedColour(fillcolour),fillstyle))
        else:
            dc.SetBrush(wx.Brush(wx.NamedColour(colour), fillstyle))
        self._drawmarkers(dc, self.scaled, marker, size)

    def getSymExtent(self):
        """Width and Height of Marker"""
        s= 5*self.attributes['size']
        return (s,s)

    def _drawmarkers(self, dc, coords, marker,size=1):
        f = eval('self._' +marker)
        f(dc, coords, size)

    def _circle(self, dc, coords, size=1):
        fact= 2.5*size
        wh= 5.0*size
        rect= numpy.zeros((len(coords),4),numpy.float)+[0.0,0.0,wh,wh]
        rect[:,0:2]= coords-[fact,fact]
        dc.DrawEllipseList(rect.astype(numpy.int32))

    def _dot(self, dc, coords, size=1):
        dc.DrawPointList(coords)

    def _square(self, dc, coords, size=1):
        fact= 2.5*size
        wh= 5.0*size
        rect= numpy.zeros((len(coords),4),numpy.float)+[0.0,0.0,wh,wh]
        rect[:,0:2]= coords-[fact,fact]
        dc.DrawRectangleList(rect.astype(numpy.int32))

    def _triangle(self, dc, coords, size=1):
        shape= [(-2.5*size,1.44*size), (2.5*size,1.44*size), (0.0,-2.88*size)]
        poly= numpy.repeat(coords,3)
        poly.shape= (len(coords),3,2)
        poly += shape
        dc.DrawPolygonList(poly.astype(numpy.int32))

    def _triangle_down(self, dc, coords, size=1):
        shape= [(-2.5*size,-1.44*size), (2.5*size,-1.44*size), (0.0,2.88*size)]
        poly= numpy.repeat(coords,3)
        poly.shape= (len(coords),3,2)
        poly += shape
        dc.DrawPolygonList(poly.astype(numpy.int32))

    def _cross(self, dc, coords, size=1):
        fact= 2.5*size
        for f in [[-fact,-fact,fact,fact],[-fact,fact,fact,-fact]]:
            lines= numpy.concatenate((coords,coords),axis=1)+f
            dc.DrawLineList(lines.astype(numpy.int32))

    def _plus(self, dc, coords, size=1):
        fact= 2.5*size
        for f in [[-fact,0,fact,0],[0,-fact,0,fact]]:
            lines= numpy.concatenate((coords,coords),axis=1)+f
            dc.DrawLineList(lines.astype(numpy.int32))

class PlotGraphics:
    """Container to hold PolyXXX objects and graph labels
        - All methods except __init__ are private.
    """

    def __init__(self, objects, title='', xLabel='', yLabel= ''):
        """Creates PlotGraphics object
        objects - list of PolyXXX objects to make graph
        title - title shown at top of graph
        xLabel - label shown on x-axis
        yLabel - label shown on y-axis
        """
        if type(objects) not in [list,tuple]:
            raise TypeError, "objects argument should be list or tuple"
        self.objects = objects

    def boundingBox(self):
        p1, p2 = self.objects[0].boundingBox()
        for o in self.objects[1:]:
            p1o, p2o = o.boundingBox()
            p1 = numpy.minimum(p1, p1o)
            p2 = numpy.maximum(p2, p2o)
        return p1, p2

    def scaleAndShift(self, scale=(1,1), shift=(0,0)):
        for o in self.objects:
            o.scaleAndShift(scale, shift)

    def draw(self, dc):
        for o in self.objects:
            #t=time.clock()          #profile info
            o.draw(dc)
            #dt= time.clock()-t
            #print o, "time=", dt

    def __len__(self):
        return len(self.objects)

    def __getitem__(self, item):
        return self.objects[item]

#-------------------------------------------------------------------------------
#Main window that you will want to import into your application.

class PlotCanvas(wx.Window):
    """Subclass of a wxWindow to allow simple general plotting
    of data with zoom, labels, and automatic axis scaling."""

    def __init__(self, parent, id = -1, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style= wx.DEFAULT_FRAME_STYLE, name= "",
            bitmap=None, borderSize=.03):
        """Constucts a window, which can be a child of a frame, dialog or
        any other non-control window"""

        wx.Window.__init__(self, parent, id, pos, size, style, name)
        self.border = (1,1)

        self.SetBackgroundColour(wx.NamedColour("white"))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        #Create some mouse events for zooming
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)

        # set curser as cross-hairs
        self.SetCursor(wx.CROSS_CURSOR)

        #Drawing Variables
        self.last_draw = None
        self._pointScale= 1
        self._pointShift= 0
        self._xSpec= 'none'
        self._ySpec= 'none'

        if bitmap is not None:
            self.bmp = bitmap
            self.original_bmp = bitmap
        else:
            self.bmp = None
        self.border = borderSize

        # OnSize called to make sure the buffer is initialized.
        # This might result in OnSize getting called twice on some
        # platforms at initialization, but little harm done.
        self.OnSize(None) #sets the initial size based on client size
        wx.InitAllImageHandlers()

    def Reset(self):
        """Unzoom the plot."""
        if self.last_draw is not None:
            self.Draw(self.last_draw[0])

    def GetXY(self,event):
        """Takes a mouse event and returns the XY user axis values."""
        screenPos= numpy_array( event.GetPosition())
        x,y= (screenPos-self._pointShift)/self._pointScale
        return x,y

    def Draw(self, graphics, xAxis = None, yAxis = None, dc = None):
        """Draw objects in graphics with specified x and y axis.
        graphics- instance of PlotGraphics with list of PolyXXX objects
        xAxis - tuple with (min, max) axis range to view
        yAxis - same as xAxis
        dc - drawing context - doesn't have to be specified.
        If it's not, the offscreen buffer is used
        """

        if dc == None:
            # allows using floats for certain functions
            dc = FloatDCWrapper(wx.BufferedDC(wx.ClientDC(self), self._Buffer))
            dc.Clear()            
        dc.DrawBitmap(self.bmp, 0, 0, False) 
        dc.BeginDrawing()

        #sizes axis to axis type, create lower left and upper right corners of plot
        if xAxis == None or yAxis == None:
            #One or both axis not specified in Draw
            p1, p2 = graphics.boundingBox()     #min, max points of graphics
            if xAxis == None:
                xAxis = self._axisInterval(self._xSpec, p1[0], p2[0]) #in user units
            if yAxis == None:
                yAxis = self._axisInterval(self._ySpec, p1[1], p2[1])
            #Adjust bounding box for axis spec
            p1[0],p1[1] = xAxis[0], yAxis[0]     #lower left corner user scale (xmin,ymin)
            p2[0],p2[1] = xAxis[1], yAxis[1]     #upper right corner user scale (xmax,ymax)
        else:
            #Both axis specified in Draw
            p1= numpy_array([xAxis[0], yAxis[0]])    #lower left corner user scale (xmin,ymin)
            p2= numpy_array([xAxis[1], yAxis[1]])     #upper right corner user scale (xmax,ymax)

        #allow for scaling and shifting plotted points
        scale = (self.plotbox_size) / (p2-p1)* numpy_array((1,-1))
        shift = -p1*scale + self.plotbox_origin 

        graphics.scaleAndShift(scale, shift)
        graphics.draw(dc)
        dc.EndDrawing()

    def Redraw(self, dc= None):
        """Redraw the existing plot."""
        if self.last_draw is not None:
            graphics, xAxis, yAxis= self.last_draw
            self.Draw(graphics,xAxis,yAxis,dc)

    def Clear(self):
        """Erase the window."""
        dc = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
        dc.Clear()
        self.last_draw = None

    # event handlers **********************************
    def OnMouseLeftDown(self,event):
        #self._zoomCorner1[0], self._zoomCorner1[1]= self.GetXY(event)
        pass # ANDY

    def OnPaint(self, event):
        # All that is needed here is to draw the buffer to screen
        dc = wx.BufferedPaintDC(self, self._Buffer)

    def OnSize(self,event):
        # The Buffer init is done here, to make sure the buffer is always
        # the same size as the Window
        Size  = self.GetClientSizeTuple()
        if self.bmp:
            img = self.original_bmp.ConvertToImage() # can't resize bmps
            img.Rescale(Size[0], Size[1], wx.IMAGE_QUALITY_HIGH) 
            self.bmp = wx.BitmapFromImage(img, depth=-1)

        # Make new offscreen bitmap: this bitmap will always have the
        # current drawing in it, so it can be used to save the image to
        # a file, or whatever.
        self._Buffer = wx.EmptyBitmap(Size[0],Size[1])
        #self._Buffer = self.bmp
        self._setSize()
        if self.last_draw is None:
            self.Clear()
        else:
            graphics, xSpec, ySpec = self.last_draw
            self.Draw(graphics,xSpec,ySpec)

    #Private Methods **************************************************
    def _setSize(self, width=None, height=None):
        """DC width and height."""
        if width == None:
            (self.width,self.height) = self.GetClientSizeTuple()
        else:
            self.width, self.height= width,height
        self.plotbox_size = (1-self.border)*numpy_array([self.width, self.height])
        xo = 0.5*(self.width-self.plotbox_size[0])
        yo = self.height-0.5*(self.height-self.plotbox_size[1])
        self.plotbox_origin = numpy_array([xo, yo])

    def _axisInterval(self, spec, lower, upper):
        """Returns sensible axis range for given spec"""
        if spec == 'none' or spec == 'min':
            if lower == upper:
                return lower-0.5, upper+0.5
            else:
                return lower, upper
        elif spec == 'auto':
            range = upper-lower
            if range == 0.:
                return lower-0.5, upper+0.5
            log = Numeric.log10(range)
            power = Numeric.floor(log)
            fraction = log-power
            if fraction <= 0.05:
                power = power-1
            grid = 10.**power
            lower = lower - lower % grid
            mod = upper % grid
            if mod != 0:
                upper = upper - mod + grid
            return lower, upper
        elif type(spec) == type(()):
            lower, upper = spec
            if lower <= upper:
                return lower, upper
            else:
                return upper, lower
        else:
            raise ValueError, str(spec) + ': illegal axis specification'

#-------------------------------------------------------------------------------

# Hack to allow plotting real numbers for the methods listed.
# All others passed directly to DC.
# For Drawing it is used as
# dc = FloatDCWrapper(wx.BufferedDC(wx.ClientDC(self), self._Buffer))
# For printing is is used as
# dc = FloatDCWrapper(self.GetDC())
class FloatDCWrapper:
    def __init__(self, aDC):
        self.theDC = aDC
    def DrawLine(self, x1,y1,x2,y2):
        self.theDC.DrawLine(int(x1),int(y1),int(x2),int(y2))
    def DrawText(self, txt, x, y):
        self.theDC.DrawText(txt, int(x), int(y))
    def DrawRotatedText(self, txt, x, y, angle):
        self.theDC.DrawRotatedText(txt, int(x), int(y), angle)
    def SetClippingRegion(self, x, y, width, height):
        self.theDC.SetClippingRegion(int(x), int(y), int(width), int(height))
    def SetDeviceOrigin(self, x, y):
        self.theDC.SetDeviceOrigin(int(x), int(y))
    def __getattr__(self, name):
        return getattr(self.theDC, name)

#---------------------------------------------------------------------------
# if running standalone...
#
#     ...a sample implementation using the above
#

def __test():
    from wx.lib.dialogs import ScrolledMessageDialog

    def _draw1Objects(data1=None):
        # 100 points sin function, plotted as green circles
        data1 = 2.*numpy.pi*numpy.arange(200)/200.
        data1.shape = (100, 2)
        data1[:,1] = numpy.sin(data1[:,0])
        markers1 = PolyMarker(data1, colour='green', marker='circle',size=1)

        # 50 points cos function, plotted as red line
        data1 = 2.*numpy.pi*numpy.arange(100)/100.
        data1.shape = (50,2)
        data1[:,1] = numpy.cos(data1[:,0])
        lines = PolyLine(data1, colour='red')

        # A few more points...
        pi = numpy.pi
        markers2 = PolyMarker([(0., 0.), (pi/4., 1.), (pi/2, 0.),
                              (3.*pi/4., -1)], colour='blue',
                              marker='cross')

        return PlotGraphics([markers1, lines, markers2],"Graph Title", "X Axis",
"Y Axis")

    def _draw2Objects():
        # 100 points sin function, plotted as green dots
        data1 = 2.*numpy.pi*numpy.arange(200)/200.
        data1.shape = (100, 2)
        data1[:,1] = numpy.sin(data1[:,0])
        line1 = PolyLine(data1,  colour='green', width=6, style=wx.DOT)

        # 50 points cos function, plotted as red dot-dash
        data1 = 2.*numpy.pi*numpy.arange(100)/100.
        data1.shape = (50,2)
        data1[:,1] = numpy.cos(data1[:,0])
        line2 = PolyLine(data1,  colour='red', width=3, style= wx.DOT_DASH)

        # A few more points...
        pi = numpy.pi
        markers1 = PolyMarker([(0., 0.), (pi/4., 1.), (pi/2, 0.),
                              (3.*pi/4., -1)],  colour='blue', width= 3, size=6,
                              fillcolour= 'red', fillstyle= wx.CROSSDIAG_HATCH,
                              marker='square')

        return PlotGraphics([markers1, line1, line2], "Big Markers with Different Line Styles")

    def _draw3Objects():
        markerList= ['circle', 'dot', 'square', 'triangle', 'triangle_down',
                    'cross', 'plus', 'circle']
        m=[]
        for i in range(len(markerList)):
            m.append(PolyMarker([(2*i+.5,i+.5)], colour='blue',
                              marker=markerList[i]))
        return PlotGraphics(m, "Selection of Markers", "Minimal Axis", "No Axis")

    def _draw4Objects(data1):
        # 2500 point line
        line1 = PolyLine(data1,  colour='green', width=5)

        # A few more points...
        #markers2 = PolyMarker(data1, colour='blue',  marker='square')
        return PlotGraphics([line1], "2500 Points", "Value X", "")

    def _draw5Objects():
        # Empty graph with axis defined but no points/lines
        points=[]
        line1 = PolyLine(points, colour='green', width=5)
        return PlotGraphics([line1], "Empty Plot With Just Axes", "Value X", "Value Y")

    class AppFrame(wx.Frame):
        def __init__(self, parent, id, title):
            wx.Frame.__init__(self, parent, id, title,
                                (220, 220), wx.Size(600, 400))

            # Now Create the menu bar and items
            self.mainmenu = wx.MenuBar()

            menu = wx.Menu()

            menu.Append(205, 'E&xit', 'Enough of this already!')
            wx.EVT_MENU(self, 205, self.OnFileExit)
            self.mainmenu.Append(menu, '&File')

            menu = wx.Menu()
            menu.Append(206, 'Draw1', 'Draw plots1')
            wx.EVT_MENU(self,206,self.OnPlotDraw1)
            menu.Append(207, 'Draw2', 'Draw plots2')
            wx.EVT_MENU(self,207,self.OnPlotDraw2)
            menu.Append(208, 'Draw3', 'Draw plots3')
            wx.EVT_MENU(self,208,self.OnPlotDraw3)
            menu.Append(209, 'Draw4', 'Draw plots4')
            wx.EVT_MENU(self,209,self.OnPlotDraw4)
            menu.Append(215, 'Enable &Grid', 'Turn on Grid', kind=wx.ITEM_CHECK)
            wx.EVT_MENU(self,215,self.OnEnableGrid)
            menu.Append(235, '&Plot Reset', 'Reset to original plot')
            wx.EVT_MENU(self,235,self.OnReset)

            self.mainmenu.Append(menu, '&Plot')

            menu = wx.Menu()
            menu.Append(300, '&About', 'About this thing...')
            wx.EVT_MENU(self, 300, self.OnHelpAbout)
            self.mainmenu.Append(menu, '&Help')

            self.SetMenuBar(self.mainmenu)

            # A status bar to tell people what's happening
            self.CreateStatusBar(1)
            bmp=wx.Bitmap('moo.jpg', wx.BITMAP_TYPE_ANY)
            self.client = PlotCanvas(self, bitmap=bmp, borderSize=.25)
            #self.client = FastPlotCanvas(self, size=self.GetClientSizeTuple(), 
            #    xAxis= (0,50000), yAxis= (0,50000))
            #Create mouse event for showing cursor coords in status bar
            self.client.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)

        def OnMouseLeftDown(self,event):
            s= "Left Mouse Down at Point: (%.4f, %.4f)" % self.client.GetXY(event)
            self.SetStatusText(s)
            event.Skip()

        def OnFileExit(self, event):
            self.Close()

        def OnPlotDraw1(self, event):
            self.resetDefaults()
            self.client.Draw(_draw1Objects(),xAxis= (0,6), yAxis= (-2,2))

        def OnPlotDraw2(self, event):
            self.resetDefaults()
            self.client.Draw(_draw2Objects(),xAxis= (0,6), yAxis= (-2,2))

        def OnPlotDraw3(self, event):
            self.resetDefaults()
            self.client.Draw(_draw3Objects(),xAxis= (0,200), yAxis= (-20,100))

        def OnPlotDraw4(self, event):
            self.resetDefaults()
            #drawObj= _draw4Objects()
            #self.client.Draw(drawObj)
            #profile
            data1 = numpy.arange(0,50000,10)
            data1.shape = (2500, 2)
            start = time.clock()
            for x in range(30):
                self.client.Draw(_draw4Objects(data1))
                print x,
            print "\n30 plots of Draw4 took: %f sec."%(time.clock() - start)
            #profile end

        def OnPlotDraw5(self, event):
            #Empty plot with just axes
            self.resetDefaults()
            drawObj= _draw5Objects()
            #make the axis X= (0,5), Y=(0,10)
            #(default with None is X= (-1,1), Y= (-1,1))
            self.client.Draw(drawObj, xAxis= (0,5), yAxis= (0,10))

        def OnPlotRedraw(self,event):
            self.client.Redraw()

        def OnPlotClear(self,event):
            self.client.Clear()

        def OnPlotScale(self, event):
            if self.client.last_draw != None:
                graphics, xAxis, yAxis= self.client.last_draw
                self.client.Draw(graphics,(1,3.05),(0,1))

        def OnEnableZoom(self, event):
            self.client.SetEnableZoom(event.IsChecked())

        def OnEnableGrid(self, event):
            self.client.SetEnableGrid(event.IsChecked())

        def OnReset(self,event):
            self.client.Reset()

        def OnHelpAbout(self, event):
            about = wx.ScrolledMessageDialog(self, __doc__, "About...")
            about.ShowModal()

        def resetDefaults(self):
            """Just to reset the fonts back to the PlotCanvas defaults"""
            pass

    class MyApp(wx.App):
        def OnInit(self):
            frame = AppFrame(None, -1, "wxPlotCanvas")
            frame.Show(True)
            self.SetTopWindow(frame)
            return True

    app = MyApp(0)
    app.MainLoop()

if __name__ == '__main__':
    # Import Psyco if available
    try:
        import psyco
        #psyco.log()
        #psyco.profile()
        psyco.full()
    except ImportError:
        pass
    __test()