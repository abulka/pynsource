# ***********************************************************************
# Simple but effective 2D-drawing module with drag and drop
#
# License: freeware, under the terms of the BSD-license
# Original version Copyright (C) 2007 Erik Lechak
# Modified version Copyright (C) 2007..2008 Stef Mientki
# mailto: ...
# Please let me know if it works or not under different conditions
#
# <Version: 2.1    , 21-07-2008,  Stef Mientki
# Test Conditions: 2
#    - improved perpendicular connection lines (for hor only)
#    - improved hit test for connection lines (for hor only)
#    - added DB_Table_Shape
#
# <Version: 2.0    , 19-04-2008,  Stef Mientki
# Test Conditions: 1
#    - refactored
#    - perpendicular connection lines, Lucian Iuga
#    - 2D-Scene elements added
#    - painting changed to buffered painting
#
# <Version: 1.0    , 01-12-2007,  Stef Mientki
# Test Conditions: 1
#    - orginal release
#
# Test Conditions
# 1. WinXP-SP2, Python 2.4.3, wxPython wx-2.8-msw-ansi
# 2. WinXP-SP2, Python 2.5.2, wxPython 2.8.7.1 (msw-unicode)
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
"""
  Diagram
  ShapeCanvas ( wx.ScrolledWindow )
  ShapeEvtHandler
    Shape
      PointShape
        Node
          INode
          ONode
          ResizeableNode
        ResizeableNode_2D
      LineShape
        Connection_Line
      t_BaseShape
        Rectangle
"""
# ***********************************************************************

import wx
import PyLab_Works_Globals as PG
from   menu_support    import *
from   utility_support import *

import pickle
import os
import sys
import copy

#clipboard   = []
TIO_Brush   = []
temp_dev_nr = 1
IO_r        = 4

