aboutmsg = """
PyNSource GUI
http://www.andypatterns.com/pynsource

A GUI front end to the python code scanner PyNSource that generates UML diagrams.
Version 1.4e

(c) Andy Bulka 2004-2009

Some code borrowed from wxPython Library and Boa.
License: Free

Feb 2009
--------
For running under the latest versions of wx.
-Andy

P.S. There is currently a problem running on a Mac.  It runs, but when you reverse engineer something, it crashes because of too many dc's or something.  Am looking into it.

"""


from wxPython.wx import *

#from wxPython.ogl import *
from wx.lib.ogl import *

import wx
from wx import Frame

# http://www.wxpython.org/docs/api/wx.lib.ogl.PolygonShape-class.html
from wx.lib.ogl import PolygonShape as wxPolygonShape
from wx.lib.ogl import DividedShape as wxDividedShape
from wx.lib.ogl import RectangleShape as wxRectangleShape
from wx.lib.ogl import ShapeEvtHandler as wxShapeEvtHandler
from wx.lib.ogl import ShapeCanvas as wxShapeCanvas
from wx.lib.ogl import OGLCleanUp as wxOGLCleanUp
from wx.lib.ogl import Diagram as wxDiagram
from wx.lib.ogl import OGLInitialize as wxOGLInitialize
from wx.lib.ogl import ShapeRegion as wxShapeRegion
from wx.lib.ogl import LineShape as wxLineShape

#import images

import os
import os,stat

UML_STYLE_1 = 0
WINDOW_SIZE = (640,480)


class DiamondShape(wxPolygonShape):
    def __init__(self, w=0.0, h=0.0):
        wxPolygonShape.__init__(self)
        if w == 0.0:
            w = 60.0
        if h == 0.0:
            h = 60.0

        ## Either wxRealPoints or 2-tuples of floats  works.

        #points = [ wxRealPoint(0.0,    -h/2.0),
        #          wxRealPoint(w/2.0,  0.0),
        #          wxRealPoint(0.0,    h/2.0),
        #          wxRealPoint(-w/2.0, 0.0),
        #          ]
        points = [ (0.0,    -h/2.0),
                   (w/2.0,  0.0),
                   (0.0,    h/2.0),
                   (-w/2.0, 0.0),
                   ]

        self.Create(points)


#----------------------------------------------------------------------

class RoundedRectangleShape(wxRectangleShape):
    def __init__(self, w=0.0, h=0.0):
        wxRectangleShape.__init__(self, w, h)
        self.SetCornerRadius(-0.3)


#----------------------------------------------------------------------

class DividedShape(wxDividedShape):
    def __init__(self, width, height, canvas):
        wxDividedShape.__init__(self, width, height)
        if UML_STYLE_1:
            self.BuildRegions(canvas)

    def BuildRegions(self, canvas):
        region1 = wxShapeRegion()
        region1.SetText('wxDividedShape')
        region1.SetProportions(0.0, 0.2)
        region1.SetFormatMode(FORMAT_CENTRE_HORIZ)
        self.AddRegion(region1)

        region2 = wxShapeRegion()
        region2.SetText('This is Region number two.')
        region2.SetProportions(0.0, 0.3)
        region2.SetFormatMode(FORMAT_NONE)
        #region2.SetFormatMode(FORMAT_CENTRE_HORIZ|FORMAT_CENTRE_VERT)
        self.AddRegion(region2)

        region3 = wxShapeRegion()

        region3.SetText("blah\nblah\nblah blah")
        region3.SetProportions(0.0, 0.5)
        region3.SetFormatMode(FORMAT_NONE)
        self.AddRegion(region3)


        self.region1 = region1   # for external access...
        self.region2 = region2   # for external access...
        self.region3 = region3   # for external access...

        self.SetRegionSizes()
        self.ReformatRegions(canvas)


    def FlushText(self):
        # Taken from Boa
        """This method retrieves the text from the shape
        regions and draws it. There seems to be a problem that
        the text is not normally drawn. """
        canvas = self.GetCanvas()
        dc = wxClientDC(canvas)
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
        dc = wxClientDC(canvas)  # used for measuring
        for region in self.GetRegions():
            text = region.GetText()
            self.FormatText(dc, text, rnum)
            rnum += 1


    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        self.base_OnSizingEndDragLeft(pt, x, y, keys, attch)
        self.SetRegionSizes()
        self.ReformatRegions()
        self.GetCanvas().Refresh()


