"""
    PyNSource GUI
    -------------
    
    LICENSE: GPL 3
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx
import wx.lib.ogl as ogl
from wx import Frame
import os, stat
from messages import *
from gui_umlshapes import *

APP_VERSION = 1.51
WINDOW_SIZE = (640,480)
IMAGENODES = False
MULTI_TAB_GUI = True


class MyEvtHandler(ogl.ShapeEvtHandler):
    def __init__(self, log, frame):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.statbarFrame = frame

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        width, height = shape.GetBoundingBoxMax()
        self.statbarFrame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)" % (x, y, width, height))

    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        canvas = shape.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        def GetCanvasDc(s):
            canvas = s.GetCanvas()
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            return canvas, dc

        if shape.Selected():
            shape.Select(False, dc)
            canvas.Refresh(False)
        else:
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
                    canvas, dc = GetCanvasDc(s)
                    s.Select(False, dc)
                canvas.Refresh(False)

        self.UpdateStatusBar(shape)


    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        self.UpdateStatusBar(shape)

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
        self.UpdateStatusBar(self.GetShape())

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        self.UpdateStatusBar(shape)
        if "wxMac" in wx.PlatformInfo:
            shape.GetCanvas().Refresh(False) 

    def OnPopupItemSelected(self, event): 
        item = self.popupmenu.FindItemById(event.GetId()) 
        text = item.GetText() 
        #wx.MessageBox("You selected item '%s'" % text)
        if text == "Delete Node":
            self.RightClickDeleteNode()
        
    def OnRightClick(self, x, y, keys, attachment):
        #self.log.WriteText("%s\n" % self.GetShape())
        self.popupmenu = wx.Menu()     # Creating a menu
        item = self.popupmenu.Append(2011, "Delete Node")
        self.statbarFrame.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        item = self.popupmenu.Append(2012, "Cancel")
        self.statbarFrame.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.statbarFrame.PopupMenu(self.popupmenu, wx.Point(x,y))

    def RightClickDeleteNode(self):
        self.GetShape().GetCanvas().CmdZapShape(self.GetShape())

import sys, glob
from gen_java import PySourceAsJava

class UmlShapeCanvas(ogl.ShapeCanvas):
    scrollStepX = 10
    scrollStepY = 10
    classnametoshape = {}

    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)
        maxWidth  = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth/20, maxHeight/20)

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE") #wxWHITE)

        self.SetDiagram(ogl.Diagram())
        self.GetDiagram().SetCanvas(self)
        self.save_gdi = []
        wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)

        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.font2 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)

        self.associations_generalisation = None
        self.associations_composition = None

    def CmdZapShape(self, shape):
        canvas = self
        diagram = self.GetDiagram()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        
        if shape.Selected():
            shape.Select(False, dc)
            canvas.Refresh(False)

        # should do list clone instead, just don't want pointer want true copy of refs
        lineList = shape.GetLines()
        toDelete = []
        for line in shape.GetLines():
            toDelete.append(line)
            
        for line in toDelete:
            line.Unlink()
            #shape.RemoveLine(line)
            diagram.RemoveShape(line)            

        # Uml related....
        classnames = self.classnametoshape.keys()
        for classname in classnames:
            if self.classnametoshape[classname] == shape:
                print 'found class to delete: ', classname
                break

        del self.classnametoshape[classname]
        """
        Too hard to remove the classname from these structures since these are tuples
        between two classes.  Harmless to keep them in here.
        """
        #if class1, class2 in self.associations_generalisation:
        #    self.associations_generalisation.remove(shape)
        #if shape in self.associations_composition:
        #    self.associations_composition.remove(shape)

        assert shape in self.umlboxshapes
        diagram.RemoveShape(shape)

    def Clear(self):
        self.GetDiagram().DeleteAllShapes()

        dc = wx.ClientDC(self)
        self.GetDiagram().Clear(dc)   # only ends up calling dc.Clear() - I wonder if this clears the screen?

        self.save_gdi = []

        # THIS is the one that we need....
        self.classnametoshape = {}

        # and maybe this too
        self.associations_generalisation = None
        self.associations_composition = None

    def _Process(self, filepath):
        print '_Process', filepath

        p = PySourceAsJava()
        p.optionModuleAsClass = 0
        p.verbose = 0
        p.Parse(filepath)

        for classname, classentry in p.classlist.items():
            #print 'CLASS', classname, classentry

            # These are a list of (attr, otherclass) however they imply that THIS class
            # owns all those other classes.
            
            for attr, otherclass in classentry.classdependencytuples:
                self.associations_composition.append((otherclass, classname))  # reverse direction so round black arrows look ok

            # Generalisations
            if classentry.classesinheritsfrom:
                for parentclass in classentry.classesinheritsfrom:

                    if parentclass.find('.') <> -1:         # fix names like "unittest.TestCase" into "unittest"
                        parentclass = parentclass.split('.')[0] # take the lhs

                    self.associations_generalisation.append((classname, parentclass))

            # Build the UML shape
            #
            if classname not in self.classnametoshape:
                if not IMAGENODES:
                    shape = DividedShape(width=100, height=150, canvas=self)
                else:
                    F = 'Research\\wx doco\\Images\\SPLASHSCREEN.BMP'
                    # wx.ImageFromBitmap(bitmap) and wx.BitmapFromImage(image)
                    shape = ogl.BitmapShape()
                    img = wx.Image(F, wx.BITMAP_TYPE_ANY)
                    bmp = wx.BitmapFromImage(img)
                    shape.SetBitmap(bmp)

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

                regionName.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ)
                shape.region1 = regionName  # Andy added, for later external reference to classname from just having the shap instance.

                shape.AddRegion(regionName)
                shape.AddRegion(regionAttribs)
                shape.AddRegion(regionMeths)

                shape.SetSize(maxWidth + 10, totHeight + 10)

                if not IMAGENODES:
                    shape.SetRegionSizes()

                dsBrush = wx.Brush("WHEAT", wx.SOLID)
                ds = self.MyAddShape(shape, pos[0], pos[1], wx.BLACK_PEN, dsBrush, '') # get back instance - but already had it...

                if not IMAGENODES:
                    shape.FlushText()

                # Record the name to shape map so that we can wire up the links later.
                self.classnametoshape[classname] = ds
            else:
                print 'Skipping', classname, 'already built shape...'

    def _BuildAuxClasses(self, classestocreate=None):
            if not classestocreate:
                classestocreate = ('variant', 'unittest', 'list', 'object', 'dict')  # should add more classes and add them to a jar file to avoid namespace pollution.
            for classname in classestocreate:
                rRectBrush = wx.Brush("MEDIUM TURQUOISE", wx.SOLID)
                dsBrush = wx.Brush("WHEAT", wx.SOLID)
                ds = self.MyAddShape(DividedShapeSmall(100, 30, self), 50, 145, wx.BLACK_PEN, dsBrush, '')
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

        if files:
            for f in files:
                self._Process(f)    # Build a shape with all attrs and methods, and prepare association dict

        if path:
            param = path
            globbed = []
            files = glob.glob(param)
            globbed += files
            #print 'parsing', globbed

            for directory in globbed:
                if '*' in directory or '.' in directory:
                    filepath = directory
                else:
                    filepath = os.path.join(directory, "*.py")
                globbed2 = glob.glob(filepath)
                for f in globbed2:
                    self._Process(f)    # Build a shape with all attrs and methods, and prepare association dict

        self.DrawAssocLines(self.associations_generalisation, ogl.ARROW_ARROW)
        self.DrawAssocLines(self.associations_composition, ogl.ARROW_FILLED_CIRCLE)

        # Layout
        self.ArrangeShapes()

    def DrawAssocLines(self, associations, arrowtype):
        for fromClassname, toClassname in associations:
            #print 'DrawAssocLines', fromClassname, toClassname

            if fromClassname not in self.classnametoshape:
                self._BuildAuxClasses(classestocreate=[fromClassname]) # Emergency creation of some unknown class.
            fromShape = self.classnametoshape[fromClassname]

            if toClassname not in self.classnametoshape:
                self._BuildAuxClasses(classestocreate=[toClassname]) # Emergency creation of some unknown class.
            toShape = self.classnametoshape[toClassname]

            line = ogl.LineShape()
            line.SetCanvas(self)
            line.SetPen(wx.BLACK_PEN)
            line.SetBrush(wx.BLACK_BRUSH)
            line.AddArrow(arrowtype)
            line.MakeLineControlPoints(2)
            fromShape.AddLine(line, toShape)
            self.GetDiagram().AddShape(line)
            line.Show(True)

    def RedrawEverything(self):
        diagram = self.GetDiagram()
        canvas = self
        assert self == canvas == diagram.GetCanvas()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        for shape in self.umlboxshapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
            if not IMAGENODES:
                shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)

        # Hack To Force The Scrollbar To Show Up
        # Set the window size to something different
        # Return the size to what it was
        oldSize = self.frame.GetSize()
        self.frame.SetSize((oldSize[0]+1,oldSize[1]+1))
        self.frame.SetSize(oldSize)

    def newRegion(self, font, name, textLst, maxWidth, totHeight = 10):
        # Taken from Boa, but put into the canvas class instead of the scrolled window class.
        region = ogl.ShapeRegion()
        dc = wx.ClientDC(self)  # self is the canvas
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
        remainingshapes = [ shape for shape in self.umlboxshapes if shape not in mostshapesinpriorityorder ]

        return mostshapesinpriorityorder + remainingshapes


    def ArrangeShapes(self):

        shapeslist = self.SortShapes()

        dc = wx.ClientDC(self)
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

            whiteSpace = 50
            shapeX, shapeY = self.getShapeSize(classShape)

            if shapeY >= biggestYthisrow:
                biggestYthisrow = shapeY

            # snap to diagram grid coords
            #csX, csY = self.GetDiagram().Snap((shapeX/2.0)+x, (shapeY/2.0)+y)
            #csX, csY = self.GetDiagram().Snap(x, y)
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
        self.setSize(wx.Size(int(width+50), int(height+50))) # fudge factors to keep some extra space

        # Now move the shapes into place.
        for (pos, classShape) in zip(positions, shapeslist):
            #print pos, classShape.region1.GetText()
            x, y = pos
            classShape.Move(dc, x, y, False)

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
        # Composites have to be moved for all children to get in place
        if isinstance(shape, ogl.CompositeShape):
            dc = wx.ClientDC(self)
            self.PrepareDC(dc)
            shape.Move(dc, x, y)
        else:
            shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        if pen:    shape.SetPen(pen)
        if brush:  shape.SetBrush(brush)
        if text:
            for line in text.split('\n'):
                shape.AddText(line)
        self.GetDiagram().AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler(self.log, self.frame)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        return shape

    def get_umlboxshapes(self):
        return [s for s in self.GetDiagram().GetShapeList() if isinstance(s, DividedShape)]

    umlboxshapes = property(get_umlboxshapes)
    
    def OnDestroy(self, evt):
        for shape in self.GetDiagram().GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)

    def OnLeftClick(self, x, y, keys):
        # keys is a bit list of the following: KEY_SHIFT  KEY_CTRL
        self.DeselectAllShapes()

    def DeselectAllShapes(self):
        shapeList = self.GetDiagram().GetShapeList()

        def GetCanvasDc(s):
            canvas = s.GetCanvas()
            dc = wx.ClientDC(canvas)        # NEW! handles scrolled situations
            canvas.PrepareDC(dc)
            return canvas, dc
            
        # If we unselect too early, some of the objects in
        # shapeList will become invalid (the control points are
        # shapes too!) and bad things will happen...
        toUnselect = []
        for s in shapeList:
            if s.Selected():
                toUnselect.append(s)

        if toUnselect:
            for s in toUnselect:
                canvas, dc = GetCanvasDc(s)
                s.Select(False, dc)
                
            canvas, dc = GetCanvasDc(s)
            canvas.Refresh(False)

class Log:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)
    write = WriteText

from gui_imageviewer import ImageViewer

class MainApp(wx.App):
    def OnInit(self):
        self.log = Log()
        wx.InitAllImageHandlers()
        self.andyapptitle = 'PyNsource GUI - Python Code into UML'

        self.frame = Frame(None, -1, self.andyapptitle, pos=(50,50), size=(0,0),
                        style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.DEFAULT_FRAME_STYLE)
        self.frame.CreateStatusBar()
        self.InitMenus()

        if MULTI_TAB_GUI:
            self.notebook = wx.Notebook(self.frame, -1)
            self.umlwin = UmlShapeCanvas(self.notebook, Log(), self.frame)
            self.yuml = ImageViewer(self.notebook) # wx.Panel(self.notebook, -1)
            self.asciiart = wx.Panel(self.notebook, -1)
    
            self.notebook.AddPage(self.umlwin, "UML")
            self.notebook.AddPage(self.yuml, "yUml")
            self.notebook.AddPage(self.asciiart, "Ascii Art")
    
            self.multiText = wx.TextCtrl(self.asciiart, -1,
            "Here is a looooooooooooooong line "
            "of text set in the control.\n\n"
            "See that it wrapped, and that "
            "this line is after a blank",
            style=wx.TE_MULTILINE)
            bsizer = wx.BoxSizer()
            bsizer.Add(self.multiText, 1, wx.EXPAND)
            self.asciiart.SetSizerAndFit(bsizer)
            self.multiText.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False))
            
            self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnTabPageChanged)
            
        else:
            self.umlwin = UmlShapeCanvas(self.frame, Log(), self.frame)
            
        ogl.OGLInitialize()  # creates some pens and brushes that the OGL library uses.
        
        # Set the frame to a good size for showing stuff
        self.frame.SetSize(WINDOW_SIZE)
        self.umlwin.SetFocus()
        self.SetTopWindow(self.frame)

        self.frame.Show(True)
        wx.EVT_CLOSE(self.frame, self.OnCloseFrame)

        # Debug bootstrap
        self.frame.SetSize((1024,768))
        self.umlwin.Go(files=[os.path.abspath( __file__ )])
        self.umlwin.RedrawEverything()
        
        return True

    def OnTabPageChanged(self, event):
        if event.GetSelection() == 0:  # ogl
            pass
        elif event.GetSelection() == 1:  # yuml
            #self.yuml.ViewImage(thefile='../outyuml.png')
            pass
        elif event.GetSelection() == 2:  # ascii art
            pass
        
        event.Skip()
         
    def InitMenus(self):
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()
        menu2 = wx.Menu()
        menu3 = wx.Menu()
        menu4 = wx.Menu()

        self.next_menu_id = 200
        def Add(menu, s1, s2, func):
            menu.Append(self.next_menu_id, s1, s2)
            wx.EVT_MENU(self, self.next_menu_id, func)
            self.next_menu_id +=1

        Add(menu1, "File &Import...\tCtrl-I", "Import Python Source Files", self.FileImport)
        Add(menu1, "File &Import yUml...\tCtrl-O", "Import Python Source Files", self.FileImport2)
        Add(menu1, "File &Import Ascii Art...\tCtrl-J", "Import Python Source Files", self.FileImport3)
        menu1.AppendSeparator()
        Add(menu1, "&Clear\tCtrl-N", "Clear Diagram", self.FileNew)
        menu1.AppendSeparator()
        Add(menu1, "File &Print / Preview...\tCtrl-P", "Print", self.FilePrint)
        menu1.AppendSeparator()
        Add(menu1, "E&xit\tAlt-X", "Exit demo", self.OnButton)
        
        Add(menu2, "&Delete Class", "Delete Node", self.OnDeleteNode)
        
        Add(menu3, "&Layout UML", "Layout UML", self.OnLayout)
        Add(menu3, "&Refresh", "Refresh", self.OnRefreshUmlWindow)
        
        Add(menu4, "&Help...", "Help", self.OnHelp)
        Add(menu4, "&Visit PyNSource Website...", "PyNSource Website", self.OnVisitWebsite)
        menu4.AppendSeparator()
        Add(menu4, "&Check for Updates...", "Check for Updates", self.OnCheckForUpdates)
        Add(menu4, "&About...", "About...", self.OnAbout)

        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&Edit")
        menuBar.Append(menu3, "&Layout")
        menuBar.Append(menu4, "&Help")
        self.frame.SetMenuBar(menuBar)
        
    def FileImport(self, event):
        self.notebook.SetSelection(0)
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            self.umlwin.Go(files=filenames)
            self.umlwin.RedrawEverything()
            wx.EndBusyCursor()
            print 'Import - Done.'

    def FileImport2(self, event):
        from gen_yuml import PySourceAsYuml
        import urllib
        
        self.notebook.SetSelection(1)
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            
            files=filenames
            p = PySourceAsYuml()
            p.optionModuleAsClass = 0
            p.verbose = 0
            if files:
                for f in files:
                    p.Parse(f)
            p.CalcYumls()
            print p

            #yuml_txt = "[Customer]+1->*[Order],[Order]++1-items >*[LineItem],[Order]-0..1>[PaymentMethod]"
            yuml_txt = ','.join(str(p).split())
            baseUrl = 'http://yuml.me/diagram/dir:lr;scruffy/class/'
            url = baseUrl + urllib.quote(yuml_txt)
            self.yuml.ViewImage(url=url)

            wx.EndBusyCursor()
            print 'Import - Done.'

    def FileImport3(self, event):
        from gen_asciiart import PySourceAsText
        import urllib
        
        self.notebook.SetSelection(2)
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            
            files=filenames
            p = PySourceAsText()
            p.optionModuleAsClass = 0
            p.verbose = 0
            if files:
                for f in files:
                    p.Parse(f)
            print p

            self.multiText.SetValue(str(p))
            self.multiText.ShowPosition(0)

            wx.EndBusyCursor()
            print 'Import - Done.'

    def FileNew(self, event):
        self.umlwin.Clear()
    def FilePrint(self, event):

        from printframework import MyPrintout

        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_LETTER)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.canvas = self.umlwin.GetDiagram().GetCanvas()

        #self.log.WriteText("OnPrintPreview\n")
        printout = MyPrintout(self.canvas, self.log)
        printout2 = MyPrintout(self.canvas, self.log)
        self.preview = wx.PrintPreview(printout, printout2, self.printData)
        if not self.preview.Ok():
            self.log.WriteText("Houston, we have a problem...\n")
            return

        frame = wx.PreviewFrame(self.preview, self.frame, "This is a print preview")

        frame.Initialize()
        frame.SetPosition(self.frame.GetPosition())
        frame.SetSize(self.frame.GetSize())
        frame.Show(True)




    def OnAbout(self, event):
        self.MessageBox(ABOUT_MSG.strip() %  APP_VERSION)

    def OnVisitWebsite(self, event):
        import webbrowser
        webbrowser.open(WEB_PYNSOURCE_HOME_URL)

    def OnCheckForUpdates(self, event):
        import urllib2
        s = urllib2.urlopen(WEB_VERSION_CHECK_URL).read()
        s = s.replace("\r", "")
        info = eval(s)
        ver = info["latest_version"]
        
        if ver > APP_VERSION:
            msg = WEB_UPDATE_MSG % (ver, info["latest_announcement"].strip())
            retCode = wx.MessageBox(msg.strip(), "Update Check", wx.YES_NO | wx.ICON_QUESTION)  # MessageBox simpler than MessageDialog
            if (retCode == wx.YES):
                import webbrowser
                webbrowser.open(info["download_url"])
        else:
            self.MessageBox("You already have the latest version:  %s" % APP_VERSION)
    
    def OnHelp(self, event):
        self.MessageBox(HELP_MSG.strip())

    def OnDeleteNode(self, event):
        for shape in self.umlwin.GetDiagram().GetShapeList():
            if shape.Selected():
                self.umlwin.CmdZapShape(shape)

    def OnLayout(self, event):
        if self.umlwin.GetDiagram().GetCount() == 0:
            self.MessageBox("Nothing to layout.  Import a python source file first.")
            return
        
        self.umlwin.ArrangeShapes()
        self.umlwin.RedrawEverything()

    def OnRefreshUmlWindow(self, event):
        self.umlwin.RedrawEverything()

    def MessageBox(self, msg):
        dlg = wx.MessageDialog(self.frame, msg, 'Message', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnButton(self, evt):
        self.frame.Close(True)


    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.umlwin.ShutdownDemo()
        evt.Skip()

def main():
    application = MainApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()