# ***********************************************************************
# ***********************************************************************
class Diagram:
  def __init__(self):
    self.shapes=[]
      
  def SaveFile(self,file=None):
    if file is None:
      return
    try:
      pickle.dump(self.shapes,open(file,'w'))
    except:
      print "problem saving this diagram"

  def LoadFile(self,file=None):
    if file is None:
      return
    try:
      self.shapes = pickle.load(open(file))
    except:
      print "problem loading this diagram"

  def AddShape ( self, shape, after = None ) :
    if after:
      self.shapes.insert ( self.shapes.index(after), shape )
    else:
      self.shapes.insert ( 0, shape )
          
  def AppendShape ( self, shape ) :
    self.shapes.append ( shape )
      
  def InsertShape ( self, shape, index = 0 ) :
    self.shapes.insert ( index, shape )
  
  def DeleteShape ( self, shape ) :
    self.shapes.remove ( shape )
  
  def PopShape ( self, index = -1 ) :
    return self.shapes.pop ( index )

  def DeleteAllShapes ( self ) :
    del self.shapes[:]

  def ChangeShapeOrder(self, shape, pos=0):
    self.shapes.remove(shape)
    self.shapes.insert(pos,shape)

  def GetCount(self):
    return len(self.shapes)
      
  def GetShapeList(self):
    return self.shapes
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class ShapeCanvas ( wx.ScrolledWindow ) :
  def __init__(self,
    parent,
    id     = -1,
    pos    = ( -1, -1 ),
    size   = ( -1, -1 ),
    style  = 0,
    Design = None,
    name   = "" ):

    # default Coordinate system
    self._W  =  100
    self._H  =  100
    self.WCl = -100
    self.WCr =  100
    self.WCb = -100
    self.WCt = self.WCb + self._H * ( self.WCr - self.WCl ) / self._W
    self.WC_Auto         = True
    self.CrossHair       = None
    self.old_CMemo       = None
    self.CMemo_Labels    = []
    self.RubberBand      = None
    self.Orientation_Hor = None

    wx.ScrolledWindow.__init__(self,parent,id,pos,size,style,name)
    self.diagram = None
    self.nodes   = []
    self.currentPoint   = [0,0] # x and y of last mouse click
    self.selectedShapes = []
    self.scalex  = 1.0
    self.scaley  = 1.0
    self.parent  = parent
    self.Design  = Design

    global TIO_Brush
    TIO_Brush = [
          wx.Brush ( ( 255, 0,   0   ) ),
          wx.Brush ( ( 0,   255, 0   ) ),
          wx.Brush ( ( 0,   0,   255 ) ),
          wx.Brush ( ( 0,   0,   255 ) ),
          wx.Brush ( ( 200, 200,  50 ) ),
          wx.Brush ( ( 50,  200, 200 ) ),
          wx.Brush ( ( 200, 50,  200 ) ),
          wx.Brush ( ( 50,  50,  200 ) ),
          wx.Brush ( ( 97, 197,  255 ) ),
        ]

    # *************************************************************
    # popup menus
    # *************************************************************
    pre  = ['Insert New']
    if self.Design :
      pre.append ('Group Bricks')
    self.Popup_Menu_Canvas = My_Popup_Menu ( self._OnPopupItemSelected, 1,
      pre = pre,
      post = ['ToDo'] )
    self.Bind ( wx.EVT_CONTEXT_MENU, self._OnShowPopup )

    self.Bind ( wx.EVT_LEFT_DOWN,    self._On_Left_Down   )
    self.Bind ( wx.EVT_LEFT_UP,      self._On_Left_Up     )
    self.Bind ( wx.EVT_LEFT_DCLICK,  self._On_Left_DClick )

    self.Bind ( wx.EVT_KEY_DOWN,     self._On_Key_Down    )
    self.Bind ( wx.EVT_MOTION,       self._On_Motion      )
    self.Bind ( wx.EVT_MIDDLE_DOWN,  self._On_Middle_Down )
    self.Bind ( wx.EVT_PAINT,        self._On_Paint       )
    self.Bind ( wx.EVT_SIZE,         self._OnSize         )

    # initialize paint buffer
    self._OnSize ( None )

  # *********************************************************
  #  Ctrl-C = copy Canvas to clipboard
  # *********************************************************
  def _On_Key_Down ( self, event ) :
    key = event.GetKeyCode()
    if key == ord('C') and event.ControlDown():
      data = wx.BitmapDataObject()
      data.SetBitmap ( self._Paint_Buffer )
      if wx.TheClipboard.Open () :
        wx.TheClipboard.SetData ( data )
        wx.TheClipboard.Close ()

  # *********************************************************
  # *********************************************************
  def _OnSize ( self, event ) :
    self._W, self._H = self.GetClientSize ()
    if self._W <= 0 : return
    if self.WC_Auto :
      self.WCt = self.WCb + self._H * ( self.WCr - self.WCl ) / self._W
    w, h = self.GetClientSize ()
    self._Paint_Buffer = wx.EmptyBitmap ( w, h )
    self.Refresh ()

  # ************************************
  # ************************************
  def Set_Coordinates ( self, LB = (-100,-100),
                              WH = ( 200, None ),
                              RT = None ) :
    print LB,WH,RT
    if RT :
      if ( len ( RT ) > 1 ) and RT [1] :
        h = RT [1] - LB [1]
      else :
        h = None
      WH = [ RT [0] - LB [0], h ]
    self.WCl = LB [0]
    self.WCr = LB [0] + WH [0]
    self.WCb = LB [1]

    if WH [1] :
      self.WC_Auto = False
      self.WCt = LB [1] + WH [1]
    else :
      self.WC_Auto = True
      self.WCt = self.WCb + self._H * ( self.WCr - self.WCl ) / self._W


  # *********************************************************
  # *********************************************************
  def Refresh ( self ) :
    dc = wx.BufferedDC ( wx.ClientDC ( self ), self._Paint_Buffer )
    dc.SetBackground ( wx.Brush ( self.GetBackgroundColour () ) )
    dc.Clear ()

    if self.CrossHair :
      dc.CrossHair ( *self.CrossHair )

    if self.diagram :
      for item in self.diagram.shapes + self.nodes:
        item.draw ( dc )

  # *********************************************************
  # *********************************************************
  def _On_Paint ( self, event ) :
    dc = wx.BufferedPaintDC ( self, self._Paint_Buffer )

  # *********************************************************
  # Translates horizontal world value x to screen coordinates
  # *********************************************************
  def W2Sx ( self, x ) :
    return int ( 1.0*self._W * ( x        - self.WCl ) /
                           ( self.WCr - self.WCl ) )

  # *********************************************************

  # *********************************************************
  # Translates screen to world coordinates
  # *********************************************************
  def S2W ( self, x, y ) :
    X = self.WCl + 1.0 * ( self.WCr - self.WCl ) * x / self._W
    Y = self.WCb + 1.0 * ( self.WCt - self.WCb ) * ( self._H - y ) / self._H
    return X, Y

  # *********************************************************
  # Translates vertical world value y to screen coordinates
  # *********************************************************
  def W2Sy ( self, y ) :
    return int ( 1.0*self._H - self._H * ( y        - self.WCb ) /
                                     ( self.WCt - self.WCb) )

  # *********************************************************
  # Translates horizontal world differences to screen coordinates
  # *********************************************************
  def W2S_w ( self, x ) :
    return int ( 1.0*self._W * x / ( self.WCr - self.WCl ) )

  # *********************************************************
  # *********************************************************
  def Add_Trail ( self ) :
    for shape in self.diagram.shapes :
      shape.Add_Trail ()

  # *********************************************************
  # *********************************************************
  def _OnShowPopup ( self, event ) :
    self.Hit_Pos = self.ScreenToClient ( event.GetPosition () )
    self.Popup_Menu_Canvas.SetEnabled ( 1, self.Design and self.RubberBand )
    self.PopupMenu ( self.Popup_Menu_Canvas, pos = self.Hit_Pos )

  # *********************************************************
  # *********************************************************
  def _OnPopupItemSelected ( self, event ) :
    ID = event.Int
    if ID == 0 :
      pass

  # *********************************************************
  # *********************************************************
  def AddShape ( self, shape, after = None ) :
    self.diagram.AddShape ( shape, after )
    self.Refresh ()

  # *********************************************************
  # *********************************************************
  def AppendShape ( self, shape ) :
    self.diagram.AppendShape ( shape )

  # *********************************************************
  # *********************************************************
  def DeleteShape ( self, shape ):
    self.diagram.DeleteShape ( shape )

  # *********************************************************
  # *********************************************************
  def InsertShape(self, shape, index=0):
    self.diagram.InsertShape(shape,index)

  # *********************************************************
  # *********************************************************
  def Print_All ( self ) :
    print 'Shapes: ****************************************'
    for item in self.diagram.shapes:
      print ' ', str ( item.__class__ ).split('.')[1],
      if   isinstance ( item, Rectangle ) :
        print ' : ' + item.Caption  + '  ================================='
      elif isinstance ( item, Connection_Line ) :
        print ''
        print '    input  =', item.input
        print '    output =', item.output
      else :
        print ''
      print '    x, y, color  =', item._x, ',', item._y, ',', \
                                  item.fill, ',', item.pen


      for node in self.nodes:
        if node.item == item :
          print '   ', str ( node.__class__ ).split('.')[1] + \
                '  ---------------------------------'
          print '      x, y, color  =', node._x, ',', node._y, ',', \
                                        node.fill, ',', node.pen

  # *********************************************************
  # *********************************************************
  def _On_Left_DClick ( self, event ) :
    item = self.getCurrentShape ( event )
    if item :
      item.OnLeftDClick ( event )
    else :
      if self.Design :
        #Toggle the rubberband
        self.Deselect_All ()
        if self.RubberBand :
          self.DeleteShape ( self.RubberBand )
          self.RubberBand = None
        else :
          self.RubberBand = t_RubberBand_Shape (
            self.RubberBand_XY [0], self.RubberBand_XY [1],
            self.RubberBand_XY [0]+10, self.RubberBand_XY [1]+10 )
            #self.RubberBand_XY [0]+dx, self.RubberBand_XY [1]+dy )
          self.AppendShape ( self.RubberBand )
          self.select ( self.RubberBand )

  # *********************************************************
  # *********************************************************
  def _On_Left_Down ( self, event ) :
    self.SetFocus ()
    item = self.getCurrentShape ( event )
    if item is None:
      self.Deselect_All ()

      if self.Design and  not ( self.RubberBand ) :
        self.RubberBand_XY = event.GetPosition ()
      return

    item.OnLeftDown(event) # send leftdown event to current shape

    if item.Selectable:
      if not event.ShiftDown():  self.Deselect_All()
    self.select ( item )
    self.Refresh ()

  # *********************************************************
  # *********************************************************
  def _On_Left_Up ( self, event ):
    #print 'CANVAS UP'
    for item in self.Get_Current_Shapes ( event ):
      if isinstance ( item, INode ) :
        print 'Canvas up', self.selectedShapes
        #shape.OnLeftUp ( event )
        """
        afhankelijk of de eerste of twede keer:
        Canvas up [<OGLlike.Connection_Line instance at 0x01E05DC8>, <OGLlike.ResizeableNode instance at 0x01E067D8>]
        Canvas up [<OGLlike.ResizeableNode instance at 0x01E06968>]
        """
    try:
      shape = self.getCurrentShape ( event )
      #print ' KKK',shape,type(shape) #, shape.item

      # *********************************************************
      # Rubberband Grouping
      # *********************************************************
      if self.Design :
        RB = None
        if isinstance ( shape, ResizeableNode ) :
          if shape.item and ( shape.item == self.RubberBand ) :
            RB = shape.item
        elif isinstance ( shape, t_RubberBand_Shape ) :
          RB = shape
        if RB:
          x0 = RB._x[0] + RB._x[1]
          dx = abs ( RB._x[0] - RB._x[1] )
          y0 = RB._y[0] + RB._y[1]
          dy = abs ( RB._y[0] - RB._y[1] )
          for item in self.diagram.shapes :
            if isinstance ( item, Rectangle ) :
              x, y = item.Get_Center ()
              if ( 2*x >= x0 - dx ) and \
                 ( 2*x <= x0 + dx ) and \
                 ( 2*y >= y0 - dy ) and \
                 ( 2*y <= y0 + dy ) :
                print 'GROUPING', item
        # *********************************************************

      shape.leftUp ( self.select() )

    except:
      pass
    self.Refresh()

  # *********************************************************
  # *********************************************************
  def _On_Middle_Down ( self, event ) :
    if self.old_CMemo :
      self.old_CMemo.Destroy ()
      self.old_CMemo = None
      self.CMemo_Labels = []
      self.CrossHair = None
      self.Refresh ()
    else :
      self.old_CMemo = wx.Panel ( self )
      self.old_CMemo.SetBackgroundColour ( self.GetBackgroundColour () )
      Sizer = wx.BoxSizer ( wx.VERTICAL )
      self.old_CMemo.SetSizer ( Sizer )
      for i in range ( 3 ) :
        label = wx.StaticText ( self.old_CMemo )
        self.CMemo_Labels.append ( label )
        label.SetForegroundColour ( wx.BLUE )
        Sizer.Add ( label, 0, wx.EXPAND )
      self._On_Motion ( event )


  # *********************************************************
  # *********************************************************
  def _On_Motion ( self, event ) :

    # *********************************************************
    # Measurement Cursor
    # *********************************************************
    if event.MiddleIsDown ():
      if self.old_CMemo :
        self.CrossHair = X,Y = event.GetPosition ()
        self.Refresh ()
        x, y = self.S2W ( X, Y )
        self.CMemo_Labels[0].SetLabel ( '  x = ' + nice_number ( x ) )
        self.CMemo_Labels[1].SetLabel ( '  y = ' + nice_number ( y ) )
        self.CMemo_Labels[2].SetLabel ( '  t = todo' )

        if X > self._W - 60 : X = X - 64
        if Y < 40 : Y = self._H - 40
        else      : Y = 2
        self.old_CMemo.SetPosition ( ( X + 2, Y ) )

        self.old_CMemo.Refresh()
        self.old_CMemo.SetSize ( ( 60, 40 ) )

      return
    # *********************************************************

    
    #print 'Move'
    point = self.getEventCoordinates(event)
    dx = point[0] - self.currentPoint[0]
    dy = point[1] - self.currentPoint[1]
    self.currentPoint = point
    if event.Dragging():
      #self.SetToolTip ( None )
      for shape in self.getSelectedShapes():
        # ************************************
        # When drawing a new connection line,
        # it takes a while to create the connection line,
        # so when moving the cursor fast,
        # drawing with delta-x, delta-y is not sufficient
        # so here positioning to the absolute cursor position is done
        # ************************************
        if isinstance ( shape, Connection_Line ):
          shape.MoveTo ( point[0], point[1] )
        else:
          shape.move ( dx, dy )
      self.Refresh ()

    # ALWAYS hints !!
    if abs(dx) + abs(dy) < 10 :
      for shape in self.diagram.shapes :  # + self.nodes:
        if not ( isinstance ( shape, Connection_Line ) ) :
          hit, IO = shape.HitTest_Extra ( point[0], point[1] )
          if hit :
            try:
              if IO == 0 :
                line = shape.Parent.Description
              elif IO > 0 :
                input = shape.Parent.Inputs [IO]
                line = 'Input: ' + input[0] + ',  '
                line = line + PG.TIO_NAMES [ input[1] ] + ',  '
                if not ( input[2] ) : line = line + 'Not '
                line = line + 'Required'
                if len ( input ) > 3 :
                  line = line + '\n' + input[3]
              else :
                output = shape.Parent.Outputs [ abs(IO) ]
                line = 'Output: ' + output[0] + ',  '
                line = line + PG.TIO_NAMES [ output[1] ]
                # description need not to be present
                if len ( output ) > 2 :
                  line = line + '\n' + output[2]

              self.SetToolTipString ( line )
              return
            except :
              pass
    self.SetToolTip ( None )

  # *********************************************************
  # *********************************************************
  def SetDiagram ( self, diagram ) :
    self.diagram = diagram

  # ************************************
  # ************************************
  def Find_Shape_By_Name ( self, name ) :
    for item in self.diagram.shapes :
      if item.Connectable :
        if item.Parent.Name == name :
          return item
    return None

  # ************************************
  # Look up all items under the cursor
  # ************************************
  def Get_Current_Shapes ( self, event ):
    # get coordinate of click in our coordinate system
    point = self.getEventCoordinates ( event )
    self.currentPoint = point
    Hoover_Shapes = []
    for item in self.diagram.shapes :  # + self.nodes:
      if item.HitTest ( point[0], point[1] ) :
        Hoover_Shapes.append ( item )
    return Hoover_Shapes

  # *********************************************************
  # *********************************************************
  def getCurrentShape ( self, event ) :
    # get coordinate of click in our coordinate system
    point = self.getEventCoordinates(event)
    self.currentPoint = point
    # Look to see if an item is selected
    for item in self.nodes + self.diagram.shapes:
        if item.HitTest ( point[0], point[1] ) :
            return item
    return None

  # *********************************************************
  # *********************************************************
  def getEventCoordinates ( self, event ) :
    originX, originY = self.GetViewStart ()
    unitX, unitY = self.GetScrollPixelsPerUnit ()
    return [ round ( (event.GetX() + ( originX * unitX )) / self.scalex ),
             round ( (event.GetY() + ( originY * unitY )) / self.scaley ) ]

  # *********************************************************
  # *********************************************************
  def getSelectedShapes ( self ) :
    return self.selectedShapes

  # ************************************
  # Deselect all objects
  # ************************************
  def Deselect_All ( self ):
    del self.selectedShapes [:]
    del self.nodes [:]

  # ************************************
  # ************************************
  def select ( self, item = None ):
    if item is None:
      return self.selectedShapes

    if isinstance ( item, Node ) and \
       not ( ( len ( self.selectedShapes ) == 1 ) and
             ( isinstance ( self.selectedShapes[0], Connection_Line ) ) ):
      del self.selectedShapes [:]
      self.selectedShapes.append ( item )
      return

    if not item in self.selectedShapes:
      self.selectedShapes.append(item)
      item.OnSelect(None)
      if item.Connectable :
        self.nodes.extend( [INode(item,n,self) for n in range( 1, item.Parent.N_Inputs)] )
        self.nodes.extend( [ONode(item,n,self) for n in range( 1, item.Parent.N_Outputs)] )
      if item.Resizeable:
        if item.Scene_2D :
          self.nodes.extend( [ResizeableNode_2D(self,item,n,self) for n in range(len(item._x))] )
        else :
          self.nodes.extend( [ResizeableNode(item,n,self) for n in range(len(item._x))] )

        # in case of a not full connected connection line
        # Highlight the correct nodes for the open end
        if isinstance ( item, Connection_Line ) :
          if not ( item.input ) and item.output :
            self.Show_Outputs (
              item.output [0], item.output [0].Type_Inputs [ item.output[1] ] )
          if not ( item.output ) and item.input :
            self.Show_Inputs (
              item.input [0], item.input [0].Type_Outputs [ item.input[1] ] )

  # ************************************
  # HighLight Outputs Nodes of the correct type,
  # of a Block-object (except item)
  # ************************************
  def Show_Outputs ( self, item, type ):
    for shape in self.diagram.shapes:
      if  shape.Connectable and ( shape != item ) :
        self.nodes.extend ( [ ONode(shape,n,self) \
                              for n in range( 1, shape.Parent.N_Outputs ) \
                              if shape.Type_Outputs[n] == type ] )
      #elif isinstance ( shape, Connection_Line ):
      #  self.nodes.extend( [ ResizeableNode(shape,n,self) for n in range(len(shape.x))] )

  # ************************************
  # HighLight Input Nodes of the correct type,
  # of a Block-object (except item)
  # ************************************
  def Show_Inputs ( self, item, type ):
    for shape in self.diagram.shapes:
      if shape.Connectable and ( shape != item ):
        self.nodes.extend ( [ INode(shape,n,self) \
                              for n in range ( 1, shape.Parent.N_Inputs ) \
                              if shape.Type_Inputs[n] == type ] )
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class ShapeEvtHandler:
  def OnLeftUp ( self, event ) :
    pass
  def OnLeftDown ( self, event ) :
    pass
  def OnLeftDClick ( self, event ) :
    pass
  def OnRightUp ( self, event ) :
    pass
  def OnRightDown ( self,event ) :
    pass
  def OnRightDClick ( self, event ) :
    pass
  def OnSelect ( self, event ) :
    pass
  def OnMove ( self, event ) :
    pass
  def OnResize ( self, event ) :
    pass
  def OnConnect ( self, event ) :
    pass
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class Shape ( ShapeEvtHandler ):
  def __init__ ( self, Container_Canvas, x=[], y=[] ) :
    self.Container_Canvas = Container_Canvas
    self._x = x                 # list of x coord
    self._y = y                 # list of y coords
    self.pen = ['BLACK' , 1]    # pen color and size
    self.fill= ['RED']          # fill color
    
    self.Selectable   = False
    self.Resizeable   = False
    self.Connectable  = False
    self.Scene_2D     = False
    self.Trail        = False
    self.Trail_Corner = False

  # *********************************************************
  # returns a pen and brush to the real Shape instance
  # *********************************************************
  def draw ( self, dc ):
    dc.SetPen   ( wx.Pen ( self.pen[0], self.pen[1], wx.SOLID ) )
    dc.SetBrush ( wx.Brush ( self.fill[0], wx.SOLID ) )

  # *********************************************************
  # *********************************************************
  def move(self,x,y):
    self._x = map((lambda v: v+x), self._x)
    self._y = map((lambda v: v+y), self._y)

  # *********************************************************
  # *********************************************************
  def Copy(self):
    return copy.deepcopy(self)

  # *********************************************************
  # *********************************************************
  ##SM
  def SetBrush ( self, brush ) :
    self.fill[0] = brush.GetColour()
    #dc.SetBrush(brush) #wx.Brush(self.fill[0], wx.SOLID))

  # *********************************************************
  # *********************************************************
  def SetX ( self, x ) :
    delta = x - self._x[0]
    self._x = map ( (lambda f: f+delta), self._x)
  def GetX ( self ) :
    return self._x[0]

  # *********************************************************
  # *********************************************************
  def SetY ( self, y ) :
    delta = y - self._y[0]
    self._y = map ( (lambda f: f+delta), self._y)
  def GetY ( self ) :
    return self._y[0]

  # *********************************************************
  # *********************************************************
  def SetWidth ( self, w ) :
    self._x[1] = self._x[0] + w
  def GetWidth ( self ) :
    return self._x[1] - self._x[0]
  def SetHeight ( self, h ) :
    self._y[1] = self._y[0] + h
  def GetHeight ( self ) :
    return self._y[1] - self._y[0]

  # ************************************
  # Dummy procedures
  # ************************************
  def HitTest ( self, x, y ) :
    return False
  def HitTest_Extra (self, x, y):
    return False, 0
  def Add_Trail ( self ) :
    pass

  # ************************************
  # Get Center to determine if it's in rubberband
  # ************************************
  def Get_Center ( self ):
    x = ( self._x[0] + self._x[1] ) / 2
    y = ( self._y[0] + self._y[1] ) / 2
    return x, y
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class PointShape ( Shape ) :
  def __init__ ( self, Container_Shape, x=20, y=20, size=IO_r, type='rect' ):
    Shape.__init__ (self, Container_Shape, [x] , [y] )
    self.type=type
    self.size=size
    self.graphic = t_BaseShape ( x-size, y-size, x+size, y+size, self.type)
    self.graphic.pen = self.pen
    self.graphic.fill = self.fill

  def moveto ( self, x, y ):
    self._x = x
    self._y = y
    size = self.size
    self.graphic._x = [ x-size, x+size ]
    self.graphic._y = [ y-size, y+size ]

  def move ( self, x, y ) :
    self._x = map((lambda v: v+x), self._x)
    self._y = map((lambda v: v+y), self._y)
    self.graphic.move(x,y)

  def HitTest ( self, x, y ) :
    return self.graphic.HitTest(x,y)

  def draw ( self, dc ) :
    self.graphic.pen = self.pen
    self.graphic.fill = self.fill
    self.graphic.draw(dc)
