##########################################
# OGLlike - OGL like library for wxPython 
#
# Phoenix compatibility and various improvements Andy Bulka 2018.
# Copyright (C) 2003-2004  Erik R. Lechak
# Feel free to use it, modify it, distribute it.  All I ask is:
#   1)  If you improve it, please send me a copy of the improved version.  
#   2)  Please don't try to take credit for my work.
##########################################

import wx #ANDY
# from wxPython.wx import *
from wx import *
import pickle
import os
import sys
import copy
import random

#Global Stuff   -------------------------------------------------------------------------
clipboard=[]

#ANDY
# ANDYMAIN = None
DEBUG_DRAG = False
DEBUG_DRAWLINE = False
DEBUG_CONNECT = False
DEBUG_INODE_CONNECT = False
##############

def menuMaker(frame, menus):
    menubar = MenuBar()
    for m,n in list(menus.items()):
        menu = Menu()
        menubar.Append(menu,m)
        for x in n:
            menu_text, help, handler = x[0], x[1], x[2]
            id = NewId()
            menu.Append(id, menu_text, help)
            frame.Bind(EVT_MENU, handler, id=id)
            # EVT_MENU(frame, id,  handler)  # old deprecated way
    frame.SetMenuBar(menubar)

#------------------------------------------------------------------------------------------


class Diagram:
    def __init__(self):
        self.shapes=[]
        
    def SaveFile(self,file=None):
        if file is None:
            return
        try:
            pickle.dump(self.shapes,open(self.file,'w'))
        except:
            print("problem saving this diagram")
 
    def LoadFile(self,file=None):
        if file is None:
            return
        try:
            self.shapes = pickle.load(open(file))
        except:
            print("problem loading this diagram")

    def AddShape(self, shape, after=None):
        if after:
            self.shapes.insert(self.shapes.index(after),shape)
        else:
            self.shapes.insert(0, shape)
            
    def AppendShape(self, shape):
        self.shapes.append(shape)
        
    def InsertShape(self, shape, index=0):
        self.shapes.insert(index, shape)
    
    def DeleteShape(self,shape):
        self.shapes.remove(shape)
    
    def PopShape(self,index=-1):
        return self.shapes.pop(index)

    def DeleteAllShapes(self):
        del self.shapes[:]

    def ChangeShapeOrder(self, shape, pos=0):
        self.shapes.remove(shape)
        self.shapes.insert(pos,shape)

    def GetCount(self):
        return len(self.shapes)
        
    def GetShapeList(self):
        return self.shapes



# Generic Shape Event Handler -------------------------------------------------------------------------------
class ShapeEvtHandler:

    def OnLeftUp(self,event):
        pass
        
    def OnLeftDown(self,event):
        pass
        
    def OnLeftDClick(self,event):
        pass

    def OnRightUp(self,event):
        pass
        
    def OnRightDown(self,event):
        pass
        
    def OnRightDClick(self,event):
        pass

    def OnSelect(self,event):
        pass
        
    def OnDeselect(self,event):
        pass
        
    def OnMove(self,event):
        pass
        
    def OnResize(self,event):
        pass
        
    def OnConnect(self,event):
        pass



# Generic Graphic items ---------------------------------------------------------------------------------------
class Shape(ShapeEvtHandler):
    def __init__(self, x=[], y=[]):
        self.x = x                         # list of x coord
        self.y = y                        # list of y coords        
        self.pen = ['BLACK' , 1]    # pen color and size
        self.fill= ['WHITE']            # fill color

    def draw(self,dc):
        dc.SetPen(Pen(self.pen[0], self.pen[1], SOLID))
        dc.SetBrush(Brush(self.fill[0], SOLID))

    def move(self,x,y):
        self.x = list(map((lambda v: v+x), self.x))
        self.y = list(map((lambda v: v+y), self.y))

    def Copy(self):
        return copy.deepcopy(self)


class LineShape(Shape):
    def __init__(self,x1=20, y1=20, x2=50, y2=50):
        Shape.__init__(self, [x1,x2] ,  [y1,y2])

    def draw(self,dc):
        Shape.draw(self,dc)
        dc.DrawLine(self.x[0], self.y[0],self.x[1], self.y[1])
        if DEBUG_DRAWLINE:
            print("DrawLine", self.x[0], self.y[0],self.x[1], self.y[1])

    def HitTest(self, x, y):
        if x < min(self.x)-3:return False
        if x > max(self.x)+3:return False
        if y < min(self.y)-3:return False
        if y > max(self.y)+3:return False
            
        top= (x-self.x[0]) *(self.x[1] - self.x[0]) + (y-self.y[0])*(self.y[1]-self.y[0])
        distsqr=pow(self.x[0]-self.x[1],2)+pow(self.y[0]-self.y[1],2)
        u=float(top)/float(distsqr)
        
        newx = self.x[0] + u*(self.x[1]-self.x[0])
        newy = self.y[0] + u*(self.y[1]-self.y[0])
       
        dist=pow(pow(newx-x,2) +  pow(newy-y,2),.5)

        if dist>7: return False
        return True

