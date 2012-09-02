##########################################
# OGLlike - OGL like library for wxPython 
# http://www.lechak.info/download/OGLlike.py
# Copyright (C) 2003-2004  Erik R. Lechak
# Feel free to use it, modify it, distribute it.  All I ask is:
#   1)  If you improve it, please send me a copy of the improved version.  
#   2)  Please don't try to take credit for my work.
##########################################

from wxPython.wx import *
import pickle
import os
import sys
import copy

#Global Stuff   -------------------------------------------------------------------------
clipboard=[]

def menuMaker(frame, menus):
    menubar = wxMenuBar()
    for m,n in menus.items():
        menu = wxMenu()
        menubar.Append(menu,m)
        for x in n:
            id = wxNewId()
            menu.Append(id,x[0],x[1])
            EVT_MENU(frame, id,  x[2])
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
            print "problem saving this diagram"
 
    def LoadFile(self,file=None):
        if file is None:
            return
        try:
            self.shapes = pickle.load(open(file))
        except:
            print "problem loading this diagram"

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
        dc.SetPen(wxPen(self.pen[0], self.pen[1], wxSOLID))
        dc.SetBrush(wxBrush(self.fill[0], wxSOLID))

    def move(self,x,y):
        self.x = map((lambda v: v+x), self.x)
        self.y = map((lambda v: v+y), self.y)

    def Copy(self):
        return copy.deepcopy(self)


class LineShape(Shape):
    def __init__(self,x1=20, y1=20, x2=50, y2=50):
        Shape.__init__(self, [x1,x2] ,  [y1,y2])

    def draw(self,dc):
        Shape.draw(self,dc)
        dc.DrawLine(self.x[0], self.y[0],self.x[1], self.y[1])

    def HitTest(self, x, y):
        if x < min(self.x)-3:return false
        if x > max(self.x)+3:return false
        if y < min(self.y)-3:return false
        if y > max(self.y)+3:return false
            
        top= (x-self.x[0]) *(self.x[1] - self.x[0]) + (y-self.y[0])*(self.y[1]-self.y[0])
        distsqr=pow(self.x[0]-self.x[1],2)+pow(self.y[0]-self.y[1],2)
        u=float(top)/float(distsqr)
        
        newx = self.x[0] + u*(self.x[1]-self.x[0])
        newy = self.y[0] + u*(self.y[1]-self.y[0])
       
        dist=pow(pow(newx-x,2) +  pow(newy-y,2),.5)

        if dist>7: return false
        return true


class RectangleShape(Shape):
    def __init__(self,x=20, y=20, x2=90, y2=90):
        Shape.__init__(self, [x,x2] ,  [y,y2])

    def draw(self,dc):
        Shape.draw(self,dc)
        dc.DrawRectangle(int(self.x[0]), int(self.y[0]),int(self.x[1]-self.x[0]), int(self.y[1]-self.y[0]))
        
    def HitTest(self, x, y):
        if x < self.x[0]: return false
        if x > self.x[1]: return false
        if y < self.y[0]: return false
        if y > self.y[1]: return false
        return true

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
        self.x = map((lambda v: v+x), self.x)
        self.y = map((lambda v: v+y), self.y)
        self.graphic.move(x,y)

    def HitTest(self, x, y):
        return self.graphic.HitTest(x,y)

    def draw(self,dc):
        self.graphic.pen = self.pen
        self.graphic.fill = self.fill
        self.graphic.draw(dc)
#---------------------------------------------------------------------------------------------------------------