# ***********************************************************************


# ***********************************************************************
# Nodes
# ***********************************************************************
class Node ( PointShape ) :
  def __init__ ( self, item, index, Container_Canvas, type='rect'):
    self.item  = item
    self.index = index
    self.Container_Canvas = Container_Canvas
    PointShape.__init__ ( self, Container_Canvas, type = type )

  def showProperties(self):
    self.item.showProperties
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class INode ( Node ):
  def __init__    ( self, item, index, Container_Canvas ) :
    Node.__init__ ( self, item, index, Container_Canvas, type='rect')
    self.pen  = [ 'WHITE', 2 ]
    self.fill [0] = TIO_Brush [ self.item.Type_Inputs [self.index] ].GetColour()

  def leftUp(self,items):
    if len ( items )==1 and isinstance ( items[0], Connection_Line ):
      if items[0].output is None:
        items[0].setOutput( self.item, self.index)
    self.Container_Canvas.Deselect_All ()
    #self.Container_Canvas.Refresh()

  # When dragging an input node
  def move ( self, x, y ) :
    self.Container_Canvas.Deselect_All ()

    # Create connection line
    CL = Connection_Line ( self.Container_Canvas )

    # Set the line color equal to the color of the source node
    CL.pen[0] = TIO_Brush [ self.item.Type_Inputs [self.index] ].GetColour()

    # Insert the connection line at the beginning of container
    self.Container_Canvas.diagram.shapes.insert ( 0, CL)

    # Connect the connection line to the node were drag started
    CL.setOutput ( self.item, self.index )

    # position the startpoint of the line
    CL._x[0], CL._y[0] = self.item.GetPort ( 'input', self.index )

    # Show inputs of all objects (excluding the already connected object)
    self.Container_Canvas.Show_Outputs (
      self.item, self.item.Type_Inputs [ self.index ] )

    # Make the connection line the active component
    self.Container_Canvas.select ( CL )

  def draw ( self, dc ) :
    x, y = self.item.GetPort ( 'input', self.index )
    self.moveto  ( x, y )
    PointShape.draw ( self, dc )
    #print 'drawINODE', self.index