class DividedShapeSmall(DividedShape):
    def __init__(self, width, height, canvas):
        DividedShape.__init__(self, width, height, canvas)

    def BuildRegions(self, canvas):
        region1 = wxShapeRegion()
        region1.SetText('wxDividedShapeSmall')
        region1.SetProportions(0.0, 0.9)
        region1.SetFormatMode(FORMAT_CENTRE_HORIZ)
        self.AddRegion(region1)

        self.region1 = region1   # for external access...

        self.SetRegionSizes()
        self.ReformatRegions(canvas)

    def ReformatRegions(self, canvas=None):
        rnum = 0
        if canvas is None:
            canvas = self.GetCanvas()
        dc = wxClientDC(canvas)  # used for measuring
        for region in self.GetRegions():
            text = region.GetText()
            self.FormatText(dc, text, rnum)
            rnum += 1

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        self.base_OnSizingEndDragLeft(pt, x, y, keys, attch)
        self.SetRegionSizes()
        self.ReformatRegions()
        self.GetCanvas().Refresh()

#----------------------------------------------------------------------

class MyEvtHandler(wxShapeEvtHandler):
    def __init__(self, log, frame):
        wxShapeEvtHandler.__init__(self)
        self.log = log
        self.statbarFrame = frame
        self.ZapShape = self._ZapShapeStub
        self.Refreshredraw = self._RefreshredrawStub

    def SetShapeZappingMethod(self, dozapshape):
        self.ZapShape = dozapshape

    def SetPostDeleteRefreshMethod(self, dorefreshredraw):
        self.Refreshredraw = dorefreshredraw


    def _ZapShapeStub(self, shape):
        """
        This event handler method calls the window zap shape method, which removes the shape from the
        app's private list of shapes and composiiton and generalisation shapes.
        The event handler than removes the shape from the diagram.
        """
        print 'No zap shape method defined.'

    def _RefreshredrawStub(self):
        print 'No Refreshredraw method defined.'

    def UpdateStatusBar(self, shape):
        #print 'UpdateStatusBar', shape.region1.GetText(), shape.GetX(), shape.GetY()
        x,y = shape.GetX(), shape.GetY()
        width, height = shape.GetBoundingBoxMax()
        self.statbarFrame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)" %
                                        (x, y, width, height))


    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        #print shape.__class__, shape.GetClassName()
        canvas = shape.GetCanvas()
        dc = wxClientDC(canvas)
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
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            shape.Select(True, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)
                canvas.Redraw(dc)

        self.UpdateStatusBar(shape)


    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        #self.base_OnEndDragLeft(x, y, keys, attachment)
        wxShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)        
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        self.UpdateStatusBar(shape)


    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        #self.base_OnSizingEndDragLeft(pt, x, y, keys, attch)
        wxShapeEvtHandler.OnSizingEndDragLeft(self.pt, x, y, keys, attch)        
        self.UpdateStatusBar(self.GetShape())


    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        #self.base_OnMovePost(dc, x, y, oldX, oldY, display)
        wxShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        self.UpdateStatusBar(self.GetShape())


    def OnRightClick(self, *dontcare):
        #self.log.WriteText("%s\n" % self.GetShape())

        shape = self.GetShape()

        canvas = shape.GetCanvas()
        dc = wxClientDC(canvas)
        canvas.PrepareDC(dc)
        diagram = canvas.GetDiagram()

        if shape.Selected():
            shape.Select(False, dc)
            canvas.Redraw(dc)

        for line in shape.GetLines():
            line.Unlink()
            #shape.RemoveLine(line)
            diagram.RemoveShape(line)

        self.ZapShape(shape)
        diagram.RemoveShape(shape)
        diagram.Clear(dc)
        canvas.Redraw(dc)

        self.Refreshredraw(event=self)   # will call the app level refresh() method in window.  Event is passed for fun - we don't look at it.

        """
        Some useful documentation on wxOGL

        wxLineShape::Unlink
        void Unlink()
        Unlinks the line from the nodes at either end.

        wxShape::GetLines
        wxList& GetLines() const
        Returns a reference to the list of lines connected to this shape.

        wxShape::RemoveLine
        void RemoveLine(wxLineShape* line)
        Removes the given line from the shape's list of attached lines.

        wxDiagram::Redraw
        void Redraw(wxDC& dc)
        Draws the shapes in the diagram on the specified device context.

        wxDiagram::Clear
        void Clear(wxDC& dc)
        Clears the specified device context.
        """
#----------------------------------------------------------------------
import sys, glob

#if not '.' in sys.path: sys.path.insert(0, '.')  # so find local pynsource package first.
#import pprint
#pprint.pprint(sys.path)
#import pynsource
#print pynsource
#from pynsource.pynsource import PythonToJava, PySourceAsJava

from pynsource import PythonToJava, PySourceAsJava