class ShapeCanvas(wxScrolledWindow):
    def __init__(self,
        parent,
        id=-1,
        pos=(-1,-1),
        size=(-1,-1),
        style=0,
        name="",
        ):
        wxScrolledWindow.__init__(self,parent,id,pos,size,style,name)
        self.diagram=None
        self.nodes=[]
        self.currentPoint = [0,0] # x and y of last mouse click
        self.selectedShapes=[]
        self.scalex =1.0
        self.scaley =1.0

        #Window Events        
        EVT_PAINT(self, self.onPaintEvent)
        #Mouse Events
        EVT_LEFT_DOWN(self, self.OnLeftDown)
        EVT_LEFT_UP(self, self.OnLeftUp)
        EVT_LEFT_DCLICK(self, self.OnLeftDClick)
        
        EVT_RIGHT_DOWN(self, self.OnRightDown)
        EVT_RIGHT_UP(self, self.OnRightUp)
        EVT_RIGHT_DCLICK(self, self.OnRightDClick)
        
        EVT_MOTION(self, self.OnMotion)
        #Key Events
        EVT_KEY_DOWN(self,self.keyPress)

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
        self.Refresh()

    def onPaintEvent(self, event):   
        dc = wxPaintDC(self)
        self.PrepareDC(dc)
        dc.SetUserScale(self.scalex,self.scaley)
        dc.BeginDrawing()
        for item in self.diagram.shapes + self.nodes:
            item.draw(dc)
        dc.EndDrawing()

    def OnRightDown(self,event):
        self.getCurrentShape(event).OnRightDown(event)
    def OnRightUp(self,event):
        self.getCurrentShape(event).OnRightUp(event)
    def OnRightDClick(self,event):
        self.getCurrentShape(event).OnRightDClick(event)
    def OnLeftDClick(self,event):
        self.getCurrentShape(event).OnLeftDClick(event)
    def OnLeftDown(self,event):
        item = self.getCurrentShape(event)
        
        if item is None:   #clicked on empty space deselect all
            self.deselect()
            return
            
        item.OnLeftDown(event) # send leftdown event to current shape
        
        if isinstance(item,Selectable): 
            if not event.ShiftDown():  self.deselect()
        
        self.select(item) 
        self.Refresh()


    def OnLeftUp(self,event):
        try:
            shape = self.getCurrentShape(event)
            shape.OnLeftUp(event)
            shape.leftUp(self.select())
        except:
            pass 
        self.Refresh()

    def OnMotion(self,event):
        if event.Dragging():            
            point = self.getEventCoordinates(event)
            x = point[0] - self.currentPoint[0]
            y = point[1] - self.currentPoint[1]
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
        for item in self.nodes + self.diagram.shapes:
            if item.HitTest(point[0],point[1]) :
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
    
class Connectable:
    '''
    Creates connection nodes or ports 
    '''
    def __init__(self):
        self.input=1
        self.output=3
        self.connections=[] # this will be the list containing downstream connections

    def getPort(self,type,num):
        if type=='input':
            div = float(self.input+1.0)
            x=self.x[0]
        elif type=='output':
            div = float(self.output+1.0)
            x=self.x[1]
            
        dy=float(self.y[1] - self.y[0])/div
        y= self.y[0]+dy*(num+1)
        return(x,y)

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

        if x < min(self.x)-3:return false
        if x > max(self.x)+3:return false
        if y < min(self.y)-3:return false
        if y > max(self.y)+3:return false
        
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
                    return true
                ind = ind +1
        except IndexError:
            pass
        return false





class ConnectionShape(LineShape,Resizeable,Selectable):
    
    def __init__(self):
        LineShape.__init__(self)
        Resizeable.__init__(self)
        self.input = None
        self.output= None

    def setInput(self,item,index):
        self.input=(item,index)
        
    def setOutput(self,item,index):
        self.output=(item,index)
        
    def draw(self,dc):   
        if self.input:
            self.x[0],self.y[0] = self.input[0].getPort('output',self.input[1])
        if self.output:
            self.x[1],self.y[1] = self.output[0].getPort('input',self.output[1])
        LineShape.draw(self,dc)


class Block(RectangleShape,Connectable,Resizeable,Selectable,Attributable):
    def __init__(self):
        RectangleShape.__init__(self)
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
            d=wxTextEntryDialog(None,'Block Label',defaultValue=self.label,style=wxOK)
            d.ShowModal()
            self.label = d.GetValue()

    def OnRightDown(self,event):
        f = AttributeEditor(NULL, -1, "props",self)
        f.Show(true)



class CodeBlock(Block):

    def __init__(self):
        Block.__init__(self)
        self.AddAttribute('code')
        self.code=''
        self.label='Code'
                
    def OnLeftDClick(self,event):
        exec str(self.code)

class ContainerBlock(Block,Diagram):

    def __init__(self):
        Block.__init__(self)
        Diagram.__init__(self)
                
        self.label='Container'        
        self.pen = ['BLACK' , 2]
        self.fill= ['GREEN']

    def OnLeftDClick(self,event):
        f = CodeFrame(self)
        f.SetTitle(self.label)
        f.Show(true)

# Nodes
class Node(PointShape):
    def __init__(self,item,index,cf):
        self.item=item
        self.index = index
        self.cf =cf
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
        if len(items)==1 and isinstance(items[0],ConnectionShape):
            if items[0].output is None:
                items[0].setOutput(self.item,self.index)

    def move(self,x,y):
        self.cf.deselect()
        ci = ConnectionShape()
        self.cf.container.shapes.insert(0, ci)
        ci.setOutput(self.item,self.index)
        ci.x[0],ci.y[0] = self.item.getPort('input',self.index)
        self.cf.showOutputs()
        self.cf.select(ci)

    def draw(self,dc):
        x,y=self.item.getPort('input',self.index)
        self.moveto(x,y)
        PointShape.draw(self,dc)