# ***********************************************************************


# ***********************************************************************
# ONode and INode are the highlighted connections on a regular shape
# ***********************************************************************
class ONode ( Node ):
  def __init__    ( self, item, index, Container_Canvas ) :
    Node.__init__ ( self, item, index, Container_Canvas, type='circ')
    self.pen  = [ 'WHITE', 2 ]
    self.fill [0] = TIO_Brush [ self.item.Type_Outputs [self.index] ].GetColour()

  # This event happens when the mouse is gone up
  # on an output node of a regular shape
  def leftUp ( self, items ) :
    if len(items)==1 and isinstance ( items[0], Connection_Line ):
      if items[0].input is None:
        items[0].setInput ( self.item, self.index )
    self.Container_Canvas.Deselect_All ()

  def move ( self, x, y ):
    self.Container_Canvas.Deselect_All ()

    # Create connection line
    CL = Connection_Line ( self.Container_Canvas)

    # Set the line color equal to the color of the source node
    CL.pen[0] = TIO_Brush [ self.item.Type_Outputs [self.index] ].GetColour()

    # Insert the connection line at the beginning of container
    self.Container_Canvas.diagram.shapes.insert ( 0, CL)

    # Connect the connection line to the node were drag started
    CL.setInput ( self.item, self.index )

    # position the startpoint of the line
    CL._x[1], CL._y[1] = self.item.GetPort ( 'output', self.index )

    # Show inputs of all objects (excluding the already connected object)
    self.Container_Canvas.Show_Inputs (
      self.item, self.item.Type_Outputs [ self.index ] )

    # Make the connection line the active component
    self.Container_Canvas.select ( CL )

  def draw ( self, dc ):
    x, y = self.item.GetPort ( 'output', self.index )
    self.moveto ( x, y )
    PointShape.draw ( self, dc )