class TestWindow(wxShapeCanvas):
    scrollStepX = 10
    scrollStepY = 10
    classnametoshape = {}


    def __init__(self, parent, log, frame):
        wxShapeCanvas.__init__(self, parent)

        maxWidth  = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth/20, maxHeight/20)

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE") #wxWHITE)

        self.diagram = wxDiagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.shapes = []
        self.save_gdi = []
        EVT_WINDOW_DESTROY(self, self.OnDestroy)

        self.font1 = wxFont(14, wxMODERN, wxNORMAL, wxNORMAL, false)
        self.font2 = wxFont(10, wxMODERN, wxNORMAL, wxNORMAL, false)

        #self.Go(path=r'C:\Documents and Settings\Administrator\My Documents\aa Python\pyNsource\Tests\PythonToJavaTest01\pythoninput01\*.py')

        self.associations_generalisation = None
        self.associations_composition = None

    def ZapShape(self, shape):
        classnames = self.classnametoshape.keys()
        for classname in classnames:
            if self.classnametoshape[classname] == shape:
                print 'found class to delete: ', classname
                break

        del self.classnametoshape[classname]

# Too hard to remove the classname from these structures since these are tuples
# between two classes.  Harmless to keep them in here.
##        if class1, class2 in self.associations_generalisation:
##            self.associations_generalisation.remove(shape)
##        if shape in self.associations_composition:
##            self.associations_composition.remove(shape)

        assert shape in self.shapes
        self.shapes.remove(shape)

    def Clear(self):
        self.diagram.DeleteAllShapes()

        dc = wxClientDC(self)
        self.diagram.Clear(dc)
        # self.redraw()   # do not redraw cos nothing exists!

        # Re-init - doesn't help the File New problem....
        """
        self.diagram = wxDiagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        """

        self.shapes = []
        self.save_gdi = []

        # THIS is the one that we need....
        self.classnametoshape = {}

        # and maybe this too
        self.associations_generalisation = None
        self.associations_composition = None


    def _Process(self, filepath):
        print '_Process', filepath

        p = PySourceAsJava('c:\\try')
        p.optionModuleAsClass = 0
        p.verbose = 0
        p.Parse(filepath)

        """
        if self.verbose:
            padding = ' '
        else:
            padding = ''
        thefile = os.path.basename(filepath)
        if thefile[0] == '_':
            print '  ', 'Skipped', thefile, 'cos begins with underscore.'
            return
        print '%sProcessing %s...'%(padding, thefile)
        p = self._CreateParser()
        p.Parse(filepath)
        str(p)  # triggers the output.
        """

        for classname, classentry in p.classlist.items():
            #print 'CLASS', classname, classentry

            # These are a list of (attr, otherclass) however they imply that THIS class
            # owns all those other classes.
            #print classentry.classdependencytuples
            for attr, otherclass in classentry.classdependencytuples:
                self.associations_composition.append((otherclass, classname))  # reverse direction so round black arrows look ok

            # Generalisations
            if classentry.classesinheritsfrom:
                for parentclass in classentry.classesinheritsfrom:

                    if parentclass.find('.') <> -1:         # fix names like "unittest.TestCase" into "unittest"
                        parentclass = parentclass.split('.')[0] # take the lhs

                    self.associations_generalisation.append((classname, parentclass))
                    #print 'ADDED Generalisation!!!!!!!!!!!!!!!'


            if UML_STYLE_1:
                # Build the UML shape
                #
                if classname not in self.classnametoshape:
                    #print 'BUILDING', classname, 'SEARCH', classname in self.classnametoshape, 'LEN', len(self.classnametoshape)
                    rRectBrush = wxBrush("MEDIUM TURQUOISE", wxSOLID)
                    dsBrush = wxBrush("WHEAT", wxSOLID)
                    ds = self.MyAddShape(DividedShape(100, 150, self), 50, 145, wxBLACK_PEN, dsBrush, '')
                    ds.SetCentreResize(0)  # Specify whether the shape is to be resized from the centre (the centre stands still) or from the corner or side being dragged (the other corner or side stands still).

                    ds.region1.SetText(classname)
                    ds.region2.SetText('\n'.join([ attrobj.attrname for attrobj in classentry.attrs ]))
                    ds.region3.SetText('\n'.join(classentry.defs))
                    ds.ReformatRegions()
                    #ds1.SetSize(ds1.GetBoundingBoxMax()[0]+1, ds1.GetBoundingBoxMax()[1])

                    # Record the name to shape map so that we can wire up the links later.
                    self.classnametoshape[classname] = ds
                else:
                    print 'Skipping', classname, 'already built shape...'
            else:
                # Build the UML shape
                #
                if classname not in self.classnametoshape:
                    shape = DividedShape(width=100, height=150, canvas=self)

                    pos = (50,50)
                    maxWidth = 10 #padding
                    #if not self.showAttributes: classAttrs = [' ']
                    #if not self.showMethods: classMeths = [' ']
                    className = classname
                    classAttrs = [ attrobj.attrname for attrobj in classentry.attrs ]
                    classMeths = classentry.defs


                    regionName, maxWidth, nameHeight = self.newRegion(
                          self.font1, 'class_name', [className], maxWidth)
                    regionAttribs, maxWidth, attribsHeight = self.newRegion(
                          self.font2, 'attributes', classAttrs, maxWidth)
                    regionMeths, maxWidth, methsHeight = self.newRegion(
                          self.font2, 'methods', classMeths, maxWidth)

                    totHeight = nameHeight + attribsHeight + methsHeight

                    regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
                    regionAttribs.SetProportions(0.0, 1.0*(attribsHeight/float(totHeight)))
                    regionMeths.SetProportions(0.0, 1.0*(methsHeight/float(totHeight)))

                    regionName.SetFormatMode(FORMAT_CENTRE_HORIZ)
                    shape.region1 = regionName  # Andy added, for later external reference to classname from just having the shap instance.

                    shape.AddRegion(regionName)
                    shape.AddRegion(regionAttribs)
                    shape.AddRegion(regionMeths)

                    shape.SetSize(maxWidth + 10, totHeight + 10)

                    shape.SetRegionSizes()

                    dsBrush = wxBrush("WHEAT", wxSOLID)
                    #idx = self.addShape(shape, pos[0], pos[1], wxBLACK_PEN, dsBrush, '') # get back index
                    ds = self.MyAddShape(shape, pos[0], pos[1], wxBLACK_PEN, dsBrush, '') # get back instance - but already had it...

                    shape.FlushText()

                    # Record the name to shape map so that we can wire up the links later.
                    self.classnametoshape[classname] = ds
                else:
                    print 'Skipping', classname, 'already built shape...'




    def _BuildAuxClasses(self, classestocreate=None):
            if not classestocreate:
                classestocreate = ('variant', 'unittest', 'list', 'object', 'dict')  # should add more classes and add them to a jar file to avoid namespace pollution.
            for classname in classestocreate:
                rRectBrush = wxBrush("MEDIUM TURQUOISE", wxSOLID)
                dsBrush = wxBrush("WHEAT", wxSOLID)
                ds = self.MyAddShape(DividedShapeSmall(100, 30, self), 50, 145, wxBLACK_PEN, dsBrush, '')
                if not UML_STYLE_1:
                    ds.BuildRegions(canvas=self)  # build the one region
                ds.SetCentreResize(0)  # Specify whether the shape is to be resized from the centre (the centre stands still) or from the corner or side being dragged (the other corner or side stands still).
                ds.region1.SetText(classname)
                ds.ReformatRegions()
                # Record the name to shape map so that we can wire up the links later.
                self.classnametoshape[classname] = ds




    def Go(self, files=None, path=None):

        # these are tuples between class names.
        self.associations_generalisation = []
        self.associations_composition = []

        # self._BuildAuxClasses()   # Now we do it on demand....


        if files:
            u = PythonToJava(None, treatmoduleasclass=0, verbose=0)
            for f in files:
                self._Process(f)    # Build a shape with all attrs and methods, and prepare association dict

        if path:
            param = path
            globbed = []
            files = glob.glob(param)
            globbed += files
            #print 'parsing', globbed

            u = PythonToJava(globbed, treatmoduleasclass=0, verbose=0)
            for directory in globbed:
                if '*' in directory or '.' in directory:
                    filepath = directory
                else:
                    filepath = os.path.join(directory, "*.py")
                #print 'Processing directory', filepath
                globbed2 = glob.glob(filepath)
                for f in globbed2:
                    self._Process(f)    # Build a shape with all attrs and methods, and prepare association dict



        # Wire up the associations
        dc = wxClientDC(self)
        self.PrepareDC(dc)

        self.DrawAssocLines(self.associations_generalisation, ARROW_ARROW, dc)
        self.DrawAssocLines(self.associations_composition, ARROW_FILLED_CIRCLE, dc)

        # Layout
        self.ArrangeShapes()



    def DrawAssocLines(self, associations, arrowtype, dc):
        for fromClassname, toClassname in associations:
            #print 'DrawAssocLines', fromClassname, toClassname

            if fromClassname not in self.classnametoshape:
                self._BuildAuxClasses(classestocreate=[fromClassname]) # Emergency creation of some unknown class.
            fromShape = self.classnametoshape[fromClassname]

            if toClassname not in self.classnametoshape:
                self._BuildAuxClasses(classestocreate=[toClassname]) # Emergency creation of some unknown class.
            toShape = self.classnametoshape[toClassname]

            line = wxLineShape()
            line.SetCanvas(self)
            line.SetPen(wxBLACK_PEN)
            line.SetBrush(wxBLACK_BRUSH)
            line.AddArrow(arrowtype)
            line.MakeLineControlPoints(2)
            fromShape.AddLine(line, toShape)
            self.diagram.AddShape(line)
            line.Show(True)

            # for some reason, the shapes have to be moved for the line to show up...
            fromShape.Move(dc, fromShape.GetX(), fromShape.GetY())




    def redraw(self):
        diagram = self.GetDiagram()
        canvas = diagram.GetCanvas()
        dc = wxClientDC(canvas)
        canvas.PrepareDC(dc)
        for shape in self.shapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
            shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)

    def redraw2(self):
        diagram = self.GetDiagram()
        canvas = diagram.GetCanvas()

        dc = wxClientDC(self)        # NEW! handles scrolled situations
        #dc = wxClientDC(canvas)     # doesn't handle scrolled situations

        canvas.PrepareDC(dc)
        for shape in self.shapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
            shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)

    def newRegion(self, font, name, textLst, maxWidth, totHeight = 10):
        # Taken from Boa, but put into the canvas class instead of the scrolled window class.
        region = wxShapeRegion()
        dc = wxClientDC(self)  # self is the canvas
        dc.SetFont(font)

        for text in textLst:
            w, h = dc.GetTextExtent(text)
            if w > maxWidth: maxWidth = w
            totHeight = totHeight + h + 0 # interline padding

        region.SetFont(font)
        region.SetText('\n'.join(textLst))
        #region._text = string.join(textLst, '\n')
        region.SetName(name)

        return region, maxWidth, totHeight


    def SortShapes(self):
        priority1 = [parentclassname for (classname, parentclassname) in self.associations_generalisation ]
        priority2 = [classname       for (classname, parentclassname) in self.associations_generalisation ]
        priority3 = [lhs            for (rhs, lhs) in self.associations_composition ]
        priority4 = [rhs             for (rhs, lhs) in self.associations_composition ]

        # convert classnames to shapes, avoid duplicating shapes.
        mostshapesinpriorityorder = []
        for classname in (priority1 + priority2 + priority3 + priority4):

            if classname not in self.classnametoshape:  # skip user deleted classes.
                continue

            shape = self.classnametoshape[classname]
            if shape not in mostshapesinpriorityorder:
                mostshapesinpriorityorder.append(shape)

        # find and loose shapes not associated to anything
        remainingshapes = [ shape for shape in self.shapes if shape not in mostshapesinpriorityorder ]

        return mostshapesinpriorityorder + remainingshapes


    def ArrangeShapes(self):

        shapeslist = self.SortShapes()

        dc = wxClientDC(self)
        self.PrepareDC(dc)

        # When look at the status bar whilst dragging UML shapes, the coords of the top left are
        # this.  This is different to what you see when mouse dragging on the canvas - there you DO get 0,0
        # Perhaps one measurement takes into account the menubar and the other doesn't.  Dunno.
        # UPDATE!!!! - it depends onteh size of the class you are dragging - get different values!
        LEFTMARGIN = 200
        TOPMARGIN = 230

        positions = []

        x = LEFTMARGIN
        y = TOPMARGIN

        maxx = 0
        biggestYthisrow = 0
        verticalWhiteSpace = 50
        count = 0
        for classShape in shapeslist:
            count += 1
            if count == 5:
                count = 0
                x = LEFTMARGIN
                y = y + biggestYthisrow + verticalWhiteSpace
                biggestYthisrow = 0

            whiteSpace = 50 # (width - currentWidth)/(len(self.shapes)-1.0 or 2.0)
            shapeX, shapeY = self.getShapeSize(classShape)

            if shapeY >= biggestYthisrow:
                biggestYthisrow = shapeY

            # snap to diagram grid coords
            #csX, csY = self.diagram.Snap((shapeX/2.0)+x, (shapeY/2.0)+y)
            #csX, csY = self.diagram.Snap(x, y)
            # don't display until finished
            positions.append((x,y))

            #print 'ArrangeShapes', classShape.region1.GetText(), (x,y)

            x = x + shapeX + whiteSpace
            if x > maxx:
                maxx = x + 300

        assert len(positions) == len(shapeslist)

        # Set size of entire diagram.
        height = y + 500
        width = maxx
        self.setSize(wxSize(int(width+50), int(height+50))) # fudge factors to keep some extra space

        # Now move the shapes into place.
        for (pos, classShape) in zip(positions, shapeslist):
            #print pos, classShape.region1.GetText()
            x, y = pos
            classShape.Move(dc, x, y, false)




    def getShapeSize( self, shape ):
        """Return the size of a shape's representation, an abstraction point"""
        return shape.GetBoundingBoxMax()

    def setSize(self, size):
        nvsx, nvsy = size.x / self.scrollStepX, size.y / self.scrollStepY
        self.Scroll(0, 0)
        self.SetScrollbars(self.scrollStepX, self.scrollStepY, nvsx, nvsy)
        canvas = self
        canvas.SetSize(canvas.GetVirtualSize())

    def MyAddShape(self, shape, x, y, pen, brush, text):
        shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        if pen:    shape.SetPen(pen)
        if brush:  shape.SetBrush(brush)
        if text:   shape.AddText(text)
        shape.SetShadowMode(SHADOW_RIGHT)
        self.diagram.AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler(self.log, self.frame)
        evthandler.SetShapeZappingMethod(self.ZapShape)
        evthandler.SetPostDeleteRefreshMethod(self.secretredrawmethod)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)
        return shape


    def addShape(self, shape, x, y, pen, brush, text):
        # Taken from Boa - we used to use MyAddShape