class RectangleShape(Shape):
    def __init__(self,x=20, y=20, x2=90, y2=90):
        
        #ANDY
        # if False and ANDYMAIN:
        #     # print "ANDYMAIN is set within %s %s %s" % (type(self), self.x, self.y)
        #     print "ANDYMAIN is set within %s %s" % (type(self), self)
        #     topx,topy = ANDYMAIN.canvas.GetViewStart() # The positions are in logical scroll units, not pixels, so to convert to pixels you will have to multiply by the number of pixels per scroll increment.
        #     # print topx,topy
        #     px,py = ANDYMAIN.canvas.GetScrollPixelsPerUnit()
        #     print "topx", topx, "topy", topy, px, py, topx*px, topy*py
        #     topx,topy = ANDYMAIN.canvas.CalcUnscrolledPosition(topx*px,topy*py)
        #     print topx,topy
        #     Shape.__init__(self, [topx+x,topx+x2] ,  [topy+y,topy+y2])
        # else:
        #     Shape.__init__(self, [x,x2] ,  [y,y2])
        ######
        
        #ANDY
        Shape.__init__(self, [x,x2] ,  [y,y2])

    def draw(self,dc):
        Shape.draw(self,dc)
        dc.DrawRectangle(int(self.x[0]), int(self.y[0]),int(self.x[1]-self.x[0]), int(self.y[1]-self.y[0]))
        
    def HitTest(self, x, y):
        if x < self.x[0]: return False
        if x > self.x[1]: return False
        if y < self.y[0]: return False
        if y > self.y[1]: return False
        return True

class PointShape(Shape):
    def __init__(self,x=20,y=20,size=4,type='rect'):
        Shape.__init__(self, [x] , [y])
        self.type=type
        self.size=size
        if self.type=='rect':
            self.graphic = RectangleShape(x-size,y-size,x+size,y+size)
        self.graphic.pen = self.pen
        self.graphic.fill = self.fill

    def moveto(self,x,y):
        self.x = x
        self.y = y
        size = self.size
        self.graphic.x=[x-size,x+size]
        self.graphic.y=[y-size,y+size]

    def move(self,x,y):
        # self.x and self.y are lists of x coords and y coords
        # in the case of default PointShape that list only has one member
        if self.x == 1:
            # Simpler to understand code
            self.x[0] += x
            self.y[0] += y
        else:
            # Future possibility (original code)
            self.x = list(map((lambda v: v+x), self.x))   # add x to each member of list self.x
            self.y = list(map((lambda v: v+y), self.y))   # add y to each member of list self.y
        self.graphic.move(x,y)

    def HitTest(self, x, y):
        return self.graphic.HitTest(x,y)

    def draw(self,dc):
        self.graphic.pen = self.pen
        self.graphic.fill = self.fill
        self.graphic.draw(dc)
#---------------------------------------------------------------------------------------------------------------