# ***********************************************************************



# ***********************************************************************
# Resize anchors, for all shapes, except 2D_scene
# ***********************************************************************
class ResizeableNode ( Node ):
  def __init__      ( self, item, index, Container_Canvas ):
    # if connection line, special resize anchors
    if isinstance ( item, Connection_Line ) :
      # determine the shape of the anchors
      if index == 0 :
        Node.__init__ ( self, item, index, Container_Canvas, type='circ' )
      else :
        Node.__init__ ( self, item, index, Container_Canvas, type='rect' )
      self.pen = [ 'WHITE', 2 ]
      # use the color of the line also for the fill color of anchor
      self.fill = [ item.pen[0] ]
    else : # normal resize anchors
      Node.__init__ ( self, item, index, Container_Canvas)
      self.fill = [ 'Black' ]

  def draw ( self, dc ):
    item = self.item
    index = self.index
    self.moveto ( item._x [index], item._y [index] )
    PointShape.draw ( self, dc )

  def move ( self, x, y ):
    self.item._x [ self.index ] += x
    self.item._y [ self.index ] += y
# ***********************************************************************


# ***********************************************************************
# Resize anchors, for 2D_scene
# ***********************************************************************
class ResizeableNode_2D ( PointShape ) : #Node ):
  def __init__      ( self, Canvas, item, index, Container_Canvas ):
    #class Node ( PointShape ) :
    #def __init__ ( self, item, index, Container_Canvas, type='rect'):
    self.Canvas = Canvas
    self.item  = item
    self.index = index
    self.Container_Canvas = Container_Canvas
    PointShape.__init__ ( self,  type = 'rect' )
    #Node.__init__ ( self, item, index, Container_Canvas)
    self.fill = [ 'Black' ]

  def draw ( self, dc ):
    item  = self.item
    index = self.index
    #self.moveto ( self.item.W2Sx (item._x [index]), self.item.W2Sy (item._y [index]) )
    self.moveto ( self.Canvas.W2Sx (item._x [index]), self.Canvas.W2Sy (item._y [index]) )
    PointShape.draw ( self, dc )

  def move ( self, x, y ):
    self.item._x [ self.index ] += x
    self.item._y [ self.index ] += y
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class LineShape ( Shape ) :
  def __init__ ( self, Container_Canvas, x1=20, y1=20, x2=50, y2=50):
    Shape.__init__(self, Container_Canvas, [x1,x2] ,  [y1,y2])

  def draw ( self, dc ) :
    Shape.draw ( self, dc )
    #dc.DrawLine(self._x[0], self._y[0],self._x[1], self._y[1])
    """
    y01 = self._y[0] + int ( 0.5 * abs ( self._y[0]-self._y[1] ))
    dc.DrawLine ( self._x[0], self._y[0], self._x[0], y01       )
    dc.DrawLine ( self._x[0], y01,       self._x[1], y01       )
    dc.DrawLine ( self._x[1], y01,       self._x[1], self._y[1] )
    """
    #if PG.OGL_Orientation_Hor:
    if self.Container_Canvas.Orientation_Hor:
      x01 = self._x[0] + int(abs(self._x[0] - self._x[1]) * 0.5)
      dc.DrawLine(self._x[0], self._y[0], x01, self._y[0])
      dc.DrawLine(x01, self._y[0], x01, self._y[1])
      dc.DrawLine(x01, self._y[1], self._x[1], self._y[1])
    else:
      y01 = self._y[0] + int(abs(self._y[0] - self._y[1]) * 0.5)
      dc.DrawLine(self._x[0], self._y[0],self._x[0], y01)
      dc.DrawLine(self._x[0], y01, self._x[1], y01)
      dc.DrawLine(self._x[1], y01, self._x[1], self._y[1])

  def HitTest(self, x, y):
    #print 'hittest'
    if x < min(self._x)-3:return False
    if x > max(self._x)+3:return False
    if y < min(self._y)-3:return False
    if y > max(self._y)+3:return False
        
    top= (x-self._x[0]) *(self._x[1] - self._x[0]) + (y-self._y[0])*(self._y[1]-self._y[0])
    distsqr=pow(self._x[0]-self._x[1],2)+pow(self._y[0]-self._y[1],2)
    # prevent dividing by zero !!
    if distsqr == 0 : return True
    u=float(top)/float(distsqr)
    
    newx = self._x[0] + u*(self._x[1]-self._x[0])
    newy = self._y[0] + u*(self._y[1]-self._y[0])
   
    dist=pow(pow(newx-x,2) +  pow(newy-y,2),.5)

    if dist>7: return False
    return True
