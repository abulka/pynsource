"""
PyNSource GUI
-------------

Andy Bulka
www.andypatterns.com

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

import random
import wx
import wx.lib.ogl as ogl
from wx import Frame
from wx import StandardPaths
import shelve
import os, stat
from messages import *
from gui_umlshapes import *
import thread

APP_VERSION = 1.6
WINDOW_SIZE = (1024,768)
MULTI_TAB_GUI = True

# compensate for the fact that x, y for a ogl shape are the centre of the shape, not the top left
def setpos(shape, x, y):
    width, height = shape.GetBoundingBoxMax()
    shape.SetX( x + width/2 )
    shape.SetY( y + height/2 )
def getpos(shape):
    width, height = shape.GetBoundingBoxMax()
    x = shape.GetX()
    y = shape.GetY()
    return x - width/2, y - height/2

         
class MyEvtHandler(ogl.ShapeEvtHandler):
    def __init__(self, log, frame, shapecanvas):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.frame = frame              # these are arbitrary initialisations
        self.shapecanvas = shapecanvas  # these are arbitrary initialisations

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        x, y = getpos(shape)
        width, height = shape.GetBoundingBoxMax()
        self.frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)" % (x, y, width, height))

    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        self._SelectNodeNow(x, y, keys, attachment)

    def _SelectNodeNow(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        shape.GetCanvas().SelectNodeNow(shape)
        self.UpdateStatusBar(shape)

    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        oldpos = getpos(shape)
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment) # super
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        newpos = getpos(shape)
        try:
            print shape.node.id, "moved from", oldpos, "to", newpos
            # Adjust the GraphNode to match the shape x,y
            shape.node.left, shape.node.top = newpos
        except:
            print "no node model attached to this shape!"
            
        self.UpdateStatusBar(shape)

        # Invoke overlap removal (unless hold down shift key)
        KEY_SHIFT = 1
        if keys & KEY_SHIFT:
            #shape.GetCanvas().stateofthenation()   # do we need this?  did quite well without it before
            pass
        else:
            shape.GetCanvas().stage2()

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        shape = self.GetShape()

        # super        
        ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
        
        width, height = shape.GetBoundingBoxMin()
        if hasattr(shape, 'node'):
            #print shape.node, "resized to", width, height
            #print shape.node.id, shape.node.left, shape.node.top, "resized to", width, height
            
            # Adjust the GraphNode to match the shape x,y
            shape.node.width, shape.node.height = width, height
            shape.node.left, shape.node.top = getpos(shape)
        
        self.UpdateStatusBar(self.GetShape())

        #wx.SafeYield()
        #time.sleep(0.2)
        
        shape.GetCanvas().stage2()
        
    #def OnEndSize(self, width, height):
    #    print "OnEndSize", width, height

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        self.UpdateStatusBar(shape)
        if "wxMac" in wx.PlatformInfo:
            shape.GetCanvas().Refresh(False) 

    def OnPopupItemSelected(self, event):
        item = self.popupmenu.FindItemById(event.GetId()) 
        text = item.GetText() 
        if text == "Delete\tDel":
            self.RightClickDeleteNode()
        elif text == "Properties...":
            self.NodeProperties()
        elif text == "Begin - Draw Line from this class\tq":
            self.GetShape().GetCanvas().NewEdgeMarkFrom()
        elif text == "End - Draw Line to this class\tw":
            self.GetShape().GetCanvas().NewEdgeMarkTo()
        elif text == "Reset Image Size":
            shape = self.GetShape()
            shape.ResetSize()
            #shape.GetCanvas().Refresh(False)   # don't seem to need since SelectNodeNow() might be doing it for us
            shape.GetCanvas().SelectNodeNow(shape)
            self.UpdateStatusBar(shape)

    def OnRightClick(self, x, y, keys, attachment):
        self._SelectNodeNow(x, y, keys, attachment)

        #self.log.WriteText("%s\n" % self.GetShape())
        self.popupmenu = wx.Menu()     # Creating a menu
        
        def MakeMenuItem(menu, msg):
            item = menu.Append(wx.NewId(), msg)
            self.frame.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)  # Not sure why but passing item is needed.  Not to find the menu item later, but to avoid crashes?  try two right click deletes followed by main menu edit/delete.  Official Bind 3rd parameter DOCO:  menu source - Sometimes the event originates from a different window than self, but you still want to catch it in self. (For example, a button event delivered to a frame.) By passing the source of the event, the event handling system is able to differentiate between the same event type from different controls.
            
        MakeMenuItem(self.popupmenu, "Properties...")
        self.popupmenu.AppendSeparator()

        menu_sub = wx.Menu()
        MakeMenuItem(menu_sub, "Begin - Draw Line from this class\tq")
        MakeMenuItem(menu_sub, "End - Draw Line to this class\tw")
        self.popupmenu.AppendMenu(wx.NewId(), "Draw Line", menu_sub)

        if self.GetShape().__class__.__name__ == 'BitmapShapeResizable':
            self.popupmenu.AppendSeparator()
            MakeMenuItem(self.popupmenu, "Reset Image Size")
        
        self.popupmenu.AppendSeparator()
        MakeMenuItem(self.popupmenu, "Delete\tDel")
        self.popupmenu.AppendSeparator()
        MakeMenuItem(self.popupmenu, "Cancel")
        
        
        self.frame.PopupMenu(self.popupmenu, wx.Point(x,y))

    def RightClickDeleteNode(self):
        self.GetShape().GetCanvas().CmdZapShape(self.GetShape())

    def OnLeftDoubleClick(self, x, y, keys, attachment):
        self.GetShape().GetCanvas().CmdEditShape(self.GetShape())

    def NodeProperties(self):
        self.GetShape().GetCanvas().CmdEditShape(self.GetShape())


import sys, glob
from generate_code.gen_java import PySourceAsJava
from umlworkspace import UmlWorkspace

from layout.layout_basic import LayoutBasic

from layout.snapshots import GraphSnapshotMgr
from layout.layout_spring import GraphLayoutSpring
from layout.overlap_removal import OverlapRemoval
from layout.blackboard import LayoutBlackboard
from layout.coordinate_mapper import CoordinateMapper

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

        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Bind(wx.EVT_CHAR, self.onKeyChar)
        self.working = False

        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.font2 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)

        self.umlworkspace = UmlWorkspace()
        #self.layout = LayoutBasic()
        #self.layout = LayoutBasic(leftmargin=0, topmargin=0, verticalwhitespace=0, horizontalwhitespace=0, maxclassesperline=5)
        self.layout = LayoutBasic(leftmargin=5, topmargin=5, verticalwhitespace=50, horizontalwhitespace=50, maxclassesperline=7)

        self.snapshot_mgr = GraphSnapshotMgr(graph=self.umlworkspace.graph, controller=self)
        self.coordmapper = CoordinateMapper(self.umlworkspace.graph, self.GetSize())
        self.layouter = GraphLayoutSpring(self.umlworkspace.graph, gui=self)
        self.overlap_remover = OverlapRemoval(self.umlworkspace.graph, margin=50, gui=self)
        self._kill_layout = False   # flag to communicate with layout engine.  aborting keypress in gui should set this to true

        @property
        def kill_layout(self):
          return self._kill_layout
        @kill_layout.setter
        def kill_layout(self, value):
          self._kill_layout = value
    
    def AllToLayoutCoords(self):
        self.coordmapper.AllToLayoutCoords()

    def AllToWorldCoords(self):
        self.coordmapper.AllToWorldCoords()

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()  # http://www.wxpython.org/docs/api/wx.KeyEvent-class.html

        if self.working:
            event.Skip()
            return
        self.working = True


        #if keycode == wx.WXK_DOWN:
        #    optimise = not event.ShiftDown()
        #    self.ReLayout(keep_current_positions=True, gui=self, optimise=optimise)
        #
        #elif keycode == wx.WXK_UP:
        #    optimise = not event.ShiftDown()
        #    self.ReLayout(keep_current_positions=False, gui=self, optimise=optimise)
        
        if keycode == wx.WXK_ESCAPE:
            print "ESC key detected: Abort Layout"
            self.kill_layout = True
        
        if keycode == wx.WXK_RIGHT:
            self.cmdLayoutExpand(event)
            
        elif keycode == wx.WXK_LEFT:
            self.cmdLayoutContract(event)

        elif keycode == wx.WXK_INSERT:
            self.CmdInsertNewNode()
        elif keycode == wx.WXK_DELETE:
            print "DELETE"
            selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
            if selected:
                shape = selected[0]
                self.CmdZapShape(shape)
        self.working = False
        event.Skip()

    def cmdLayoutExpand(self, event):
        if self.coordmapper.scale > 0.8:
            self.ChangeScale(-0.2, remap_world_to_layout=event.ShiftDown(), removeoverlaps=not event.ControlDown())
            #print "expansion ", self.coordmapper.scale
        else:
            print "Max expansion prevented.", self.coordmapper.scale

    def cmdLayoutContract(self, event):
        if self.coordmapper.scale < 3:
            self.ChangeScale(0.2, remap_world_to_layout=event.ShiftDown(), removeoverlaps=not event.ControlDown())
            #print "contraction ", self.coordmapper.scale
        else:
            print "Min expansion thwarted.", self.coordmapper.scale

    def onKeyChar(self, event):
        if event.GetKeyCode() >= 256:
            event.Skip()
            return
        if self.working:
            event.Skip()
            return
        self.working = True
        
        keycode = chr(event.GetKeyCode())

        if keycode == 'q':
            self.NewEdgeMarkFrom()

        elif keycode == 'w':
            self.NewEdgeMarkTo()
            
        elif keycode in ['1','2','3','4','5','6','7','8']:
            todisplay = ord(keycode) - ord('1')
            self.snapshot_mgr.Restore(todisplay)

        elif keycode in ['b', 'B']:
            self.CmdDeepLayout()
                
        elif keycode in ['l', 'L']:
            self.CmdLayout()
            
        elif keycode in ['d', 'D']:
            self.DumpStatus()
        
        self.working = False
        event.Skip()

    def DumpStatus(self):
        # Also called by Snapshot manager.
        # When create Snapshot manager we pass ourselves as a controller and DumpStatus() is expected to exist.
        import locale
        locale.setlocale(locale.LC_ALL, '')  # http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x
        
        print "v" * 50
        self.umlworkspace.Dump()
        print
        print "  MISC Scaling etc info "
        print
        self.coordmapper.DumpCalibrationInfo(dump_nodes=False)
        print "line-line intersections", len(self.umlworkspace.graph.CountLineOverLineIntersections())
        print "node-node overlaps", self.overlap_remover.CountOverlaps()
        print "line-node crossings", self.umlworkspace.graph.CountLineOverNodeCrossings()['ALL']/2 #, self.graph.CountLineOverNodeCrossings()
        print "bounds", self.umlworkspace.graph.GetBounds()


        #print "SHAPE to classname list: -------------------"
        #for shape in self.umlboxshapes:
        #    print 'shape', shape, shape.node.classname

        print
        print "^" * 50

  
    def CmdRememberLayout1(self):
        self.snapshot_mgr.QuickSave(slot=1)
    def CmdRememberLayout2(self):
        self.snapshot_mgr.QuickSave(slot=2)
    def CmdRestoreLayout1(self):
        self.snapshot_mgr.QuickRestore(slot=1)
    def CmdRestoreLayout2(self):
        self.snapshot_mgr.QuickRestore(slot=2)

    def DisplayDialogUmlNodeEdit(self, id, attrs, methods):
        """
        id, attrs, methods are lists of strings
        returns id, attrs, methods as lists of strings
        """
        from dialogs.DialogUmlNodeEdit import DialogUmlNodeEdit
        class EditDialog(DialogUmlNodeEdit):
            def OnClassNameEnter( self, event ):
                self.EndModal(wx.ID_OK) 
        dialog = EditDialog(None)

        dialog.txtClassName.Value, dialog.txtAttrs.Value, dialog.txtMethods.Value = id, "\n".join(attrs), "\n".join(methods)
        if dialog.ShowModal() == wx.ID_OK:
            #wx.MessageBox("got wx.ID_OK")
            result = True
            id = dialog.txtClassName.Value

            def string_to_list_smart(s):
                s = s.strip()
                if s == "":
                    return []
                else:
                    return s.split('\n')

            attrs = string_to_list_smart(dialog.txtAttrs.Value)
            methods = string_to_list_smart(dialog.txtMethods.Value)
            print id, attrs, methods
        else:
            result, id, attrs, methods = False, None, None, None
        dialog.Destroy()
        return (result, id, attrs, methods)
        
    def CmdInsertNewNode_OLD_SIMPLE(self):
        id = 'D' + str(random.randint(1,99))
        dialog = wx.TextEntryDialog ( None, 'Enter an id string:', 'Create a new node', id )
        if dialog.ShowModal() == wx.ID_OK:
            id = dialog.GetValue()
            node = self.umlworkspace.AddSimpleNode(id)
            shape = self.createNodeShape(node)
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            node.shape.Show(True)
            self.stateofthenation()
        dialog.Destroy()
        
    def CmdInsertNewComment(self):
        id = 'D' + str(random.randint(1,9999))
        dialog = wx.TextEntryDialog ( None, 'Enter a comment:', 'New Comment', "hello\nthere") #, wx.TE_MULTILINE )
        if dialog.ShowModal() == wx.ID_OK:
            comment = dialog.GetValue() + "\nfred"
            node = self.umlworkspace.AddCommentNode(id, comment)
            shape = self.createCommentShape(node)
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            node.shape.Show(True)
            self.stateofthenation()
        dialog.Destroy()
        
        
    def CmdInsertNewImageNode(self, filename=None):
        if not filename:
            curr_dir = os.path.dirname( os.path.abspath( __file__ ) )
            filename = os.path.join(curr_dir, '..\\Research\\wx doco\\Images\\SPLASHSCREEN.BMP')
        
        self.CreateImageShape(filename)
        self.stage2(force_stateofthenation=True) # if want overlap removal and proper refresh
        #self.SelectNodeNow(node.shape)
            
    def CmdInsertNewNode(self):
        result, id, attrs, methods = self.DisplayDialogUmlNodeEdit(id='D' + str(random.randint(1,99)),
                                            attrs=['attribute 1', 'attribute 2', 'attribute 3'],
                                            methods=['method A', 'method B', 'method C', 'method D'])

        if result:
            # Ensure unique name
            while self.umlworkspace.graph.FindNodeById(id):
                id += '2'

            node = self.umlworkspace.AddUmlNode(id, attrs, methods)
            shape = self.CreateUmlShape(node)
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            
            node.shape.Show(True)
            
            #self.stateofthenation() # if want simple refresh
            #self.stage2() # if want overlap removal
            self.stage2(force_stateofthenation=True) # if want overlap removal and proper refresh
            
            self.SelectNodeNow(node.shape)
            

    def CmdEditShape(self, shape):
        node = shape.node
         
        result, id, attrs, methods = self.DisplayDialogUmlNodeEdit(node.id, node.attrs, node.meths)
        if result:
            self.umlworkspace.graph.RenameNode(node, id)   # need special rename cos of underlying graph plumbing - perhaps put setter on id?
            node.attrs = attrs
            node.meths = methods
    
            self.CmdZapShape(shape, deleteNodeToo=False)
            
            shape = self.CreateUmlShape(node)
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
    
            # TODO Hmmm - how does new shape get hooked up if the line mapping uses old name!??  Cos of graph's edge info perhaps?
            for edge in self.umlworkspace.graph.edges:
                self.CreateUmlEdge(edge)
                
            node.shape.Show(True)
            self.stateofthenation()

            # TODO Why doesn't this select the node?
            #self.SelectNodeNow(node.shape)
            #self.stateofthenation()

        
    def SelectNodeNow(self, shape):
        canvas = shape.GetCanvas()

        canvas.DeselectAllShapes()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        shape.Select(True, dc)  # could pass None as dc if you don't want to trigger the OnDrawControlPoints(dc) handler immediately - e.g. if you want to do a complete redraw of everything later anyway
        #canvas.Refresh(False)   # t/f or don't use - doesn't seem to make a difference
        
        #self.UpdateStatusBar(shape)  # only available in the shape evt handler (this method used to live there...)

    def CmdZapShape(self, shape, deleteNodeToo=True):
        # Model/Uml related....
        self.umlworkspace.DeleteShape(shape, deleteNodeToo)
        # Delete View
        self._ZapShape(shape)
        
    def _ZapShape(self, shape):
        # View
        self.DeselectAllShapes()
        for line in shape.GetLines()[:]:
            line.Delete()
        shape.Delete()

    def Clear(self):
        self.GetDiagram().DeleteAllShapes()

        dc = wx.ClientDC(self)
        self.GetDiagram().Clear(dc)   # only ends up calling dc.Clear() - I wonder if this clears the screen?

        self.save_gdi = []
        
        self.umlworkspace.Clear()

    def NewEdgeMarkFrom(self):
        selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
        if not selected:
            print "Please select a node"
            return
        
        self.new_edge_from = selected[0].node
        print "From", self.new_edge_from.id

    def NewEdgeMarkTo(self):
        selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
        if not selected:
            print "Please select a node"
            return
        
        tonode = selected[0].node
        print "To", tonode.id
        
        if self.new_edge_from == None:
            print "Please set from node first"
            return
        
        if self.new_edge_from.id == tonode.id:
            print "Can't link to self"
            return
        
        if not self.umlworkspace.graph.FindNodeById(self.new_edge_from.id):
            print "From node %s doesn't seem to be in graph anymore!" % self.new_edge_from.id
            return
        
        edge = self.umlworkspace.graph.AddEdge(self.new_edge_from, tonode, weight=None)
        # TODO should also arguably add to umlworkspace's associations_composition or associations_generalisation list (or create a new one for unlabelled associations like the one we are creating here)
        edge['uml_edge_type'] = ''
        #edge['uml_edge_type'] = 'composition'
        self.CreateUmlEdge(edge)
        self.stateofthenation()

    def ConvertParseModelToUmlModel(self, p):
        
        def BuildEdgeModel(association_tuples, edge_label):
            for fromClassname, toClassname in association_tuples:
                from_node = self.umlworkspace.AddUmlNode(fromClassname)
                to_node = self.umlworkspace.AddUmlNode(toClassname)
                edge = self.umlworkspace.graph.AddEdge(from_node, to_node)
                edge['uml_edge_type'] = edge_label
            
        def AddGeneralisation(classname, parentclass):
            if (classname, parentclass) in self.umlworkspace.associations_generalisation:
                #print "DUPLICATE Generalisation skipped when ConvertParseModelToUmlModel", (classname, parentclass) # DUPLICATE DETECTION
                return
            self.umlworkspace.associations_generalisation.append((classname, parentclass))

        def AddDependency(otherclass, classname):
            if (otherclass, classname) in self.umlworkspace.associations_composition:
                #print "DUPLICATE Dependency skipped when ConvertParseModelToUmlModel", (otherclass, classname) # DUPLICATE DETECTION
                return
            self.umlworkspace.associations_composition.append((otherclass, classname))  # reverse direction so round black arrows look ok

        for classname, classentry in p.classlist.items():
            """
            These are a list of (attr, otherclass) however they imply that THIS class
            owns all those other classes.
            """
            #print 'CLASS', classname, classentry
            
            # Composition / Dependencies
            for attr, otherclass in classentry.classdependencytuples:
                AddDependency(otherclass, classname)

            # Generalisations
            if classentry.classesinheritsfrom:
                for parentclass in classentry.classesinheritsfrom:

                    #if parentclass.find('.') <> -1:         # fix names like "unittest.TestCase" into "unittest"
                    #    parentclass = parentclass.split('.')[0] # take the lhs
                    AddGeneralisation(classname, parentclass)

            classAttrs = [ attrobj.attrname for attrobj in classentry.attrs ]
            classMeths = classentry.defs
            node = self.umlworkspace.AddUmlNode(classname, classAttrs, classMeths)

        # ensure no duplicate relationships exist
        assert len(set(self.umlworkspace.associations_composition)) == len(self.umlworkspace.associations_composition), self.umlworkspace.associations_composition        # ensure no duplicates exist
        assert len(set(self.umlworkspace.associations_generalisation)) == len(self.umlworkspace.associations_generalisation), self.umlworkspace.associations_generalisation        # ensure no duplicates exist

        BuildEdgeModel(self.umlworkspace.associations_generalisation, 'generalisation')
        BuildEdgeModel(self.umlworkspace.associations_composition, 'composition')
  
    def Go(self, files=None, path=None):

        # these are tuples between class names.
        self.umlworkspace.ClearAssociations()       # WHY DO WE WANT TO DESTROY THIS VALUABLE INFO?

        if files:
            for f in files:
                p = PySourceAsJava()
                p.optionModuleAsClass = 0
                p.verbose = 0
                p.Parse(f)
                self.ConvertParseModelToUmlModel(p)

        self.stage1()

        # Layout
        self.LayoutAndPositionShapes()
              
    def CreateImageShape(self, F):
        #shape = ogl.BitmapShape()
        shape = BitmapShapeResizable()
        img = wx.Image(F, wx.BITMAP_TYPE_ANY)
        
        #adjusted_img = img.AdjustChannels(factor_red = 1., factor_green = 1., factor_blue = 1., factor_alpha = 0.5)
        #adjusted_img = img.Rescale(10,10)
        adjusted_img = img
        
        bmp = wx.BitmapFromImage(adjusted_img)
        shape.SetBitmap(bmp)

        self.GetDiagram().AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler(self.log, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        setpos(shape, 0, 0)
        #setpos(shape, node.left, node.top)
        #node.width, node.height = shape.GetBoundingBoxMax()
        #node.shape = shape
        #shape.node = node
        return shape
        
    def CreateUmlShape(self, node):

        def newRegion(font, name, textLst, maxWidth, totHeight = 10):
            # Taken from Boa, but put into the canvas class instead of the scrolled window class.
            region = ogl.ShapeRegion()
            
            if len(textLst) == 0:
                return region, maxWidth, 0
                
            dc = wx.ClientDC(self)  # self is the canvas
            dc.SetFont(font)
    
            for text in textLst:
                w, h = dc.GetTextExtent(text)
                if w > maxWidth: maxWidth = w
                totHeight = totHeight + h + 0 # interline padding
    
            region.SetFont(font)
            region.SetText('\n'.join(textLst))
            region.SetName(name)
    
            return region, maxWidth, totHeight

        shape = DividedShape(width=99, height=98, canvas=self)
        maxWidth = 10 # min node width, grows as we update it with text widths
        
        """
        Future: Perhaps be able to show regions or not. Might need to totally
        reconstruct the shape.
        """
        #if not self.showAttributes: classAttrs = [' ']
        #if not self.showMethods: classMeths = [' ']

        # Create each region.  If height returned is 0 this means don't create this region.
        regionName, maxWidth, nameHeight = newRegion(self.font1, 'class_name', [node.classname], maxWidth)
        regionAttribs, maxWidth, attribsHeight = newRegion(self.font2, 'attributes', node.attrs, maxWidth)
        regionMeths, maxWidth, methsHeight = newRegion(self.font2, 'methods', node.meths, maxWidth)

        # Work out total height of shape
        totHeight = nameHeight + attribsHeight + methsHeight

        # Set regions to be a proportion of the total height of shape
        regionName.SetProportions(0.0, 1.0*(nameHeight/float(totHeight)))
        regionAttribs.SetProportions(0.0, 1.0*(attribsHeight/float(totHeight)))
        regionMeths.SetProportions(0.0, 1.0*(methsHeight/float(totHeight)))

        # Add regions to the shape
        shape.AddRegion(regionName)
        if attribsHeight:   # Dont' make a region unless we have to
            shape.AddRegion(regionAttribs)
        if methsHeight:     # Dont' make a region unless we have to
            shape.AddRegion(regionMeths)

        shape.SetSize(maxWidth + 10, totHeight + 10)
        shape.SetCentreResize(False)  # Specify whether the shape is to be resized from the centre (the centre stands still) or from the corner or side being dragged (the other corner or side stands still).

        regionName.SetFormatMode(ogl.FORMAT_CENTRE_HORIZ)
        shape.region1 = regionName  # Andy added, for later external reference to classname from just having the shape instance.
        
        shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetPen(wx.BLACK_PEN)   # Controls the color of the border of the shape
        shape.SetBrush(wx.Brush("WHEAT", wx.SOLID))
        setpos(shape, node.left, node.top)
        self.GetDiagram().AddShape(shape) # self.AddShape is ok too, ShapeCanvas's AddShape is delegated back to Diagram's AddShape.  ShapeCanvas-->Diagram
        shape.Show(True)

        evthandler = MyEvtHandler(self.log, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)
        
        shape.FlushText()

        # Don't set the node left,top here as the shape needs to conform to the node.
        # On the other hand the node needs to conform to the shape's width,height.
        # ACTUALLY I now do set the pos of the shape, see above,
        # just before the AddShape() call.
        #
        node.width, node.height = shape.GetBoundingBoxMax()
        node.shape = shape
        shape.node = node
        return shape

    def createNodeShape(self, node):     # FROM SPRING LAYOUT
        shape = ogl.RectangleShape( node.width, node.height )
        shape.AddText(node.id)
        setpos(shape, node.left, node.top)
        #shape.SetDraggable(True, True)
        self.AddShape( shape )
        node.shape = shape
        shape.node = node
        
        # wire in the event handler for the new shape
        evthandler = MyEvtHandler(None, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

    def createCommentShape(self, node):
        shape = ogl.TextShape( node.width, node.height )
            
        shape.SetCanvas(self)
        shape.SetPen(wx.BLACK_PEN)
        shape.SetBrush(wx.LIGHT_GREY_BRUSH)
        shape.SetBrush(wx.RED_BRUSH)
        for line in node.comment.split('\n'):
            shape.AddText(line)
        
        setpos(shape, node.left, node.top)
        #shape.SetDraggable(True, True)
        self.AddShape( shape )
        node.shape = shape
        shape.node = node
        
        # wire in the event handler for the new shape
        evthandler = MyEvtHandler(None, self.frame, self)  # just init the handler with whatever will be convenient for it to know.
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

    def CmdEditShape(self, shape):
        node = shape.node
         
        result, id, attrs, methods = self.DisplayDialogUmlNodeEdit(node.id, node.attrs, node.meths)
        if result:
            self.umlworkspace.graph.RenameNode(node, id)   # need special rename cos of underlying graph plumbing - perhaps put setter on id?
            node.attrs = attrs
            node.meths = methods
    
            self.CmdZapShape(shape, deleteNodeToo=False)
            
            shape = self.CreateUmlShape(node)
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
    
            # TODO Hmmm - how does new shape get hooked up if the line mapping uses old name!??  Cos of graph's edge info perhaps?
            for edge in self.umlworkspace.graph.edges:
                self.CreateUmlEdge(edge)
                
            node.shape.Show(True)
            self.stateofthenation()
        
    def CreateUmlEdge(self, edge):
        fromShape = edge['source'].shape
        toShape = edge['target'].shape
        
        edge_label = edge.get('uml_edge_type', '')
        if edge_label == 'generalisation':
            arrowtype = ogl.ARROW_ARROW
        elif edge_label == 'composition':
            arrowtype = ogl.ARROW_FILLED_CIRCLE
        else:
            arrowtype = None

        line = ogl.LineShape()
        line.SetCanvas(self)
        line.SetPen(wx.BLACK_PEN)
        line.SetBrush(wx.BLACK_BRUSH)
        if arrowtype:
            line.AddArrow(arrowtype)
        line.MakeLineControlPoints(2)

        fromShape.AddLine(line, toShape)
        self.GetDiagram().AddShape(line)
        line.Show(True)

    def OnWheelZoom(self, event):
        #print "OnWheelZoom"
        if self.working: return
        self.working = True

        if event.GetWheelRotation() < 0:
            self.cmdLayoutContract(event)
        else:
            self.cmdLayoutExpand(event)

        self.working = False

    def OnWheelZoom_OverlapRemoval_Defunct(self, event):
        if self.working: return
        self.working = True

        if event.GetWheelRotation() < 0:
            self.stage2()
            print self.overlap_remover.GetStats()
        else:
            self.stateofthenation()

        self.working = False
        
    def ChangeScale(self, delta, remap_world_to_layout=False, removeoverlaps=True):
        if remap_world_to_layout:
            self.AllToLayoutCoords()    # Experimental - only needed when you've done world coord changes 
        self.coordmapper.Recalibrate(scale=self.coordmapper.scale+delta)
        self.AllToWorldCoords()
        numoverlaps = self.overlap_remover.CountOverlaps()
        if removeoverlaps:
            self.stage2(force_stateofthenation=True, watch_removals=False) # does overlap removal and stateofthenation
        else:
            self.stateofthenation()
        
    def stage1(self, translatecoords=True):         # FROM SPRING LAYOUT
        if translatecoords:
            self.AllToWorldCoords()

        # Clear existing visualisation
        for node in self.umlworkspace.graph.nodes:
            if node.shape:
                self._ZapShape(node.shape)
                node.shape = None

        # Create fresh visualisation
        for node in self.umlworkspace.graph.nodes:
            assert not node.shape
            shape = self.CreateUmlShape(node)
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            
        for edge in self.umlworkspace.graph.edges:
            self.CreateUmlEdge(edge)

        self.Redraw222()

    def stage2(self, force_stateofthenation=False, watch_removals=True):
        ANIMATION = False
        
        #if ANIMATION:
        #    self.graph.SaveOldPositionsForAnimationPurposes()
        #    watch_removals = False  # added this when I turned animation on.
        
        self.overlap_remover.RemoveOverlaps(watch_removals=watch_removals)
        if self.overlap_remover.GetStats()['total_overlaps_found'] > 0 or force_stateofthenation:
            self.stateofthenation(animate=ANIMATION)

    def stateofthenation(self, animate=False):
        for node in self.umlworkspace.graph.nodes:
            self.AdjustShapePosition(node)
        self.Redraw222()
        wx.SafeYield()

    def stateofthespring(self):
        self.coordmapper.Recalibrate()
        self.AllToWorldCoords()
        self.stateofthenation() # DON'T do overlap removal or it will get mad!
                
    def RedrawEverything(self):
        diagram = self.GetDiagram()
        canvas = self
        assert self == canvas == diagram.GetCanvas()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        for shape in self.umlboxshapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
            if shape.__class__.__name__ == 'DividedShape':
                shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)

        """
        Do we need any of this?  YES.
        Annoying to have a hack, esp if it keeps forcing calls to Recalibrate()
        But we need it so that the Recalibrate() is called at least once
        """
        #self.frame.SetScrollbars(needs lots of weird args...)
        # or
        #self.SetScrollbars(needs lots of weird args...)
        #
        # Hack To Force The Scrollbar To Show Up
        # Set the window size to something different
        # Return the size to what it was
        #
        oldSize = self.frame.GetSize()
        self.frame.SetSize((oldSize[0]+1,oldSize[1]+1))
        self.frame.SetSize(oldSize)

    def CmdLayout(self):
        #print
        #print "CmdLayout"
        #print
        if self.GetDiagram().GetCount() == 0:
            #self.frame.MessageBox("Nothing to layout.  Import a python source file first.")
            return
        
        self.LayoutAndPositionShapes()
        self.RedrawEverything()

    def CmdDeepLayout_OFFLINE(self):
        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        wx.SafeYield()
        try:
            b = LayoutBlackboard(graph=self.umlworkspace.graph, controller=self)
            b.LayoutMultipleChooseBest(4)
        finally:
            wx.EndBusyCursor()

    def CmdDeepLayout(self):
        from blackboard_thread import MainBlackboardFrame
        """Init Main App."""
        f = MainBlackboardFrame(parent=self.frame, id=-1)
        f.Show(True)
        
        b = LayoutBlackboard(graph=self.umlworkspace.graph, controller=self)
        f.SetBlackboardObject(b)
        print "CmdDeepLayout end"

    def ReLayout(self, keep_current_positions=False, gui=None, optimise=True):
        self.AllToLayoutCoords()
        self.layouter.layout(keep_current_positions, optimise=optimise)
        self.AllToWorldCoords()
        self.stage2() # does overlap removal and stateofthenation
    
    def LayoutAndPositionShapes(self):
        self.ReLayout()
        return
    
        positions, shapeslist, newdiagramsize = self.layout.Layout(self.umlworkspace, self.umlboxshapes)
        print "Layout positions", positions
        
        self.setSize(newdiagramsize)

        dc = wx.ClientDC(self)
        self.PrepareDC(dc)

        # Now move the shapes into place.
        for (pos, classShape) in zip(positions, shapeslist):
            #print pos, classShape.region1.GetText()
            x, y = pos

            # compensate for the fact that x, y for a ogl shape are the centre of the shape, not the top left
            width, height = classShape.GetBoundingBoxMax()
            x += width/2
            y += height/2

            classShape.Move(dc, x, y, False)

        #self.umlworkspace.Dump()
        
        
    def setSize(self, size):
        size = wx.Size(size[0], size[1])
        
        nvsx, nvsy = size.x / self.scrollStepX, size.y / self.scrollStepY
        self.Scroll(0, 0)
        self.SetScrollbars(self.scrollStepX, self.scrollStepY, nvsx, nvsy)
        canvas = self
        canvas.SetSize(canvas.GetVirtualSize())


    def AdjustShapePosition(self, node, point=None):   # FROM SPRING LAYOUT
        assert node.shape
        
        if point:
            x, y = point
        else:
            x, y = node.left, node.top
            
        # Don't need to use node.shape.Move(dc, x, y, False)
        setpos(node.shape, x, y)

        # But you DO need to use a dc to adjust the links
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)
        node.shape.MoveLinks(dc)
        
    def Redraw222(self, clear=True):        # FROM SPRING LAYOUT
        diagram = self.GetDiagram()
        canvas = self
        assert canvas == diagram.GetCanvas()
    
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        
        #for node in self.graph.nodes:    # TODO am still moving nodes in the pynsourcegui version?
        #    shape = node.shape
        #    shape.Move(dc, shape.GetX(), shape.GetY())
        
        if clear:
            diagram.Clear(dc)
        diagram.Redraw(dc)
        
    def get_umlboxshapes(self):
        return [s for s in self.GetDiagram().GetShapeList() if isinstance(s, DividedShape)]

    umlboxshapes = property(get_umlboxshapes)
    
    def OnDestroy(self, evt):
        for shape in self.GetDiagram().GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)

    def OnLeftClick(self, x, y, keys):  # Override of ShapeCanvas method
        # keys is a bit list of the following: KEY_SHIFT  KEY_CTRL
        self.DeselectAllShapes()

    def DeselectAllShapes(self):
        selected = [s for s in self.GetDiagram().GetShapeList() if s.Selected()]
        if selected:
            assert len(selected) == 1
            s = selected[0]
            canvas = s.GetCanvas()
            
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            s.Select(False, dc)
            canvas.Refresh(False)   # Need this or else Control points ('handles') leave blank holes
       

class Log:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)
    write = WriteText

from gui_imageviewer import ImageViewer

USE_SIZER = False

class MainApp(wx.App):
    def OnInit(self):
        self.log = Log()
        self.working = False
        wx.InitAllImageHandlers()
        self.andyapptitle = 'PyNsource GUI - Python Code into UML'

        self.frame = Frame(None, -1, self.andyapptitle, pos=(50,50), size=(0,0),
                        style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.DEFAULT_FRAME_STYLE)
        self.frame.CreateStatusBar()
        self.InitMenus()

        if MULTI_TAB_GUI:
            self.notebook = wx.Notebook(self.frame, -1)
         
            if USE_SIZER:
                # create the chain of real objects
                panel = wx.Panel(self.notebook, -1)
                self.umlwin = UmlShapeCanvas(panel, Log(), self.frame)
                # add children to sizers and set the sizer to the parent
                sizer = wx.BoxSizer( wx.VERTICAL )
                sizer.Add(self.umlwin, 1, wx.GROW)
                panel.SetSizer(sizer)
            else:
                self.umlwin = UmlShapeCanvas(self.notebook, Log(), self.frame)

            #self.yuml = ImageViewer(self.notebook) # wx.Panel(self.notebook, -1)
            
            self.asciiart = wx.Panel(self.notebook, -1)
    
            if USE_SIZER:
                self.notebook.AddPage(panel, "UML")
            else:
                self.notebook.AddPage(self.umlwin, "UML")
            #self.notebook.AddPage(self.yuml, "yUml")
            self.notebook.AddPage(self.asciiart, "Ascii Art")
    
            # Modify my own page http://www.andypatterns.com/index.php/products/pynsource/asciiart/
            # Some other ideas here http://c2.com/cgi/wiki?UmlAsciiArt 
            self.multiText = wx.TextCtrl(self.asciiart, -1, ASCII_UML_HELP_MSG, style=wx.TE_MULTILINE|wx.HSCROLL)
            bsizer = wx.BoxSizer()
            bsizer.Add(self.multiText, 1, wx.EXPAND)
            self.asciiart.SetSizerAndFit(bsizer)
            self.multiText.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False))   # see http://www.wxpython.org/docs/api/wx.Font-class.html for more fonts
            self.multiText.Bind( wx.EVT_CHAR, self.onKeyChar_Ascii_Text_window)
            self.multiText.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom_ascii)

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
        
        self.popupmenu = None
        self.umlwin.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonMenu)  # WARNING: takes over all righclick events - need to event.skip() to let through things to MyEvtHandler 
        self.Bind(wx.EVT_SIZE, self.OnResizeFrame)

        #self.umlwin.Bind(wx.EVT_SET_FOCUS, self.onFocus)  # attempt at making mousewheel auto scroll the workspace
        #self.frame.Bind(wx.EVT_SET_FOCUS, self.onFocus)   # attempt at making mousewheel auto scroll the workspace
        
        self.InitConfig()

        wx.CallAfter(self.BootStrap)    # doesn't make a difference calling this via CallAfter
        
        return True
    
    def BootStrap(self):

        def bootstrap01():
            self.frame.SetSize((1024,768))
            self.umlwin.Go(files=[os.path.abspath( __file__ )])
        def bootstrap02():
            self.umlwin.Go(files=[os.path.abspath( "../Research/state chart editor/Editor.py" )])
            self.umlwin.RedrawEverything()
            #self.umlwin.umlworkspace.Dump()
        def bootstrap03():
            self.umlwin.RedrawEverything()  # Allow main frame to resize and thus allow world coords to calibrate before we generate layout coords for loaded graph
            filename = os.path.abspath( "saved uml workspaces/uml05.txt" )
            fp = open(filename, "r")
            s = fp.read()
            fp.close()
            self.LoadGraph(s)
        def bootstrap04():
            self.umlwin.Go(files=[os.path.abspath( "pyNsourceGui.py" )])
            self.umlwin.RedrawEverything()
        def bootstrap05():
            self.umlwin.Go(files=[os.path.abspath("printframework.py"), os.path.abspath("png.py")])
            self.umlwin.RedrawEverything()
        def bootstrap06():
            self.umlwin.Go(files=[os.path.abspath("gui_umlshapes.py")])
            self.umlwin.RedrawEverything()
            
        #print "BootStrap"
        bootstrap03()
        
    #def onFocus(self, event):   # attempt at making mousewheel auto scroll the workspace
    #    self.umlwin.SetFocus()  # attempt at making mousewheel auto scroll the workspace
        
    def InitConfig(self):
        config_dir = os.path.join(wx.StandardPaths.Get().GetUserConfigDir(), PYNSOURCE_CONFIG_DIR)
        try:
            os.makedirs(config_dir)
        except OSError:
            pass        
        self.user_config_file = os.path.join(config_dir, PYNSOURCE_CONFIG_FILE)
        #print "Pynsource config file", self.user_config_file
        
        from configobj import ConfigObj # easy_install configobj
        self.config = ConfigObj(self.user_config_file) # doco at http://www.voidspace.org.uk/python/configobj.html
        #print self.config
        self.config['keyword1'] = 100
        self.config['keyword2'] = "hi there"
        self.config.write()

    def OnResizeFrame (self, event):   # ANDY  interesting - GetVirtualSize grows when resize frame
        if event.EventObject == self.umlwin:
            #print "OnResizeFrame"
            self.umlwin.coordmapper.Recalibrate(self.frame.GetClientSize()) # may need to call self.GetVirtualSize() if scrolled window
            #self.umlwin.coordmapper.Recalibrate(self.umlwin.GetVirtualSize())
        event.Skip()
        
    def OnRightButtonMenu(self, event):   # Menu
        x, y = event.GetPosition()

        # Since our binding of wx.EVT_RIGHT_DOWN to here takes over all right click events
        # we have to manually figure out if we have clicked on shape 
        # then allow natural shape node menu to kick in via MyEvtHandler (defined above)
        hit_which_shapes = [s for s in self.umlwin.GetDiagram().GetShapeList() if s.HitTest(x,y)]
        if hit_which_shapes:
            event.Skip()
            return
        
        if self.popupmenu:
            self.popupmenu.Destroy()    # wx.Menu objects need to be explicitly destroyed (e.g. menu.Destroy()) in this situation. Otherwise, they will rack up the USER Objects count on Windows; eventually crashing a program when USER Objects is maxed out. -- U. Artie Eoff  http://wiki.wxpython.org/index.cgi/PopupMenuOnRightClick
        self.popupmenu = wx.Menu()     # Create a menu
        
        item = self.popupmenu.Append(wx.NewId(), "Insert Class...")
        self.frame.Bind(wx.EVT_MENU, self.OnInsertClass, item)
        item = self.popupmenu.Append(wx.NewId(), "Insert Image...")
        self.frame.Bind(wx.EVT_MENU, self.OnInsertImage, item)
        item = self.popupmenu.Append(wx.NewId(), "Insert Comment...")
        self.frame.Bind(wx.EVT_MENU, self.OnInsertComment, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.NewId(), "Load Graph from text...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoadGraphFromText, item)
        
        item = self.popupmenu.Append(wx.NewId(), "Dump Graph to console")
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGraphToConsole, item)
        
        self.popupmenu.AppendSeparator()
        
        item = self.popupmenu.Append(wx.NewId(), "Load Graph...")
        self.frame.Bind(wx.EVT_MENU, self.OnLoadGraph, item)
        
        item = self.popupmenu.Append(wx.NewId(), "Save Graph...")
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGraph, item)
        
        self.popupmenu.AppendSeparator()
        
        item = self.popupmenu.Append(wx.NewId(), "DumpUmlWorkspace")
        self.frame.Bind(wx.EVT_MENU, self.OnDumpUmlWorkspace, item)
        
        self.frame.PopupMenu(self.popupmenu, wx.Point(x,y))
        
    def OnWheelZoom_ascii(self, event):
        # Since our binding of wx.EVT_MOUSEWHEEL to here takes over all wheel events
        # we have to manually do the normal test scrolling.  This event can't propogate via event.skip()
        #
        #The native widgets handle the low level 
        #events (or not) their own way and wx makes no guarantees about behaviors 
        #when intercepting them yourself. 
        #-- 
        #Robin Dunn 

        if self.working: return
        self.working = True
        
        #print event.ShouldPropagate(), dir(event)
        
        controlDown = event.CmdDown()
        if controlDown:
            font = self.multiText.GetFont()
    
            if event.GetWheelRotation() < 0:
                newfontsize = font.GetPointSize() - 1
            else:
                newfontsize = font.GetPointSize() + 1
    
            if newfontsize > 0 and newfontsize < 100:
                self.multiText.SetFont(wx.Font(newfontsize, wx.MODERN, wx.NORMAL, wx.NORMAL, False))
        else:
            if event.GetWheelRotation() < 0:
                self.multiText.ScrollLines(4)
            else:
                self.multiText.ScrollLines(-4)

        self.working = False

        #self.frame.GetEventHandler().ProcessEvent(event)
        #wx.PostEvent(self.frame, event)
        
    def onKeyChar_Ascii_Text_window(self, event):
        # See good tutorial http://www.blog.pythonlibrary.org/2009/08/29/wxpython-catching-key-and-char-events/
        keycode = event.GetKeyCode()
        controlDown = event.CmdDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        #print keycode
        
        if controlDown and keycode == 1:    # CTRL-A
            self.multiText.SelectAll()

        event.Skip()

    def OnDumpUmlWorkspace(self, event):
        self.umlwin.DumpStatus()

    def OnSaveGraphToConsole(self, event):
        print self.umlwin.umlworkspace.graph.GraphToString()

    def OnSaveGraph(self, event):
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.\\saved uml workspaces',
            defaultFile="", wildcard="*.txt", style=wx.FD_SAVE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            
            fp = open(filename, "w")
            fp.write(self.umlwin.umlworkspace.graph.GraphToString())
            fp.close()
        dlg.Destroy()
        
    def OnLoadGraphFromText(self, event):
        eg = "{'type':'node', 'id':'A', 'x':142, 'y':129, 'width':250, 'height':250}"
        dialog = wx.TextEntryDialog (parent=self.frame, message='Enter node/edge persistence strings:', caption='Load Graph From Text', defaultValue=eg, style=wx.OK|wx.CANCEL|wx.TE_MULTILINE )
        if dialog.ShowModal() == wx.ID_OK:
            txt = dialog.GetValue()
            print txt
            self.LoadGraph(txt)
        dialog.Destroy()
            
    def OnLoadGraph(self, event):
        thisdir = self.config.get('LastDirFileOpen', '.\\saved uml workspaces') # remember dir path
        
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir=thisdir,
            defaultFile="", wildcard="*.txt", style=wx.OPEN, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            self.config['LastDirFileOpen'] = dlg.GetDirectory()  # remember dir path
            self.config.write()

            fp = open(filename, "r")
            s = fp.read()
            fp.close()

            self.LoadGraph(s)
        dlg.Destroy()

    def LoadGraph(self, filedata=""):
        self.umlwin.Clear()
        
        self.umlwin.umlworkspace.graph.LoadGraphFromStrings(filedata)
                
        # build view from model
        self.umlwin.stage1(translatecoords=False)

        # set layout coords to be in sync with world, so that if expand scale things will work
        self.umlwin.coordmapper.Recalibrate()
        self.umlwin.AllToLayoutCoords()
        
        # refresh view
        self.umlwin.GetDiagram().ShowAll(1) # need this, yes
        self.umlwin.stateofthenation()
        
        self.RefreshAsciiUmlTab()

        
    def OnTabPageChanged(self, event):
        if event.GetSelection() == 0:  # ogl
            self.Bind(wx.EVT_MOUSEWHEEL, self.umlwin.OnWheelZoom)  # rebind as it seems to get unbound when switch to ascii tab
            wx.CallAfter(self.umlwin.SetFocus)
            self.menuBar.EnableTop(2, True)  # enable layout menu

        #elif event.GetSelection() == 1:  # yuml
        #    #self.yuml.ViewImage(thefile='../outyuml.png')
        #    pass

        elif event.GetSelection() == 1:  # ascii art
            self.RefreshAsciiUmlTab()
            self.menuBar.EnableTop(2, False)  # disable layout menu
            wx.CallAfter(self.multiText.SetFocus)
            wx.CallAfter(self.multiText.SetInsertionPoint, 0) 
         
        event.Skip()
        
    def RefreshAsciiUmlTab(self):
        self.model_to_ascii()
        
    def InitMenus(self):
        menuBar = wx.MenuBar(); self.menuBar = menuBar
        menu1 = wx.Menu()
        menu2 = wx.Menu()
        menu3 = wx.Menu()
        menu3sub = wx.Menu()
        menu4 = wx.Menu()

        self.next_menu_id = wx.NewId()
        def Add(menu, s1, s2, func, func_update=None):
            menu_item = menu.Append(self.next_menu_id, s1, s2)
            wx.EVT_MENU(self, self.next_menu_id, func)
            if func_update:
                wx.EVT_UPDATE_UI(self, self.next_menu_id, func_update)
            self.next_menu_id = wx.NewId()
            return menu_item

        def AddSubMenu(menu, submenu, s):
            menu.AppendMenu(self.next_menu_id, s, submenu)
            self.next_menu_id = wx.NewId()

        Add(menu1, "&New\tCtrl-N", "New Diagram", self.FileNew)
        Add(menu1, "&Open...\tCtrl-O", "Load UML Diagram...", self.OnLoadGraph)
        Add(menu1, "&Save As...\tCtrl-S", "Save UML Diagram...", self.OnSaveGraph)
        menu1.AppendSeparator()
        Add(menu1, "&Import Python Code...\tCtrl-I", "Import Python Source Files", self.FileImport)
        #Add(menu1, "File &Import yUml...\tCtrl-Y", "Import Python Source Files", self.FileImport2)
        #Add(menu1, "&Import Ascii Art...\tCtrl-J", "Import Python Source Files", self.FileImport3)
        menu1.AppendSeparator()
        Add(menu1, "&Print / Preview...\tCtrl-P", "Print", self.FilePrint)
        menu1.AppendSeparator()
        Add(menu1, "E&xit\tAlt-X", "Exit demo", self.OnButton)
        
        Add(menu2, "&Insert Class...\tIns", "Insert Class...", self.OnInsertClass)
        Add(menu2, "&Insert Image...\tCtrl-Ins", "Insert Image...", self.OnInsertImage)
        Add(menu2, "&Insert Comment...\tShift-Ins", "Insert Comment...", self.OnInsertComment)
        menu_item_delete_class = Add(menu2, "&Delete\tDel", "Delete", self.OnDeleteNode, self.OnDeleteNode_update)
        menu_item_delete_class.Enable(True)  # demo one way to enable/disable.  But better to do via _update function
        Add(menu2, "&Edit Class Properties...\tF2", "Edit Class Properties", self.OnEditProperties, self.OnEditProperties_update)
        menu2.AppendSeparator()
        Add(menu2, "&Refresh", "Refresh", self.OnRefreshUmlWindow)
        
        Add(menu3, "&Layout UML\tL", "Layout UML", self.OnLayout)
        Add(menu3, "&Layout UML Optimally (slower)\tB", "Deep Layout UML (slow)", self.OnDeepLayout)
        menu3.AppendSeparator()
        Add(menu3sub, "&Remember Layout into memory slot 1\tShift-9", "Remember Layout 1", self.OnRememberLayout1)
        Add(menu3sub, "&Restore Layout 1\t9", "Restore Layout 1", self.OnRestoreLayout1)
        menu3sub.AppendSeparator()
        Add(menu3sub, "&Remember Layout into memory slot 2\tShift-0", "Remember Layout 2", self.OnRememberLayout2)
        Add(menu3sub, "&Restore Layout 2\t0", "Restore Layout 2", self.OnRestoreLayout2)
        AddSubMenu(menu3, menu3sub, "Snapshots")
        #menu3.AppendSeparator()
        #Add(menu3, "&Expand Layout\t->", "Expand Layout", self.OnExpandLayout)
        menu3.AppendSeparator()
        
        
        Add(menu4, "&Help...\tF1", "Help", self.OnHelp)
        Add(menu4, "&Visit PyNSource Website...", "PyNSource Website", self.OnVisitWebsite)
        Add(menu4, "&Check for Updates...", "Check for Updates", self.OnCheckForUpdates)
        menu4.AppendSeparator()
        Add(menu4, "&About...", "About...", self.OnAbout)

        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&Edit")
        menuBar.Append(menu3, "&Layout")
        menuBar.Append(menu4, "&Help")
        self.frame.SetMenuBar(menuBar)
        
    def OnRememberLayout1(self, event):
        self.umlwin.CmdRememberLayout1()
    def OnRememberLayout2(self, event):
        self.umlwin.CmdRememberLayout2()
    def OnRestoreLayout1(self, event):
        self.umlwin.CmdRestoreLayout1()
    def OnRestoreLayout2(self, event):
        self.umlwin.CmdRestoreLayout2()
        
    def FileImport(self, event):
        self.notebook.SetSelection(0)
        
        thisdir = self.config.get('LastDirFileImport', os.getcwd()) # remember dir path
        
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir=thisdir,
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            
            self.config['LastDirFileImport'] = dlg.GetDirectory()  # remember dir path
            self.config.write()
            
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            self.umlwin.Go(files=filenames)
            self.umlwin.RedrawEverything()
            wx.EndBusyCursor()
            print 'Import - Done.'

    #def FileImport2(self, event):
    #    from generate_code.gen_yuml import PySourceAsYuml
    #    import urllib
    #    
    #    self.notebook.SetSelection(1)
    #    dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
    #        defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
    #    if dlg.ShowModal() == wx.ID_OK:
    #        filenames = dlg.GetPaths()
    #        print 'Importing...'
    #        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
    #        print filenames
    #        
    #        files=filenames
    #        p = PySourceAsYuml()
    #        p.optionModuleAsClass = 0
    #        p.verbose = 0
    #        if files:
    #            for f in files:
    #                p.Parse(f)
    #        p.CalcYumls()
    #        print p
    #
    #        #yuml_txt = "[Customer]+1->*[Order],[Order]++1-items >*[LineItem],[Order]-0..1>[PaymentMethod]"
    #        yuml_txt = ','.join(str(p).split())
    #        baseUrl = 'http://yuml.me/diagram/dir:lr;scruffy/class/'
    #        url = baseUrl + urllib.quote(yuml_txt)
    #        self.yuml.ViewImage(url=url)
    #
    #        wx.EndBusyCursor()
    #        print 'Import - Done.'
    #
    #def FileImport3(self, event):
    #    from generate_code.gen_asciiart import PySourceAsText
    #    import urllib
    #    
    #    self.notebook.SetSelection(2)
    #    dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir='.',
    #        defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
    #    if dlg.ShowModal() == wx.ID_OK:
    #        filenames = dlg.GetPaths()
    #        print 'Importing...'
    #        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
    #        print filenames
    #        
    #        files=filenames
    #        p = PySourceAsText()
    #        p.optionModuleAsClass = 0
    #        p.verbose = 0
    #        if files:
    #            for f in files:
    #                p.Parse(f)
    #        print p
    #
    #        self.multiText.SetValue(str(p))
    #        self.multiText.ShowPosition(0)
    #
    #        wx.EndBusyCursor()
    #        print 'Import - Done.'


    def model_to_ascii(self):
        from layout.layout_ascii import model_to_ascii_builder
        import time
        
        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        m = model_to_ascii_builder()
        try:
            wx.SafeYield()
            #time.sleep(0.2)
            s = m.main(self.umlwin.umlworkspace.graph)
            #self.notebook.SetSelection(2)            
            self.multiText.SetValue(str(s))
            if str(s).strip() == "":
                self.multiText.SetValue(ASCII_UML_HELP_MSG)
            self.multiText.ShowPosition(0)
        finally:
            wx.EndBusyCursor()
            
    def FileNew(self, event):
        self.umlwin.Clear()
        self.RefreshAsciiUmlTab()
        
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
        #self.MessageBox(ABOUT_MSG.strip() %  APP_VERSION)
        
        from wx.lib.wordwrap import wordwrap
        info = wx.AboutDialogInfo()
        #info.SetIcon(wx.Icon('Images\\img_uml01.png', wx.BITMAP_TYPE_PNG))
        info.SetName(ABOUT_APPNAME)
        info.SetVersion(str(APP_VERSION))
        info.SetDescription(ABOUT_MSG)
        #info.Description = wordwrap(ABOUT_MSG, 350, wx.ClientDC(self.frame))
        info.SetCopyright(ABOUT_AUTHOR)
        #info.SetWebSite(WEB_PYNSOURCE_HOME_URL)
        info.WebSite = (WEB_PYNSOURCE_HOME_URL, "Home Page")
        info.SetLicence(ABOUT_LICENSE)
        #info.AddDeveloper(ABOUT_AUTHOR)
        #info.AddDocWriter(ABOUT_FEATURES)
        #info.AddArtist('Blah')
        #info.AddTranslator('Blah')

        wx.AboutBox(info)

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

    def Enable_if_node_selected(self, event):
        selected = [s for s in self.umlwin.GetDiagram().GetShapeList() if s.Selected()]
        viewing_uml_tab = self.notebook.GetSelection() == 0
        event.Enable(len(selected) > 0 and viewing_uml_tab)

    def OnDeleteNode(self, event):
        for shape in self.umlwin.GetDiagram().GetShapeList():
            if shape.Selected():
                self.umlwin.CmdZapShape(shape)
    def OnDeleteNode_update(self, event):
        self.Enable_if_node_selected(event)

    def OnInsertComment(self, event):
        self.umlwin.CmdInsertNewComment()

    def OnInsertImage(self, event):
        filename = None
        
        thisdir = self.config.get('LastDirInsertImage', '.') # remember dir path
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir=thisdir,
            defaultFile="", wildcard="*.jpg", style=wx.OPEN, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            self.config['LastDirInsertImage'] = dlg.GetDirectory()  # remember dir path
            self.config.write()
        dlg.Destroy()
        
        self.umlwin.CmdInsertNewImageNode(filename)
                
    def OnInsertClass(self, event):
        self.umlwin.CmdInsertNewNode()
        self.RefreshAsciiUmlTab()
        
    def OnEditProperties(self, event):
        for shape in self.umlwin.GetDiagram().GetShapeList():
            if shape.Selected():
                self.umlwin.CmdEditShape(shape)
                break
    def OnEditProperties_update(self, event):
        self.Enable_if_node_selected(event)

    def OnLayout(self, event):
        self.umlwin.CmdLayout()

    def OnDeepLayout(self, event):
        self.umlwin.CmdDeepLayout()


    def OnRefreshUmlWindow(self, event):
        self.umlwin.RedrawEverything()
        self.RefreshAsciiUmlTab()

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