class ShapeCanvas(ScrolledWindow):
    def __init__(self,
        parent,
        id=-1,
        pos=(-1,-1),
        size=(-1,-1),
        style=0,
        name="",
        ):
        ScrolledWindow.__init__(self,parent,id,pos,size,style,name)
        self.diagram=None
        self.nodes=[]
        self.currentPoint = [0,0] # x and y of last mouse click or mouse drag
        self.selectedShapes=[]
        self.scalex =1.0
        self.scaley =1.0

        #Window Events        
        self.Bind(EVT_PAINT, self.onPaintEvent)  # was EVT_PAINT(self, self.onPaintEvent)
        #Mouse Events
        self.Bind(EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(EVT_LEFT_DCLICK, self.OnLeftDClick)
        
        self.Bind(EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(EVT_RIGHT_DCLICK, self.OnRightDClick)
        
        self.Bind(EVT_MOTION, self.OnMotion)
        #Key Events
        self.Bind(EVT_KEY_DOWN,self.keyPress)

    def AddShape(self, shape, after=None):
        self.diagram.AddShape(shape,after)
            
    def AppendShape(self, shape):
        self.diagram.AppendShape(shape)
        
    def InsertShape(self, shape, index=0):
        self.diagram.InsertShape(shape,index)

    def DeleteShape(self,shape):
        self.diagram.DeleteShape(shape)
        
    def RemoveShape(self,shape):
        self.diagram.DeleteShape(shape)

    def keyPress(self,event):
        key = event.GetKeyCode()
        if key ==127:  # DELETE
            #self.diagram.shapes = [n for n in self.diagram.shapes if not n in self.select()]
            for s in self.select():
                self.diagram.DeleteShape(s)
            self.deselect() #remove nodes 
        elif key ==67 and event.ControlDown():  # COPY
            del clipboard[:]
            for i in self.select():
                clipboard.append(i)
        elif key ==86 and event.ControlDown():  # PASTE
            for i in clipboard:
                self.AddShape(i.Copy())
        elif key == 9: # TAB
            if len(self.diagram.shapes)==0:
                return
            shape = self.select()
            if shape:
                ind = self.diagram.shapes.index(shape[0])
                self.deselect()
                try:
                    self.select(self.diagram.shapes[ind+1])
                except:
                    self.select(self.diagram.shapes[0])
            else:
                    self.select(self.diagram.shapes[0])
        elif key ==68 and event.ControlDown():  # CMD_D INFO
            pt = GetMousePosition()
            mouseX = pt[0] - self.GetScreenPosition().x
            mouseY = pt[1] - self.GetScreenPosition().y
            point = (mouseX, mouseY)
            # print "pt=%s mouse=%s,%s" % (pt, mouseX, mouseY)
            print("%s,%s %s" % (mouseX, mouseY, self.shapeFromPoint(point)))
        self.Refresh()

    def onPaintEvent(self, event):   
        dc = PaintDC(self)
        self.PrepareDC(dc)
        dc.SetUserScale(self.scalex,self.scaley)
        # dc.BeginDrawing()
        for item in self.diagram.shapes + self.nodes:
            item.draw(dc)
        # dc.EndDrawing()

    def OnRightDown(self,event):
        #ANDY
        #self.getCurrentShape(event).OnRightDown(event)

        #ANDY
        if False and self.getCurrentShape(event):
            self.getCurrentShape(event).OnRightDown(event)
        
    def OnRightUp(self,event):
        #ANDY        
        #self.getCurrentShape(event).OnRightUp(event)

        #ANDY
        if False and self.getCurrentShape(event):
            self.getCurrentShape(event).OnRightUp(event)
        else:
            #
            self.shape_popup_menu_is_of = self.getCurrentShape(event)
            self.popupmenu = Menu()
            item = self.popupmenu.Append(2021, "Properties...")
            self.Bind(EVT_MENU, self.OnPopupItemSelected, item)
            item = self.popupmenu.Append(2022, "Delete Node")
            self.Bind(EVT_MENU, self.OnDelete, item)
            item = self.popupmenu.Append(2023, "Cancel")
            self.Bind(EVT_MENU, self.OnPopupItemSelected, item)
            
            pos = event.GetPosition()
            # pos = self.ScreenToClient(pos)
            self.PopupMenu(self.popupmenu, pos)
        ########

    #ANDY
    def OnDelete(self, event):
        s = self.shape_popup_menu_is_of
        # MessageBox("You want to delete shape '%s'" % s)
        self.diagram.DeleteShape(s)
        self.deselect() #remove nodes
        self.Refresh()

    def OnPopupItemSelected(self, event):
        item = self.popupmenu.FindItemById(event.GetId())
        text = item.GetText() 
        # MessageBox("You selected item '%s'" % text)
        if text == "Properties...":
            f = AttributeEditor(None, -1, "props", self.shape_popup_menu_is_of)
            f.Show(True)
    ################        
        
    def OnRightDClick(self,event):
        self.getCurrentShape(event).OnRightDClick(event)
    def OnLeftDClick(self,event):
        self.getCurrentShape(event).OnLeftDClick(event)
    def OnLeftDown(self,event):
        item = self.getCurrentShape(event)
        
        if item is None:   #clicked on empty space deselect all
            self.deselect()
            return

        # ANDY
        # print('OnLeftDown', item, type(item), type(ResizeableNode), isinstance(item, Node))
        if not isinstance(item, Node):
            """bring node to the front"""
            # print('ChangeShapeOrder', item)
            self.diagram.ChangeShapeOrder(item,999) # ANDY bring selected shape to top

        item.OnLeftDown(event) # send leftdown event to current shape
        
        if isinstance(item,Selectable): 
            if not event.ShiftDown():  self.deselect()
        
        self.select(item) 
        self.Refresh()


    def OnLeftUp(self,event):
        try:
            shape = self.getCurrentShape(event)
            # print "master OnLeftUp", shape
            shape.OnLeftUp(event)
            shape.leftUp(self.select())
        except AttributeError:  # catch exceptions re shapes not implementing OnLeftUp or leftUp methods
            pass
        self.avoid_dangling_lines(shape, event, self.select())
        self.Refresh()

    def avoid_dangling_lines(self, shape, event, items):
        if len(items) == 1 and isinstance(items[0], ConnectionShape) and items[0].output is None:
            self.diagram.DeleteShape(items[0])
            self.deselect()  # remove nodes

    def OnMotion(self,event):
        if event.Dragging():
            point = self.getEventCoordinates(event)
            x = point[0] - self.currentPoint[0]
            y = point[1] - self.currentPoint[1]
            if DEBUG_DRAG:
                print('Dragging %s mouse at %s currentPoint is %s thus moveto difference is %s,%s' % (self.getSelectedShapes(), point, self.currentPoint, x, y))
            for i in self.getSelectedShapes():
                i.move(x,y)
            self.currentPoint = point
            self.Refresh()

    def SetDiagram(self,diagram):
        self.diagram=diagram

    def getCurrentShape(self,event):
        # get coordinate of click in our coordinate system
        point = self.getEventCoordinates(event)
        self.currentPoint = point
        # Look to see if an item is selected
        return self.shapeFromPoint(point)

    def shapeFromPoint(self, point):
        for item in self.nodes:
            if item.HitTest(point[0], point[1]):
                return item
        for item in reversed(self.diagram.shapes):
            if item.HitTest(point[0], point[1]):
                return item
        return None

    def getEventCoordinates(self, event):
        originX, originY = self.GetViewStart()
        unitX, unitY = self.GetScrollPixelsPerUnit()
        return [(event.GetX() + (originX * unitX)) / self.scalex, (event.GetY() + (originY * unitY))/ self.scaley]

    def getSelectedShapes(self):
        return self.selectedShapes

    def deselect(self,item=None):
        if item is None:
            for s in self.selectedShapes:
                s.OnDeselect(None)
            del self.selectedShapes[:]
            del self.nodes[:]
        else:
            self.nodes=[ n for n in self.nodes if n.item != item]
            self.selectedShapes = [ n for n in self.selectedShapes if n != item]
            item.OnDeselect(None)

    def select(self,item=None):
        if item is None:
            return self.selectedShapes
        
        if isinstance(item,Node):
            del self.selectedShapes[:]
            self.selectedShapes.append(item) # items here is a single node
            return
                
        if not item in self.selectedShapes:
            self.selectedShapes.append(item)
            item.OnSelect(None)
            if isinstance(item,Connectable):            
                self.nodes.extend( [INode(item,n,self) for n in range(item.input)] )
                self.nodes.extend( [ONode(item,n,self) for n in range(item.output)] )
            if isinstance(item,Resizeable):            
                self.nodes.extend( [ResizeableNode(item,n,self) for n in range(len(item.x))] )
            
    def showOutputs(self,item=None):
        if item:
            self.nodes.extend( [ONode(item,n,self) for n in range(item.output)] )
        elif item is None:
            for i in self.diagram.shapes:
                if isinstance(i,Connectable):
                    self.nodes.extend( [ONode(i,n,self) for n in range(i.output)] )

    def showInputs(self,item=None):
        if isinstance(item,Block):
            self.nodes.extend( [INode(item,n,self) for n in range(item.input)] )
        else:
            for i in self.diagram.shapes:
                if isinstance(i,Connectable):
                    self.nodes.extend( [INode(i,n,self) for n in range(i.input)] )




#Abstract Classes ------------------------------------------------------------------------------------------
class Selectable:
    '''
    Allows Shape to be selected
    '''
    def __init__(self):
        pass

class Resizeable:
    '''
    Creates resize Nodes that can be drug around the canvas
    to alter the shape or size of the Shape
    '''
    def __init__(self):
        pass
    
class ConnectableOriginal:
    '''
    Creates connection nodes or ports 
    '''
    def __init__(self):
        self.input=1
        self.output=3
        self.connections=[] # this will be the list containing downstream connections

    def getPort(self,type,num):
        """
        Calculate port location as (x,y).  Dynamically calculated based on the number
        of inputs and number of outputs.  Just divide the shape length by the number of
        ports and spread them evenly.

        Args:
            type: 'input' or 'output' where inputs are on the left of the shape
                    and outputs are on the rhs of the shape.
            num: port number

        Returns: port location as (x,y)

        """
        if type=='input':
            div = float(self.input+1.0)
            x=self.x[0]
        elif type=='output':
            div = float(self.output+1.0)
            x=self.x[1]
            
        dy=float(self.y[1] - self.y[0])/div
        y= self.y[0]+dy*(num+1)
        return(x,y)

class Connectable:
    '''
    Creates connection nodes or ports
    New version only has one port for in and one for out
    '''
    def __init__(self):
        self.input=1
        self.output=1
        self.connections=[] # this will be the list containing downstream connections

    def getPortXX(self,type,num):
        if type=='input':
            x=self.x[0]
        elif type=='output':
            x=self.x[1]
        y= self.y[0]
        return (x, y)

    def getPortXXXX(self,type,num):
        # calc centre - the problem is that input node and output node on the same point
        # and cannot be distinguished, meaning often try to drag from an input node, which
        # is 'undefined' and buggy.
        x = self.x[0] + (self.x[1] - self.x[0]) / 2
        y = self.y[0] + (self.y[1] - self.y[0]) / 2
        return (x, y)

    def getPortZ(self,type,num):
        # calc almost centre
        x = self.x[0] + (self.x[1] - self.x[0]) / 2
        y = self.y[0] + (self.y[1] - self.y[0]) / 2
        if type=='input':
            x -= 10
        return (x, y)

    def getPort(self,type,num):
        # centre of left and right sides
        if type=='input':
            x=self.x[0]
        elif type=='output':
            x=self.x[1]
        y = self.y[0] + (self.y[1] - self.y[0]) / 2
        return (x, y)

    def getCentre(self):
        # calc centre
        x = self.x[0] + (self.x[1] - self.x[0]) / 2
        y = self.y[0] + (self.y[1] - self.y[0]) / 2
        return (x, y)


class Attributable:
    '''
    Allows AttributeEditor to edit specified properties
    of the Shape
    '''
    def __init__(self):
        self.attributes=[]

    def AddAttribute(self,name):
        self.attributes.append(name)

    def AddAttributes(self,atts):
        self.attributes.extend(atts)
        
    def RemoveAttribute(self,name):
        self.attributes.remove(name)

#------------------------------------------------------------------------------------------------------------


class LinesShape(Shape,Resizeable):
    def __init__(self,points):
        Shape.__init__(self)
        self.x=[]
        self.y=[]
        for p in points:
            self.x.append(p[0])
            self.y.append(p[1])

    def draw(self,dc):
        Shape.draw(self,dc)
        ind = 0
        try:
            while 1:
                dc.DrawLine(self.x[ind], self.y[ind],self.x[ind+1], self.y[ind+1])
                ind = ind+1
        except:
            pass
        
    def HitTest(self, x, y):

        if x < min(self.x)-3:return False
        if x > max(self.x)+3:return False
        if y < min(self.y)-3:return False
        if y > max(self.y)+3:return False
        
        ind=0
        try:
            while 1:
                x1=self.x[ind]
                y1=self.y[ind]
                x2=self.x[ind+1]
                y2=self.y[ind+1]
    
                top= (x-x1) *(x2 - x1) + (y-y1)*(y2-y1)
                distsqr=pow(x1-x2,2)+pow(y1-y2,2)
                u=float(top)/float(distsqr)
            
                newx = x1 + u*(x2-x1)
                newy = y1 + u*(y2-y1)
           
                dist=pow(pow(newx-x,2) +  pow(newy-y,2),.5)
    
                if dist<7: 
                    return True
                ind = ind +1
        except IndexError:
            pass
        return False





class ConnectionShape(LineShape,Resizeable,Selectable):
    
    def __init__(self):
        LineShape.__init__(self)
        Resizeable.__init__(self)
        self.input = None
        self.output= None

    def setInput(self, shape, portnum):
        """
        Set the object and port you are dragging/connecting from
        Assign to self.input which is a tuple comprising (shape, portnum) where the portnum
        is a rhs output portnum, since we draw from an output port to an input port.

        Args:
            shape: the shape you are dragging from
            portnum: the port number 0..n you are dragging from

        Returns: -

        """
        self.input=(shape, portnum)
        
    def setOutput(self,shape,portnum):
        self.output=(shape,portnum)
        
    def draw(self,dc):
        # SHAPE = 0
        # PORT = 1
        if self.input:
            # self.x[0],self.y[0] = self.input[SHAPE].getPort('output',self.input[PORT])  # Original code

            shape, portnum = self.input
            if not self.output:
                # if haven't connected to something yet, keep drawing from node, not centre
                point = shape.getPort('output',portnum)
            else:
                point = shape.getCentre()
            self.x[0],self.y[0] = point
            if DEBUG_CONNECT:
                print("from shape output port %s at %s" % (portnum, point), end=' ')
                if not self.output: print()
        if self.output:
            # self.x[1],self.y[1] = self.output[SHAPE].getPort('input',self.output[PORT])

            shape, portnum = self.output
            # point = shape.getPort('input',portnum)
            point = shape.getCentre()
            self.x[1],self.y[1] = point
            if DEBUG_CONNECT:
                print("to shape input port %s at %s" % (portnum, point))
        LineShape.draw(self,dc)


class Block(RectangleShape,Connectable,Resizeable,Selectable,Attributable):
   
    def __init__(self):
        x, y, x2, y2 = rand_bounds()
        RectangleShape.__init__(self, x, y, x2, y2)
        Resizeable.__init__(self)
        Connectable.__init__(self)
        Attributable.__init__(self)
        self.AddAttributes(['label','pen','fill','input','output'])
        self.label='Block' 

    def draw(self,dc):
        RectangleShape.draw(self,dc)
        w,h =  dc.GetTextExtent(self.label)
        mx=int((self.x[0] + self.x[1])/2.0 )-int(w/2.0)
        my = int((self.y[0]+self.y[1])/2.0)-int(h/2.0)
        dc.DrawText(self.label,mx, my)

    def OnLeftDown(self,event):
        if isinstance(self,Block) and event.ControlDown():
            d=TextEntryDialog(None,'Block Label',defaultValue=self.label,style=OK)
            d.ShowModal()
            self.label = d.GetValue()

    # Original - pops up attribute properties editor instantly
    def OnRightDown(self,event):
        # f = AttributeEditor(None, -1, "props",self)
        # f.Show(True)
        wx.MessageBox("You r. down on shape '%s' event is %s" % (self, event))

    """
    Attempt to have a r.click menu on the shape, but this needs to be done in the shapecanvas window
    not in the individual shape because only the shape window has access to the .diagram object 
    which allows shape deletion.  Shapes don't have a back pointer to the shapecanvas window or to 
    the diagram which houses it, unfortunately.  
        - We need the shapecanvas window in order to bind popup menu etc. events
        - We need the shapecanvas window .diagram to access delete shape method 
    ANDYMAIN was a failed attempt to record the last shapecanvas window, which was hacky, and 
    also failed since there are nested containers in this demo.
    """
    #ANDY
    # def OnRightDown(self,event):
    #     self.popupmenu = Menu()
    #     item = self.popupmenu.Append(2011, "Properties...")
    #     ANDYMAIN.canvas.Bind(EVT_MENU, self.OnPopupItemSelected, item)
    #     item = self.popupmenu.Append(2012, "Delete Node")
    #     ANDYMAIN.canvas.Bind(EVT_MENU, self.OnPopupItemSelected, item)
    #     item = self.popupmenu.Append(2013, "Cancel")
    #     ANDYMAIN.canvas.Bind(EVT_MENU, self.OnPopupItemSelected, item)
    #     #
    #     pos = event.GetPosition()
    #     # pos = ANDYMAIN.canvas.ScreenToClient(pos)
    #     ANDYMAIN.canvas.PopupMenu(self.popupmenu, pos)
    # ##########
    #
    # #ANDY
    # def OnPopupItemSelected(self, event):
    #     item = self.popupmenu.FindItemById(event.GetId())
    #     text = item.GetText()
    #     #wx.MessageBox("You selected item '%s'" % text)
    #     if text == "Properties...":
    #         f = AttributeEditor(None, -1, "props",self)
    #         # f.moveto(item.x, item.y)  # ANDY
    #         f.Show(True)
    #     elif text == "Delete Node":
    #         print "Delete Node"
    #         # Block is a shape, but we need to get to the diagram which this shape is part of
    #         # we cannot, so move this logic into the ShapeCanvas not the Shape
    #         # self.diagram.DeleteShape(s)
    #         # self.deselect() #remove nodes

################ New Shapes

class EllipseShape(Shape):
    def __init__(self, x=20, y=20, x2=90, y2=90):
        Shape.__init__(self, [x, x2], [y, y2])
        self._width = x2-x
        self._height = y2-y

    def GetWidth(self):
        return self.x[1] - self.x[0]

    def GetHeight(self):
        return self.y[1] - self.y[0]

    def draw(self,dc):
        """The draw handler."""
        # if self._shadowMode != SHADOW_NONE:
        #     if self._shadowBrush:
        #         dc.SetBrush(self._shadowBrush)
        #     dc.SetPen(TransparentPen)
        #     dc.DrawEllipse(self._xpos - self.GetWidth() / 2.0 + self._shadowOffsetX,
        #                    self._ypos - self.GetHeight() / 2.0 + self._shadowOffsetY,
        #                    self.GetWidth(), self.GetHeight())

        # if self._pen:
        #     if self._pen.GetWidth() == 0:
        #         dc.SetPen(TransparentPen)
        #     else:
        #         dc.SetPen(self._pen)

        # if self._brush:
        #     dc.SetBrush(self._brush)

        # Drawn so it fits inside rectangle
        dc.DrawEllipse(self.x[0],
                       self.y[0],
                       self.GetWidth(),
                       self.GetHeight())

    def HitTest(self, x, y):
        # Crude copy of Rectangle test
        if x < self.x[0]: return False
        if x > self.x[1]: return False
        if y < self.y[0]: return False
        if y > self.y[1]: return False
        return True


class EllipseShapeAndy(EllipseShape, Connectable, Resizeable, Selectable, Attributable):
    def __init__(self):
        x, y, x2, y2 = rand_bounds()
        EllipseShape.__init__(self, x, y, x2, y2)
        Resizeable.__init__(self)
        Connectable.__init__(self)
        Attributable.__init__(self)
        # self.AddAttributes(['label', 'pen', 'fill', 'input', 'output'])
        # self.label = 'Block'


    ################
    
class CodeBlock(Block):

    def __init__(self):
        Block.__init__(self)
        self.AddAttribute('code')
        self.code=''
        self.label='Code'
                
    def OnLeftDClick(self,event):
        exec(str(self.code))

class ContainerBlock(Block,Diagram):

    def __init__(self):
        Block.__init__(self)
        Diagram.__init__(self)
                
        self.label='Container'        
        self.pen = ['BLACK' , 2]
        self.fill= ['GREEN']

    def OnLeftDClick(self,event):
        print("OnLeftDClick")
        f = CodeFrame(self)
        f.SetTitle(self.label)

        # Open new frame near container object click
        pos = event.GetEventObject().ClientToScreen(event.GetPosition())
        f.SetPosition(pos)

        f.Show(True)

# Nodes
class Node(PointShape):
    def __init__(self,item,index,cf):
        # print "Node creation item=%s index=%s cf=%s" % (item,index,cf)
        self.item=item      # shape to which node is attached
        self.index = index  # portnum
        self.cf =cf         # shape canvas
        PointShape.__init__(self)

    def showProperties(self):
        self.item.showProperties

class ConnectableNode(Node):
    def __init__(self,item,index,cf):
        Node.__init__(self,item,index,cf)

class INode(ConnectableNode):
    def __init__(self,item,index,cf):
        ConnectableNode.__init__(self,item,index,cf)

    def leftUp(self,items):
        """
        This gets called when you release the mouse when connecting to a destination input port
        The ConnectionShape item has .input and .output containing (shape, portnum) each.

        To know the 'from' shape you look at the ConnectionShape.input[0] which has an output node on a portnum
         and to know the 'to' shape you look at the ConnectionShape.output[0] which has an input node

        Args:
            items: list of ConnectionShape instances (really, only one)
        """
        if DEBUG_INODE_CONNECT:
            print("inode leftup", items, "ConnectionShape.input", items[0].input, "ConnectionShape.output", items[0].output)
        if len(items)==1 and isinstance(items[0],ConnectionShape):
            connection_shape = items[0]
            if connection_shape.output is None:  # means its not connected to anything
                connection_shape.setOutput(self.item,self.index)

    def move(self,x,y):
        """
        Dragging from an input doesn't make sense?
        """
        print("INode - Dragging from an input doesn't make sense? unless repositioning to re-attach?", self)
        self.cf.deselect()
        ci = ConnectionShape()
        self.cf.container.shapes.insert(0, ci)
        ci.setOutput(self.item,self.index)
        ci.x[0],ci.y[0] = self.item.getPort('input',self.index)
        self.cf.showOutputs()
        self.cf.select(ci)

    def draw(self,dc):
        # Each node instance has a property index (portnum) baked into it, as well as the item (shape)
        # Draw yourself on the shape at coords of the portnum on the input side (cos this is an INode)
        x,y=self.item.getPort('input',self.index)
        self.moveto(x,y)
        PointShape.draw(self,dc)

class ONode(ConnectableNode):
    def __init__(self,item,index,cf):
        ConnectableNode.__init__(self,item,index,cf)

    def move(self,x,y):
        """
        initiating a connection from output node, creating the shape and adding it to the
        shapecanvas, setting the input, output to be set later when leftUp over INode

        Note the subsequent multiple move() calls due to the OnMotion() goes to the
        ConnectionShape not to the ONode.
        """
        print("ONode initiating a connection from output node", self)
        self.cf.deselect()
        ci = ConnectionShape()
        self.cf.diagram.shapes.insert(0, ci)
        ci.setInput(self.item,self.index)
        ci.x[1],ci.y[1] = self.item.getPort('output',self.index)
        self.cf.showInputs()
        self.cf.select(ci)

    def leftUp(self,items):
        # Not sure the use of this, I don't think the setInput() ever gets executed
        print("onode leftup", items)
        if len(items)==1 and isinstance(items[0],ConnectionShape):
            if items[0].input is None:
                print("onode leftup, setting input", items)
                items[0].setInput(self.item,self.index)


    def draw(self,dc):
        x,y=self.item.getPort('output',self.index)
        self.moveto(x,y)
        PointShape.draw(self,dc)

class ResizeableNode(Node):
    def __init__(self,item,index,cf):
        Node.__init__(self,item,index,cf)
        self.fill=['BLACK']

    def draw(self,dc):
        item=self.item
        index=self.index
        self.moveto(item.x[index],item.y[index])
        PointShape.draw(self,dc)

    def move(self,x,y):
        self.item.x[self.index]+=x
        self.item.y[self.index]+=y

#---------------------------------------------------------------------------------------------------------

class AttributeEditor(Frame):
    def __init__(self, parent, ID, title,item):
        """Edits properties of 'item' as defined by the list of properties in item.attributes"""
        Frame.__init__(self, parent, ID, title,
                         DefaultPosition,Size(200, 450))
        self.item = item  # type Block

        # Create a box sizer for self
        box =BoxSizer(VERTICAL)
        self.SetSizer(box)
        
        tID = NewId()
        self.list = ListCtrl(self, tID, DefaultPosition, DefaultSize, LC_REPORT)
        self.SetSize(self.GetSize())
 
        self.list.InsertColumn(0, "Attribute")
        self.list.InsertColumn(1, "Value")

        self.accept = Button(self, NewId(), "Apply",size=(40,20))

        for c in range(len(item.attributes)):
            self.list.InsertItem(c , "")  # insert the list control item
            self.list.SetItem(c, 0, str(item.attributes[c]))  # set the list control item's 0 col

            # set the list control item's 1 col to actual value of the attribute, converted into
            # a string for display purposes
            temp = str( eval("item." + str(item.attributes[c])))
            self.list.SetItem(c, 1, temp)

        # This is the area we edit in - first select the attribute and then edit in here
        self.text    = TextCtrl(self,NewId(), "", style=TE_MULTILINE)
        self.text.SetBackgroundColour((255, 255, 230))  # set text back color

        # Close button
        button = wx.Button(self, label="Close")

        # The layout
        box.Add(self.list, 1,EXPAND)
        box.Add(self.text, 1,EXPAND)
        box.Add(self.accept, 0,EXPAND)
        box.Add(button, 0,EXPAND)

        self.Bind(EVT_LIST_ITEM_SELECTED, self.selectProp, self.list,tID)
        self.Bind(EVT_BUTTON, self.acceptProp, self.accept, self.accept.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, button)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.accept.Disable()

        # CMD-W to close Frame by attaching the key bind event to accellerator table
        randomId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=randomId)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('W'), randomId )])
        self.SetAcceleratorTable(accel_tbl)

    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()

    def selectProp(self,event):
        """When you click on an item in the list control, populate the edit text area with its content"""
        idx=self.list.GetFocusedItem()
        prop = self.list.GetItem(idx,0).GetText()
        val = self.list.GetItem(idx,1).GetText()
        self.text.Clear()
        self.text.WriteText(val)

        self.accept.Enable()

    def acceptProp(self,event):
        """Write the edited value back into the property"""
        idx=self.list.GetFocusedItem()
        print(idx)
        prop = self.list.GetItem(idx,0).GetText()  # calc property name

        if get_type(self.text.GetValue()) == str or self.text.GetNumberOfLines() > 1:
            val = self.text.GetValue()  # string
        else:
            val = eval(self.text.GetValue())  # convert string back into Python data e.g int or list
        setattr(self.item, prop, val)

        self.list.SetItem(idx, 1, str(getattr(self.item,prop)))