# ***********************************************************************


# ***********************************************************************
# Line + 2 end-nodes,
# Created when dragging an output-node
# ***********************************************************************
class Connection_Line ( LineShape ) :
  def __init__ ( self, Container_Canvas ) :
    LineShape.__init__ ( self, Container_Canvas )
    self.Resizeable  = True
    self.Selectable  = True
    self.input       = None
    self.output      = None
    self.My_PolyLine = None

  # ************************************
  # When drawing a new connection line,
  # it takes a while to create the connection line,
  # so when moving the cursor fast,
  # drawing with delta-x, delta-y is not sufficient
  # so here positioning to the absolute cursor position is done
  # ************************************
  def MoveTo ( self, x, y ):
    if self.input :
      self._x[1] = x
      self._y[1] = y
    else :
      self._x[0] = x
      self._y[0] = y

  def setInput ( self, item, index ) :
    self.input = ( item, index )

  def setOutput ( self, item, index ) :
    self.output = ( item, index )

  def draw ( self, dc ) :
    #print 'Line',self.input,self.output
    #if PG.OGL_Orientation_Hor :
    if self.input and self.output :
      self._x[0], self._y[0] = self.input[0].GetPort  ( 'output', self.input[1]  )
      self._x[1], self._y[1] = self.output[0].GetPort ( 'input',  self.output[1] )

      # get pen and brushes
      Shape.draw ( self, dc )

      # determine the outer borders
      N1 = self.input[1]
      N2 = self.output[1]

      left_side   = -N2*5 -10 + min ( self.input[0]._x[0], self.output[0]._x[0])
      right_side  =  N2*5 +10 + max ( self.input[0]._x[1], self.output[0]._x[1])
      top_side    = -N1*5 -10 + min ( self.input[0]._y[0], self.output[0]._y[0])
      bottom_side =  N1*5 +10 + max ( self.input[0]._y[1], self.output[0]._y[1])

      # start at the output
      PolyLine = []
      PolyLine.append ( ( self._x[0], self._y[0] ) )

      if self.Container_Canvas.Orientation_Hor:
        if self._x[0] > self._x[1] :

          # from the output a little to the right
          x1 = self._x[0] + 10 + N1 * 5
          PolyLine.append ( ( x1, self._y[0] ) )

          # if output higher than input, go above
          if self._y[0] < self._y[1] :
            side = top_side
          else :
            side = bottom_side

          # line to a little above output brick
          PolyLine.append ( ( x1, side ) )

          # line to the left of both devices
          PolyLine.append ( ( left_side, side ) )

          # line downto the input
          PolyLine.append ( ( left_side, self._y[1] ) )

        else : # normal zig-zag
          # from the output a little to the right
          x1 = ( self._x[0] + self._x[1] ) / 2 + N1 * 5
          PolyLine.append ( ( x1, self._y[0] ) )

          # line up or down
          PolyLine.append ( ( x1, self._y[1] ) )

      else :  # Vertical
        if self._y[0] > self._y[1] :

          # from the output a little down
          y1 = self._y[0] + 10 + N1 * 5
          PolyLine.append ( ( self._x[0], y1 ) )

          # if output .... than input, go left
          #if self._x[0] < self._x[1] :
          if self._x[0] < self._x[1] :
            side = left_side
          else :
            side = right_side

          # line to the left of the output brick
          PolyLine.append ( ( side, y1 ) )

          # line to the left of both devices
          PolyLine.append ( ( side, top_side ) )

          # line downto the input
          PolyLine.append ( ( self._x[1], top_side ) )

        else : # normal zig-zag
          # from the output a little down
          y1 = ( self._y[0] + self._y[1] ) / 2 + N1 * 5
          PolyLine.append ( ( self._x[0], y1 ) )

          # line left or right
          PolyLine.append ( ( self._x[1], y1 ) )

      # line to last point
      PolyLine.append ( ( self._x[1] , self._y[1] ) )

      dc.DrawLines ( PolyLine )
      self.My_PolyLine = PolyLine

    else :  # not ( input and output )
      self.My_PolyLine = None
      if self.input :
        self._x[0], self._y[0] = self.input[0].GetPort ( 'output', self.input[1] )
      if self.output:
        self._x[1], self._y[1] = self.output[0].GetPort ( 'input', self.output[1] )
      LineShape.draw ( self, dc )


  def HitTest(self, x, y):
    if self.My_PolyLine :
      dist = 7
      hor = self.Container_Canvas.Orientation_Hor #True
      p1 = self.My_PolyLine [0]
      for point in self.My_PolyLine [1:] :
        p2 = point

        # this is a simple algorithm, that ignores outer corners
        # if we want to detect outer corners we'ld best use Pythagoras
        
        if hor : # horizontal line
          # test if y-distance small enough
          if abs ( p1[1] - y ) < dist :
            # test if x in range of linepiece
            if min ( p1[0], p2[0] ) < x < max ( p1[0], p2[0] ) :
              return True

        else : # vertical line
          # test if x-distance small enough
          if abs ( p1[0] - x ) < dist :
            # test if y in range of linepiece
            if min ( p1[1], p2[1] ) < y < max ( p1[1], p2[1] ) :
              return True

        p1 = p2
        hor = not ( hor )

      return False

    else : # No PolyLine
      #print 'HitLine',x,y,self._x,self._y
      LineShape.HitTest ( self, x, y )
        

# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class t_BaseShape ( Shape ) :
  def __init__ ( self, Container_Canvas, x=20, y=20, x2=90, y2=90, type='rect' ) :
    Shape.__init__ ( self, Container_Canvas, [x,x2] ,  [y,y2] )
    self.type = type

  def draw ( self, dc ) :
    Shape.draw ( self, dc )
    if self.type == 'rect' :
      # x, y, w, h
      dc.DrawRectangle(int(self._x[0]), int(self._y[0]),int(self._x[1]-self._x[0]), int(self._y[1]-self._y[0]))
    else : # 'circ'
      # x, y, r
      r = int ( self._x[1]-self._x[0] ) / 2
      dc.DrawCircle ( self._x[0]+r, self._y[0]+r, r+1 )

  def HitTest(self, x, y):
    #print 'hittest'
    if ( x < self._x[0] ) or \
       ( x > self._x[1] ) or \
       ( y < self._y[0] ) or \
       ( y > self._y[1] ) :
      return False
    else :
      return True
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class t_RubberBand_Shape ( Shape ) :
  def __init__ ( self, Container_Canvas, x1=20, y1=20, x2=90, y2=90 ):
    print x1,x2,y1,y2
    Shape.__init__ ( self, Container_Canvas, [x1,x2] ,  [y1,y2] )
    self.Selectable = True
    self.Resizeable = True

  #def leftUp ( self, items ) :
  #  print 'detremine selecteion'
    
  def draw ( self, dc ) :
    Shape.draw ( self, dc )
    dc.SetPen ( wx.Pen ( wx.RED, 4 ) )
    dc.DrawLine ( self._x[0], self._y[0], self._x[1], self._y[0] )
    dc.DrawLine ( self._x[1], self._y[0], self._x[1], self._y[1] )
    dc.DrawLine ( self._x[1], self._y[1], self._x[0], self._y[1] )
    dc.DrawLine ( self._x[0], self._y[1], self._x[0], self._y[0] )

  def HitTest(self, x, y):
    x0 = self._x[0] + self._x[1]
    dx = abs ( self._x[0] - self._x[1] )
    y0 = self._y[0] + self._y[1]
    dy = abs ( self._y[0] - self._y[1] )
    if ( 2*x < x0 - dx ) or \
       ( 2*x > x0 + dx ) or \
       ( 2*y < y0 - dy ) or \
       ( 2*y > y0 + dy ) :
      return False
    else :
      return True
# ***********************************************************************

# ***********************************************************************
# ***********************************************************************
class Rectangle ( t_BaseShape ):
  def __init__          ( self, Container_Canvas, parent, Pos = [10,10], Caption = '' ):
    t_BaseShape.__init__( self, Container_Canvas,        Pos[0], Pos[1], Pos[0]+80, Pos[1]+50 )
    self.Parent = parent
    self.Resizeable = True
    self.Selectable = True
    self.Connectable = True

    self.Type_Inputs = [ None ]
    for i in range ( 1, self.Parent.N_Inputs ) :
      #self.Type_Inputs.append ( self.Parent.Inputs [i+1][1] )
      self.Type_Inputs.append ( self.Parent.Inputs [i][1] )
    self.Type_Outputs = [ None ]
    for i in range ( 1, self.Parent.N_Outputs ) :
      #self.Type_Outputs.append ( self.Parent.Outputs [i+1][1] )
      self.Type_Outputs.append ( self.Parent.Outputs [i][1] )

    global temp_dev_nr
    if Caption:
      self.Caption = Caption
    else :
      self.Caption='Block ' + str ( temp_dev_nr )
    temp_dev_nr += 1

  # ************************************
  # Special hittest, that also detects IO-pins
  # ************************************
  def HitTest_Extra (self, x, y):
    #if PG.OGL_Orientation_Hor :
    if self.Container_Canvas.Orientation_Hor:
      return self.HitTest_Extra_Hor ( x, y )
    else :
      return self.HitTest_Extra_Ver ( x, y )

  def HitTest_Extra_Hor (self, x, y):
    if ( y > self._y[0] ) and ( y < self._y[1] ) :
      # Test input pins
      if abs ( x - self._x[0]) <= IO_r :
        for i in range ( 1, self.Parent.N_Inputs ) :
          xi, yi  = self.GetPort ( 'input', i)
          if abs ( y - yi ) <= IO_r :
            return True, i
      # Test output pins
      elif abs ( x - self._x[1]) <= IO_r :
        for i in range ( 1, self.Parent.N_Outputs ) :
          xi, yi  = self.GetPort ( 'output', i)
          if abs ( y - yi ) <= IO_r :
            return True, -(i)
      # Test body
      elif ( x > self._x[0] ) and ( x < self._x[1] ) :
        return True, 0
    return False, 0

  def HitTest_Extra_Ver (self, x, y):
    if ( x > self._x[0] ) and ( x < self._x[1] ) :
      #print y, self._y[0],IO_r,abs ( y - self._y[0]),self.N_inputs
      # Test input pins
      if abs ( y - self._y[0]) <= IO_r :
        for i in range ( 1, self.Parent.N_Inputs ) :
          xi, yi  = self.GetPort ( 'input', i)
          if abs ( x - xi ) <= IO_r :
            #return True, i+1
            return True, i
      # Test output pins
      elif abs ( y - self._y[1]) <= IO_r :
        for i in range ( 1, self.Parent.N_Outputs ) :
          xi, yi  = self.GetPort ( 'output', i)
          if abs ( x - xi ) <= IO_r :
            #return True, -(i+1)
            return True, -(i)
      # Test body
      elif ( y > self._y[0] ) and ( y < self._y[1] ) :
        return True, 0
    return False, 0


  # ************************************
  # Calculates the x,y position of the centre of the selected io-port
  # ************************************
  def GetPort ( self, type, num ):
    #if PG.OGL_Orientation_Hor :
    if self.Container_Canvas.Orientation_Hor:
      return self.GetPort_Hor ( type, num )
    else :
      return self.GetPort_Ver ( type, num )

  def GetPort_Hor ( self, type, num ):
    if type=='input':
      div = float ( self.Parent.N_Inputs ) #+ 1.0 )
      x = self._x[0]
    elif type=='output':
      div = float ( self.Parent.N_Outputs ) #+ 1.0 )
      x = self._x[1]
    #//EVEN
    num -=1

    dy = float ( self._y[1] - self._y[0] ) / div
    y  = self._y[0] + dy * (num+1)
    return(x,y)
  
  def GetPort_Ver ( self, type, num ):
    if type=='input':
      div = float ( self.Parent.N_Inputs ) #+ 1.0 )
      y = self._y[0]
    elif type=='output':
      div = float ( self.Parent.N_Outputs ) #+ 1.0 )
      y = self._y[1]
    #//EVEN
    num -=1

    dx = float ( self._x[1] - self._x[0] ) / div
    x  = self._x[0] + dx * (num+1)
    return(x,y)

  def draw ( self, dc ):
    #self.pen = ['RED' , 3]    # pen color and size

    t_BaseShape.draw ( self, dc )
    w,h =  dc.GetTextExtent ( self.Caption )
    mx = int ( ( self._x[0] + self._x[1] ) / 2.0 ) - int ( w / 2.0 )
    my = int ( ( self._y[0] + self._y[1] ) / 2.0 ) - int ( h / 2.0 )
    dc.DrawText ( self.Caption, mx, my )

    # draw inputs and outputs
    dc.SetPen ( wx.Pen ( wx.BLACK ) )
    for i in range ( 1, self.Parent.N_Inputs ) :
      x,y = self.GetPort ( 'input', i)
      dc.SetBrush ( TIO_Brush [ self.Type_Inputs [i] ])
      dc.DrawRectangle ( x-IO_r, y-IO_r, 2*IO_r, 2*IO_r )
      # if input is required, draw a small flag-line
      if self.Parent.Inputs [i] [2] :
        #if PG.OGL_Orientation_Hor :
        if self.Container_Canvas.Orientation_Hor:
          dc.DrawLine ( x-IO_r,   y-IO_r,
                        x-IO_r-7, y-IO_r)
        else :
          dc.DrawLine ( x-IO_r, y-IO_r,
                        x-IO_r, y-IO_r-7)

    r = 5
    for i in range ( 1, self.Parent.N_Outputs ) :
      x,y = self.GetPort ( 'output', i)
      dc.SetBrush ( TIO_Brush [ self.Type_Outputs [i] ])
      dc.DrawCircle ( x, y, r )

  def OnLeftDown(self,event):
    #if isinstance(self,Block) and event.ControlDown():
    if event.ControlDown():
      d=wx.TextEntryDialog(None,'Block Caption',defaultValue=self.Caption,style=wx.OK)
      d.ShowModal()
      self.Caption = d.GetValue()

  def OnRightDown(self,event):
    print 'right down'