#        shape.SetDraggable(false)
        shape.SetCanvas(self.canvas)
        shape.SetX(x)
        shape.SetY(y)
        shape.SetPen(pen)
        shape.SetBrush(brush)
#        shape.SetFont(wxFont(6, wxMODERN, wxNORMAL, wxNORMAL, false))
        shape.AddText(text)
        shape.SetShadowMode(SHADOW_RIGHT)
        self.diagram.AddShape(shape)
        shape.Show(true)

        evthandler = MyEvtHandler()
        evthandler.menu = self.shapeMenu
        evthandler.view = self
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)

        return len(self.shapes) -1


    def OnDestroy(self, evt):
        # Do some cleanup
        for shape in self.diagram.GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)
                shape.Destroy()
        self.diagram.Destroy()



##    def OnBeginDragLeft(self, x, y, keys):
##        self.log.write("OnBeginDragLeft: %s, %s, %s\n" % (x, y, keys))
##
##    def OnEndDragLeft(self, x, y, keys):
##        self.log.write("OnEndDragLeft: %s, %s, %s\n" % (x, y, keys))

    def OnLeftClick(self, x, y, keys):
        """
        wxShapeCanvas::OnLeftClick
        void OnLeftClick(double x, double y, int keys = 0)

        Called when a left click event on the canvas background is detected by OnEvent. You may override this member; by default it does nothing.

        keys is a bit list of the following:


        KEY_SHIFT
        KEY_CTRL
        """
        self.DeselectAllShapes()

    def DeselectAllShapes(self):
        shapeList = self.diagram.GetShapeList()
        toUnselect = []
        for s in shapeList:
            if s.Selected():
                # If we unselect it now then some of the objects in
                # shapeList will become invalid (the control points are
                # shapes too!) and bad things will happen...
                toUnselect.append(s)

        if toUnselect:
            canvas = self.diagram.GetCanvas()
            dc = wxClientDC(self)        # NEW! handles scrolled situations
            canvas.PrepareDC(dc)

            for s in toUnselect:
                s.Select(False, dc)
            canvas.Redraw(dc)