class CodeFrame(Frame):
    def __init__(self,diagram):
        Frame.__init__(self,None, -1, 'Untitled', size=(500,300))
        
        self.file=None
        menus={}

        menus['&Add']=[
            ('Code\tCtrl+n' , "Block that holds Python code",self.newCodeBlock),
            ('Container\tCtrl+f', 'Container of blocks', self.newContBlock),
            ('Point', 'Playing with points', self.newPointShape),
            ('Lines', 'Plotting', self.newLinesShape),
            ('Ellipse\tCtrl+l', 'Ellipse', self.newEllipseShape),
            ]

        menus['&Zoom']=[
            ('Zoom In\tCtrl+o' , "zoom in",self.zoomin),
            ('Zoom Out\tCtrl+p' , "zoom out",self.zoomout),
            ]

        menuMaker(self,menus)

        # Canvas Stuff
        self.canvas=ShapeCanvas(self,-1)
        self.canvas.SetDiagram(diagram)
        self.canvas.SetBackgroundColour(WHITE)

        #ANDY
        # global ANDYMAIN
        # ANDYMAIN = self
        #
        self.canvas.SetScrollbars(1, 1, 600, 400)
        self.canvas.SetVirtualSize((600, 400))
        ################
      
        self.Show(True)

    #ANDY
    #def OnPopupItemSelected(self, event):
    #    OnPopupItemSelected(self, event):
    #        
    #    item = self.popupmenu.FindItemById(event.GetId()) 
    #    text = item.GetText() 
    #    wx.MessageBox("You selected item '%s'" % text)
    #    if text == "Properties...":
    #        f = AttributeEditor(NULL, -1, "props",self)
    #        f.Show(True)
    ################
    
        # CMD-W to close Frame by attaching the key bind event to accellerator table
        randomId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=randomId)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('W'), randomId )])
        self.SetAcceleratorTable(accel_tbl)

    def OnCloseWindow(self, event):
        self.Destroy()
    
    def zoomin(self,event):
        self.canvas.scalex=max(self.canvas.scalex+.05,.3)
        self.canvas.scaley=max(self.canvas.scaley+.05,.3)

        #ANDY
        self.canvas.SetVirtualSize((1900, 1600))

        self.canvas.Refresh()


    def zoomout(self,event):
        self.canvas.scalex=self.canvas.scalex-.05
        self.canvas.scaley=self.canvas.scaley-.05
        self.canvas.Refresh()

    def newCodeBlock(self, event):
        i = CodeBlock()
        # self.canvas.AddShape(i)
        self.canvas.InsertShape(i, 999)
        self.canvas.deselect()
        self.canvas.Refresh()

    def newContBlock(self, event):
        i = ContainerBlock()
        self.canvas.AddShape(i)
        self.canvas.deselect()
        self.canvas.Refresh()
                
    def newPointShape(self, event):
        i = PointShape(50,50)
        self.canvas.AddShape(i)
        self.canvas.deselect()
        self.canvas.Refresh()
        
    def newEllipseShape(self, event):
        # x, y, x2, y2 = rand_bounds()
        # i = EllipseShape(x, y, x2, y2)
        i = EllipseShapeAndy()  # random happens within
        self.canvas.InsertShape(i, 9999)
        self.canvas.deselect()
        self.canvas.Refresh()

    def newLinesShape(self, event):
        points=[
            (5,30),(10,20),(20,25),(30,50),(40,70),
            (50,30),(60,20),(70,25),(80,50),(90,70),
            (100,30),(110,20),(115,25),(120,50),(125,70),
            (130,30),(135,20),(140,25),(150,50),(160,70),
            (165,30),(170,20),(175,25),(180,50),(200,70),
            ]
        i = LinesShape(points)
        self.canvas.AddShape(i)
        self.canvas.deselect()
        self.canvas.Refresh()