# ***********************************************************************



# ***********************************************************************
# Dummy brick for DB_Table_Shape
# ***********************************************************************
class _dummy_brick ( object ) :
  def __init__ ( self, N ) :
    self.N_Inputs  = N
    self.N_Outputs = N
    self.Description = 'DataBase Table ...'
    # Inputs = ...
    # Outputs = ...
# ***********************************************************************


# ***********************************************************************
# For automatic table positioning
# ***********************************************************************
_Pos_DB_Table_Shape = [ 10, 10 ]
# ***********************************************************************


# ***********************************************************************
# ***********************************************************************
class DB_Table_Shape ( Shape ) : #t_BaseShape ):

  def __init__          ( self, Container_Canvas, field_list, Pos = -1, Caption = '' ):
    # Auto positioning
    if Pos == -1 :
      Pos = _Pos_DB_Table_Shape
      _Pos_DB_Table_Shape [1] +=  20
      
    # Create the shape
    Shape.__init__ ( self, Container_Canvas, [ Pos[0], Pos[0]+80 ] ,  [ Pos[1], Pos[1]+ 50 ] )
    self.type = 'rect'

    self.init = False
    self.List = field_list

    self.N = len ( self.List )
    self.Parent = _dummy_brick ( self.N )
    self.Resizeable = False 
    self.Selectable = True
    self.Connectable = True
    
    # Define the IO-types, needed for connections
    self.Type_Inputs = []
    self.Type_Outputs = []
    for i in range ( self.N ) :
      self.Type_Inputs.append  ( 8 )
      self.Type_Outputs.append ( 8 )

    global temp_dev_nr
    temp_dev_nr += 1


  # ************************************
  # Special hittest, that also detects IO-pins
  # ************************************
  def HitTest_Extra (self, x, y):
    if ( y > self._y[0] ) and ( y < self._y[1] ) :
      # Test input pins
      if abs ( x - self._x[0]) <= IO_r :
        for i in range ( 1, self.N ) :
          xi, yi  = self.GetPort ( 'input', i)
          if abs ( y - yi ) <= IO_r :
            return True, i
      # Test output pins
      elif abs ( x - self._x[1]) <= IO_r :
        for i in range ( 1, self.N ) :
          xi, yi  = self.GetPort ( 'output', i)
          if abs ( y - yi ) <= IO_r :
            return True, -(i)
      # Test body
      elif ( x > self._x[0] ) and ( x < self._x[1] ) :
        return True, 0
    return False, 0


  # ************************************
  # Calculates the x,y position of the centre of the selected io-port
  # ************************************
  def GetPort ( self, type, num ):
    if type=='input':
      div = float ( len ( self.List ) ) 
      x = self._x[0]
    elif type=='output':
      div = float ( len ( self.List ) ) 
      x = self._x[1]
      
    dy = float ( self._y[1] - self._y[0] ) / div
    y  = int ( self._y[0] + dy * ( num + 0.5 ) )
    return ( x, y )


  # ************************************
  # ************************************
  def HitTest ( self, x, y ) :
    #print 'hittest'
    if ( x < self._x[0] ) or \
       ( x > self._x[1] ) or \
       ( y < self._y[0] ) or \
       ( y > self._y[1] ) :
      return False
    else :
      return True

  # ************************************
  # ************************************
  def draw ( self, dc ):
    Shape.draw ( self, dc )

    w,h =  dc.GetTextExtent ( self.List[0] )
    if not ( self.init ) :
      self.init = True
      h *= len ( self.List )
      self._x[1] = self._x[0] + w + 10
      self._y[1] = self._y[0] + h

    c = 200
    dc.SetBrush ( wx.Brush ( ( c, c, c ) ) )
    dc.DrawRectangle ( int( self._x[0]), int(self._y[0] + h ),
                       int( self._x[1] - self._x[0] ),
                       int( self._y[1] - self._y[0] - h ))

    dc.SetBrush ( TIO_Brush [ self.Type_Inputs [0] ])
    dc.DrawRectangle ( int( self._x[0]), int(self._y[0] ),
                       int( self._x[1] - self._x[0] ),
                       int( h ) )

    mx = 5 + int ( self._x[0] )
    delta = int ( ( self._y[1] - self._y[0] ) / self.N )

    # draw table name
    dc.DrawText ( self.List[0], mx, self._y[0] )
    # fields some further to the right
    mx += 5
    r = 5
    for i, item in enumerate ( self.List [1:] ) :
      my = int ( self._y[0] + (i+1) * delta )
      dc.DrawText ( item, mx, my )

      x,y = self.GetPort ( 'input', i+1 )
      dc.DrawRectangle ( x-IO_r, y-IO_r, 2*IO_r, 2*IO_r )

      x,y = self.GetPort ( 'output', i+1 )
      dc.DrawCircle ( x, y, r )

# ***********************************************************************