#----------------------------------------------------------------------

#def runTest(frame, nb, log):
#    win = TestWindow(nb, log, frame)
#    return win

#----------------------------------------------------------------------

class __Cleanup:
    cleanup = wxOGLCleanUp
    def __del__(self):
        self.cleanup()

# when this module gets cleaned up then wxOGLCleanUp() will get called
__cu = __Cleanup()








overview = """\
The Object Graphics Library is a library supporting the creation and
manipulation of simple and complex graphic images on a canvas.

"""



#if __name__ == '__main__':
#    import sys,os
#    import run
#    run.main(['', os.path.basename(sys.argv[0])])



class Log:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)
    write = WriteText



class BoaApp(wx.App):
    def OnInit(self):
        wxInitAllImageHandlers()

        #self.main = wxFrame1.create(None)

        #self.main = TestWindow(parent=self, log=None, frame=None)

        self.andyapptitle = 'PyNsource GUI - Python Reverse Engineering Tool - Python Code into UML.'



        self.frame = Frame(None, -1, self.andyapptitle, pos=(50,50), size=(0,0),
                        style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.DEFAULT_FRAME_STYLE)
        self.frame.CreateStatusBar()
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu2 = wx.Menu()


        menu.Append(103, "File &Import...\tCtrl-I", "Import Python Source Files")
        wx.EVT_MENU(self, 103, self.FileImport)

        menu.Append(1055, "File Import &Recursive...", "Import Python Source Files PLUS all modules imported by your sources - WARNING - may generate lots of UML!!")
        wx.EVT_MENU(self, 1055, self.RecursivePathImport)


        menu.AppendSeparator()

        menu.Append(102, "File &New\tCtrl-N", "New")
        wx.EVT_MENU(self, 102, self.FileNew)

        menu.AppendSeparator()

        menu.Append(104, "File &Open\tCtrl-O", "Open")
        wx.EVT_MENU(self, 104, self.FileOpen)

        menu.Append(105, "File &Save\tCtrl-S", "Save")
        wx.EVT_MENU(self, 105, self.FileSave)

        menu.AppendSeparator()

        menu.Append(1056, "File &Print / Preview\tCtrl-P", "Print")
        wx.EVT_MENU(self, 1056, self.FilePrint)

        menu.AppendSeparator()

        menu.Append(106, "&About...", "About...")
        wx.EVT_MENU(self, 106, self.OnAbout)

        menu.AppendSeparator()

        menu.Append(101, "E&xit\tAlt-X", "Exit demo")
        wx.EVT_MENU(self, 101, self.OnButton)

        # -----------

        menu2.Append(122, "&Delete Node (r.mouse click)", "Delete Node")
        wx.EVT_MENU(self, 122, self.OnDeleteNode)

        menu2.AppendSeparator()

        menu2.Append(123, "&Layout", "Layout")
        wx.EVT_MENU(self, 123, self.OnLayout)

        menu2.Append(124, "&Refresh", "Refresh")
        wx.EVT_MENU(self, 124, self.OnRefresh)



        menuBar.Append(menu, "&File")
        menuBar.Append(menu2, "&Edit")
        self.frame.SetMenuBar(menuBar)
        self.frame.Show(True)
        wx.EVT_CLOSE(self.frame, self.OnCloseFrame)

        #win = self.demoModule.runTest(frame, frame, Log())
        #win = runTest(frame, frame, )
        self.win = TestWindow(self.frame, Log(), self.frame)
        self.win.secretredrawmethod = self.OnRefresh    # Hack so can do a high level refresh screen after a delete node event.

        # a window will be returned if the demo does not create
        # its own top-level window
        if self.win:
            # so set the frame to a good size for showing stuff
            self.frame.SetSize(WINDOW_SIZE)
            self.win.SetFocus()

        else:
            # otherwise the demo made its own frame, so just put a
            # button in this one
            if hasattr(self.frame, 'otherWin'):
                b = wx.Button(self.frame, -1, " Exit ")
                self.frame.SetSize((200, 100))
                wx.EVT_BUTTON(self.frame, b.GetId(), self.OnButton)
            else:
                # It was probably a dialog or something that is already
                # gone, so we're done.
                self.frame.Destroy()
                return True

        self.SetTopWindow(self.frame)



        #self.main.Show()
        #self.SetTopWindow(self.main)

        return True


    def RecursivePathImport(self,event=None):
        dlg = wxFileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wxOPEN|wxMULTIPLE, pos=wxDefaultPosition)
        if dlg.ShowModal() == wxID_OK:
            filenames = dlg.GetPaths() # dlg.GetFilename()
            print 'Importing...'
            wxBeginBusyCursor(cursor=wxHOURGLASS_CURSOR)
            # self.fileloadhandler(filename)
            print filenames

            self.fileList = []
            self.DoRecursivePathImport( os.path.split(filenames[0])[0] )
            print self.fileList
            self.win.Go(files=self.fileList)

            self._HackToForceTheScrollbarToShowUp()

            wxEndBusyCursor()
            print 'Import - Done.'


    def _HackToForceTheScrollbarToShowUp(self):
            """
            sizeX,sizeY = WINDOW_SIZE
            self.frame.SetSize((sizeX+1,sizeY+1))
            self.frame.SetSize((sizeX,sizeY))
            """

            # Actual size of the window
            oldSize = self.frame.GetSize()

            # Set the window size to something different
            self.frame.SetSize((oldSize[0]+1,oldSize[1]+1))

            # Return the size to what it was
            self.frame.SetSize(oldSize)



    def DoRecursivePathImport(self,dir):
        if( os.path.split(dir)[1] == "CVS"):
            #print dir,os.path.split(dir)[0]
            return

        for f in os.listdir(dir):
            pathname = os.path.join( dir, f )
            mode = os.stat(pathname)[stat.ST_MODE]
            if stat.S_ISDIR(mode):
                # It's a directory, recurse into it
                self.RecursivePathImport(pathname)
            elif stat.S_ISREG(mode):
                # It's a file
                if( os.path.splitext(f)[1] != ".pyc" and f != "__init__.py" ):
                    self.fileList.append( os.path.join(dir,f) )

    def FileImport(self, event):
        dlg = wxFileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wxOPEN|wxMULTIPLE, pos=wxDefaultPosition)
        if dlg.ShowModal() == wxID_OK:
            filenames = dlg.GetPaths() # dlg.GetFilename()
            print 'Importing...'
            wxBeginBusyCursor(cursor=wxHOURGLASS_CURSOR)
            # self.fileloadhandler(filename)
            print filenames

            self.win.Go(files=filenames)

            wxEndBusyCursor()
            print 'Import - Done.'

        self._HackToForceTheScrollbarToShowUp()


    def FileNew(self, event):
        self.win.Clear()

    def FileOpen(self, event):
        self.MessageBox("Sorry, FileOpen not implemented yet.")
        self.win.diagram.LoadFile('c:\\try\\testUml.txt')
        return
        """
        dlg = wxFileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wxOPEN|wxMULTIPLE, pos=wxDefaultPosition)
        if dlg.ShowModal() == wxID_OK:
            filenames = dlg.GetPaths() # dlg.GetFilename()
            print 'Importing...'
            wxBeginBusyCursor(cursor=wxHOURGLASS_CURSOR)
            # self.fileloadhandler(filename)
            print filenames
            wxEndBusyCursor()
            print 'Import - Done.'
        """

    def FileSave(self, event):
        self.MessageBox("Sorry, FileSave not implemented yet.")
        return
        self.win.diagram.SaveFile('c:\\try\\testUml.txt')
        """
        dlg = wxFileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wxOPEN|wxMULTIPLE, pos=wxDefaultPosition)
        if dlg.ShowModal() == wxID_OK:
            filenames = dlg.GetPaths() # dlg.GetFilename()
            print 'Importing...'
            wxBeginBusyCursor(cursor=wxHOURGLASS_CURSOR)
            # self.fileloadhandler(filename)
            print filenames
            wxEndBusyCursor()
            print 'Import - Done.'
        """


    def FilePrint(self, event):
        self.MessageBox("""
Helpful Reminder:

   Ensure you have resized your UML diagram
   to be big enough to fit most of your UML
   otherwise the print preview will only
   show a partial diagram. (I hope to auto fix this soon)

""")

        from printframework import MyPrintout

        self.printData = wxPrintData()
        self.printData.SetPaperId(wxPAPER_LETTER)

        self.box = wxBoxSizer(wxVERTICAL)
        self.canvas = self.win.GetDiagram().GetCanvas()

        #self.log.WriteText("OnPrintPreview\n")
        printout = MyPrintout(self.canvas)
        printout2 = MyPrintout(self.canvas)
        self.preview = wxPrintPreview(printout, printout2, self.printData)
        if not self.preview.Ok():
            self.log.WriteText("Houston, we have a problem...\n")
            return

        frame = wxPreviewFrame(self.preview, self.frame, "This is a print preview")

        frame.Initialize()
        frame.SetPosition(self.frame.GetPosition())
        frame.SetSize(self.frame.GetSize())
        frame.Show(True)




    def OnAbout(self, event):
        self.MessageBox(aboutmsg)


    def OnDeleteNode(self, event):
        self.MessageBox("To delete a node simply right click with your mouse on it.")

    def OnLayout(self, event):
        self.win.ArrangeShapes()
        self.win.redraw()
        self._HackToForceTheScrollbarToShowUp()

    def OnRefresh(self, event):
        self.win.redraw2()
        self._HackToForceTheScrollbarToShowUp()  # this is just as necessary to get the screen to refresh.

    def MessageBox(self, msg):
        dlg = wxMessageDialog(self.frame, msg,
                              'A Message Box', wxOK | wxICON_INFORMATION)
                              #wxYES_NO | wxNO_DEFAULT | wxCANCEL | wxICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnButton(self, evt):
        self.frame.Close(True)


    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.win.ShutdownDemo()
        evt.Skip()

def main():
    application = BoaApp(0)
#----------------------------------------------------------------------
# This creates some pens and brushes that the OGL library uses.

    wxOGLInitialize()    # moved here for wxpython 2.5 compatibility

#----------------------------------------------------------------------
    application.MainLoop()

if __name__ == '__main__':
    main()