# Util - ANDY

def rand_bounds():
    x = random.randint(20, 350)
    y = random.randint(20, 150)
    x2 = x + 70
    y2 = y + 70
    return x, y, x2, y2

def rand_brush():
    brushes = [BLUE_BRUSH, GREEN_BRUSH, YELLOW_BRUSH, WHITE_BRUSH, BLACK_BRUSH, GREY_BRUSH, MEDIUM_GREY_BRUSH, LIGHT_GREY_BRUSH, TRANSPARENT_BRUSH, CYAN_BRUSH, RED_BRUSH]
    return random.choice(brushes)

from ast import literal_eval


def get_type(input_data):
    """
    Guess type of input string

    print(get_type("1"))        # <class 'int'>
    print(get_type("1.2354"))   # <class 'float'>
    print(get_type("True"))     # <class 'bool'>
    print(get_type("abcd"))     # <class 'str'>

    See https://stackoverflow.com/questions/22199741/identifying-the-data-type-of-an-input

    Args:
        input_data: str

    Returns: type class
    """
    try:
        return type(literal_eval(input_data))
    except (ValueError, SyntaxError):
        # A string, so return str
        return str

################################

if __name__ == '__main__':

    class MyApp(App):
        def OnInit(self):
            frame = CodeFrame(ContainerBlock())
            return True

    ##########################################

    app = MyApp(0)
    app.MainLoop()