class ONode(ConnectableNode):
    def __init__(self,item,index,cf):
        ConnectableNode.__init__(self,item,index,cf)

    def move(self,x,y):
        self.cf.deselect()
        ci = ConnectionShape()
        self.cf.diagram.shapes.insert(0, ci)
        ci.setInput(self.item,self.index)
        ci.x[1],ci.y[1] = self.item.getPort('output',self.index)
        self.cf.showInputs()
        self.cf.select(ci)

    def leftUp(self,items):
        if len(items)==1 and isinstance(items[0],ConnectionShape):
            if items[0].input is None:
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

class AttributeEditor(wxFrame):
    def __init__(self, parent, ID, title,item):
        wxFrame.__init__(self, parent, ID, title,
                         wxDefaultPosition, wxSize(200, 450))
        self.item = item
        # Create a box sizer for self
        box = wxBoxSizer(wxVERTICAL)
        self.SetSizer(box)
        
        tID = wxNewId()
        self.list = wxListCtrl(self, tID, wxDefaultPosition, wxDefaultSize, wxLC_REPORT)
        self.SetSize(self.GetSize())
 
        self.list.InsertColumn(0, "Attribute")
        self.list.InsertColumn(1, "Value")

        accept = wxButton(self, wxNewId(), "Accept",size=(40,20))

        for c in range(len(item.attributes)):
            self.list.InsertStringItem(c , "")
            self.list.SetStringItem(c, 0, str(item.attributes[c]))
            temp = str( eval("item." + str(item.attributes[c])))
            self.list.SetStringItem(c, 1, temp)
        
        self.text    = wxTextCtrl(self,wxNewId(), "", style=wxTE_MULTILINE)
        
        box.Add(self.list, 1,wxEXPAND) 
        box.Add(accept, 0,wxEXPAND) 
        box.Add(self.text, 1,wxEXPAND) 

        EVT_LIST_ITEM_SELECTED(self.list,tID, self.selectProp)
        EVT_BUTTON(accept, accept.GetId(), self.acceptProp)
        
    def selectProp(self,event):
        idx=self.list.GetFocusedItem()
        prop = self.list.GetItem(idx,0).GetText()
        val = self.list.GetItem(idx,1).GetText()
        self.text.Clear()
        self.text.WriteText(val)
        
    def acceptProp(self,event):
        idx=self.list.GetFocusedItem()
        prop = self.list.GetItem(idx,0).GetText()
        lines = self.text.GetNumberOfLines()
        if lines ==1:
            exec 'self.item.' + prop +'='+self.text.GetValue()
        else:
            p=setattr(self.item,prop,self.text.GetValue())
            
        self.list.SetStringItem(idx, 1, str(getattr(self.item,prop)))


class CodeFrame(wxFrame):
    def __init__(self,diagram):
        wxFrame.__init__(self,None, -1, 'Untitled', size=(500,300))
        
        self.file=None
        menus={}

        menus['&Add']=[
            ('Code' , "Block that holds code",self.newCodeBlock),
            ('Container', 'Block that holds blocks', self.newContBlock),
            ('Point', 'Playing with points', self.newPointShape),
            ('Lines', 'Plotting', self.newLinesShape),
            ]

        menus['&Zoom']=[
            ('Zoom In\tCtrl+o' , "zoom in",self.zoomin),
            ('Zoom Out\tCtrl+p' , "zoom out",self.zoomout),
            ]

        menuMaker(self,menus)

        # Canvas Stuff
        self.canvas=ShapeCanvas(self,-1)
        self.canvas.SetDiagram(diagram)
        self.canvas.SetBackgroundColour(wxWHITE)

        self.Show(true)

    def zoomin(self,event):
        self.canvas.scalex=max(self.canvas.scalex+.05,.3)
        self.canvas.scaley=max(self.canvas.scaley+.05,.3)
        self.canvas.Refresh()

    def zoomout(self,event):
        self.canvas.scalex=self.canvas.scalex-.05
        self.canvas.scaley=self.canvas.scaley-.05
        self.canvas.Refresh()

    def newCodeBlock(self, event):
        i = CodeBlock()
        self.canvas.AddShape(i)
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
        
        
class MyApp(wxApp):
    def OnInit(self):
        frame = CodeFrame(ContainerBlock())
        return true

##########################################

app = MyApp(0)
app.MainLoop()

