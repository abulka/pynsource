# -*- coding: iso-8859-1 -*-#
#!/usr/bin/env python2.4
"""

A start to create a wine rack designer with FloatCanvas

"""

import wx
import wx.lib.imageutils as imgutil

from amara import binderytools

#ver = 'local'
ver = 'installed'

if ver == 'installed': ## import the installed version
    from wx.lib.floatcanvas import NavCanvas, Resources
    from wx.lib.floatcanvas import FloatCanvas as FC
    print("using installed version:", wx.lib.floatcanvas.__version__)
elif ver == 'local':
    ## import a local version
    import sys
    sys.path.append("../")
    from floatcanvas import NavCanvas,  Resources
    from floatcanvas import FloatCanvas as FC

import numpy as N

import myimages

# xml - using amara
def ucode(value):
    if isinstance(value, str): 
        return str(value.strip(), 'iso-8859-1')
    else:
        return str(str(value).strip(), 'iso-8859-1')

def addElement(doc, element, name):
    return element.xml_append(doc.xml_create_element(name))

def addValueElement(doc, element, name, value):
    return element.xml_append(doc.xml_create_element(name, content=value))


class ShapeMixin:
    def __init__(self):
        self.RackItemId = 0
        self.ShapeTip = ''

    def Save(self, xmlDoc):
        if isinstance(self, FC.Rectangle):
            klass = addElement(xmlDoc, xmlDoc.shapes,
                                ucode('RectangleShape'))
            addValueElement(xmlDoc, klass, 'width',
                                    ucode(self.WH[0]))
            addValueElement(xmlDoc, klass, 'height',
                                ucode(self.WH[1]))
            addValueElement(xmlDoc, klass, 'x',
                                    ucode(self.XY[0]))
            addValueElement(xmlDoc, klass, 'y',
                                    ucode(self.XY[1]))

        else:
            klass = addElement(xmlDoc, xmlDoc.shapes,
                                ucode('PolygonShape'))
            shapePoints = self.Points.tolist()
            points = addElement(xmlDoc, klass, 'points')
            for wxp in shapePoints:
                points.xml_append_fragment('<point><x>%i</x><y>%i</y></point>'%(wxp[0], wxp[1]))
                
        addValueElement(xmlDoc, klass, 'rackitemid',
                                ucode(self.RackItemId))


class TriangleShape(FC.Polygon, ShapeMixin):
    def __init__(self, Points, fillcolor, rackitemid, shapetip):
        FC.Polygon.__init__(self, Points,
                                  LineColor = "Black",
                                  LineStyle = "Solid",
                                  LineWidth = 2,
                                  FillColor = fillcolor,
                                  FillStyle = "Solid")
        ShapeMixin.__init__(self)
        self.RackItemId = rackitemid
        self.ShapeTip = shapetip


class RectangleShape(FC.Rectangle, ShapeMixin):
    def __init__(self, XY, WH, fillcolor, rackitemid, shapetip):
        FC.Rectangle.__init__(self, XY,
                            WH,
                            LineColor = "Black",
                            LineStyle = "Solid",
                            LineWidth = 2,
                            FillColor = fillcolor,
                            FillStyle = "Solid")
        ShapeMixin.__init__(self)
        self.RackItemId = rackitemid
        self.ShapeTip = shapetip


class DrawFrame(wx.Frame):

    """
    A frame used for the FloatCanvas Demo

    """

    def __init__(self,parent, id,title,position,size):
        wx.Frame.__init__(self,parent, id,title,position, size)

        self.Bind(wx.EVT_CLOSE, self.OnRackDesignerClose)
        self.CreateStatusBar()
        self.GetStatusBar().SetFieldsCount(2)
        # Add the Canvas
        self.NavCanvas = NavCanvas.NavCanvas(self,-1,(500,500),
                                          ProjectionFun = None,
                                          Debug = 0,
                                          BackgroundColor = "DARK SLATE BLUE",
                                          )
        self.Canvas = self.NavCanvas.Canvas

        self.Canvas.Bind(FC.EVT_MOTION, self.OnMove ) 
        self.Canvas.Bind(FC.EVT_LEFT_UP, self.OnLeftUp ) 

##        # add a grid for snap:
##        Grid = FC.DotGrid( (10, 10), Size=1, Color="Red")
##        self.Canvas.GridUnder = Grid

        self.MoveShape = None
        self.Moving = False
        self.dataToSave = False
        self.shapes = []
        self.Resizing = False
        self.ResizeRect = None
        self.RL = False
        self.UP = False
        self.SelectedObject = None

        self.Show(True)
        self.Canvas.ZoomToBB()
        
        self.UpdateToolBar()
        
        self.LoadFromXML()
        
        self.ResetSelections()

        return None
    
    def UpdateToolBar(self):
        tb = self.NavCanvas.ToolBar
        
        # Add triangle 2
        self.wxId_TBAddTri2 =wx.NewId()
        img = myimages.getwrTriangle2Image()
        imgGO = myimages.getwrTriangle2Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        tb.InsertLabelTool(pos=0, label = 'Add triangle 2',
                bitmap = bmp,
                bmpDisabled = bmpDA,
                id = self.wxId_TBAddTri2,
                longHelp = '',
                shortHelp = '')
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri2, id=self.wxId_TBAddTri2)

        # Add triangle 1
        self.wxId_TBAddTri1 =wx.NewId()
        img = myimages.getwrTriangle1Image()
        imgGO = myimages.getwrTriangle1Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        tb.InsertLabelTool(pos=0, label = 'Add triangle 1',
                bitmap = bmp,
                bmpDisabled = bmpDA,
                id = self.wxId_TBAddTri1,
                longHelp = '',
                shortHelp = '')
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri1, id=self.wxId_TBAddTri1)

        # Add rectangle
        self.wxId_TBAddRect =wx.NewId()
        img = myimages.getwrRectangleImage()
        imgGO = myimages.getwrRectangleImage()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        tb.InsertLabelTool(pos=0, label = 'Add rectangle',
                bitmap = bmp,
                bmpDisabled = bmpDA,
                id = self.wxId_TBAddRect,
                longHelp = '',
                shortHelp = '')
        self.Bind(wx.EVT_TOOL, self.OnTBAddRect, id=self.wxId_TBAddRect)

        # delete
        self.wxId_TBDelete =wx.NewId()
        img = myimages.getwrDeleteImage()
        imgGO = myimages.getwrDeleteImage()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        tb.InsertLabelTool(pos=0, label = 'Delete shape',
                bitmap = bmp,
                bmpDisabled = bmpDA,
                id = self.wxId_TBDelete,
                longHelp = '',
                shortHelp = '')
        self.Bind(wx.EVT_TOOL, self.OnTBDelete, id=self.wxId_TBDelete)
        
        tb.AddSeparator()
        
        # save
        self.wxId_TBSave =wx.NewId()
        img = myimages.getsaveImage()
        imgGO = myimages.getsaveImage()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        tb.InsertLabelTool(pos=0, label = 'Save rack design',
                bitmap = bmp,
                bmpDisabled = bmpDA,
                id = self.wxId_TBSave,
                longHelp = '',
                shortHelp = '')
        self.Bind(wx.EVT_TOOL, self.OnTBSave, id=self.wxId_TBSave)

        tb.AddSeparator()
        
        tb.Realize()

    def OnTBAddRect(self, event):
        rackitemid, shapetip = self.GetRackItem()
        if rackitemid != 0:
            XY = (0, 0)
            WH = (100, 100)
            shape = RectangleShape(XY, WH, "Red", rackitemid, shapetip)
            self.Canvas.AddObject(shape)
            shape.Bind(FC.EVT_FC_LEFT_DOWN, self.MoveRect)
            self.Canvas.Draw()
            self.dataToSave = True
            self.shapes.append(shape)
    
    def OnTBAddTri1(self, event):
        rackitemid, shapetip = self.GetRackItem()
        if rackitemid != 0:
            Points = N.array(((0 , 100),
                             (100, 0),
                             (0, 0)),
                             N.float_)

            self.AddTriShape(TriangleShape(Points, "Red", rackitemid, shapetip))
            
    def OnTBAddTri2(self, event):
        rackitemid, shapetip = self.GetRackItem()
        if rackitemid != 0:
            Points = N.array(((0 , -100),
                             (-100, 0),
                             (0, 0)),
                             N.float_)

            self.AddTriShape(TriangleShape(Points, "Red", rackitemid, shapetip))

    def AddTriShape(self, shape):
        self.Canvas.AddObject(shape)
        shape.Bind(FC.EVT_FC_LEFT_DOWN, self.MovePoly)
        self.Canvas.Draw()
        self.dataToSave = True
        self.shapes.append(shape)
    
    def MoveRect(self, object):
        if not self.Moving:
            self.Moving = True
            self.SelectedObject = object
            self.StartPoint = object.HitCoordsPixel
            self.StartShape = self.Canvas.WorldToPixel(object.XY)
            self.RectWH = self.Canvas.ScaleWorldToPixel(object.WH)
            self.MoveShape = None
           
        self.SelectRect(object)    

    def MovePoly(self, object):
        self.DeSelectRect()
        if not self.Moving:
            self.Moving = True
            self.SelectedObject = object
            self.StartPoint = object.HitCoordsPixel
            self.StartShape = self.Canvas.WorldToPixel(object.Points)
            self.MoveShape = None

    def OnMove(self, event):
        """
        Updates the status bar with the world coordinates

        And moves the shape if it is clicked on

        """
        self.SetStatusText("%.4f, %.4f"%tuple(event.Coords))

        if self.Resizing:
            if isinstance(self.SelectedObject, RectangleShape):
                diff = self.SelectedObject.XY - event.GetCoords()
                if self.UD:
                    diff[0] = 0
                elif self.RL:
                    diff[1] = 0
                
                w, h = self.Canvas.ScaleWorldToPixel(self.SelectedObject.WH + diff)
                x, y = self.Canvas.WorldToPixel(self.SelectedObject.XY - diff)
                
                dc = wx.ClientDC(self.Canvas)
                PixelCoords = event.GetPosition()
                dc.SetPen(wx.Pen('WHITE', 2, wx.SHORT_DASH))
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.SetLogicalFunction(wx.XOR)
    
                if self.ResizeRect:
                    dc.DrawRectangle(*self.ResizeRect)
                self.ResizeRect = (x,y,w,h)
                dc.DrawRectangle(*self.ResizeRect)
                
        elif self.Moving:
            self.PointSelected = False
            self.DeSelectRect()
            dxy = event.GetPosition() - self.StartPoint
            # Draw the Moving shape:
            dc = wx.ClientDC(self.Canvas)
            dc.SetPen(wx.Pen('WHITE', 2, wx.SHORT_DASH))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.SetLogicalFunction(wx.XOR)
            if self.MoveShape is not None:
                if isinstance(self.SelectedObject, FC.Rectangle):
                    x, y = self.MoveShape
                    w, h = self.RectWH
                    dc.DrawRectangle(x, y, w, h)
                else:
                    dc.DrawPolygon(self.MoveShape)
            self.MoveShape = self.StartShape + dxy
            if isinstance(self.SelectedObject, FC.Rectangle):
                x, y = self.MoveShape
                w, h = self.RectWH
                dc.DrawRectangle(x, y, w, h)
            else:
                dc.DrawPolygon(self.MoveShape)

    def ResetSelections(self):
        self.SelectedRect = None
        self.SelectedRectOrig = None
        self.RL = False
        self.UP = False
        
    def DeSelectRect(self):
        Canvas = self.Canvas
        if hasattr(self.SelectedRect, 'HasChanged'):
            if self.SelectedRect.HasChanged:
                self.Canvas.Draw(Force = True)
            Canvas.RemoveObject(self.SelectedRect)
            Canvas.RemoveObject(self.HandleRL)
            Canvas.RemoveObject(self.HandleUD)
            self.ResetSelections()
    
    def SelectRect(self, Object):
        Canvas = self.Canvas
        if Object is self.SelectedRectOrig:
            pass
        else:
            if self.SelectedRect:
                self.DeSelectRect()

            self.SelectedRectOrig = Object
            self.SelectedRect = Canvas.AddRectangle(Object.XY, Object.WH,
                                                  LineWidth = 2,
                                                  LineColor = "Yellow",
                                                  FillColor = None,
                                                  InForeground = True)
            self.SelectedRect.HasChanged = False
            # draw handles for resizing
            rlPos = Object.XY + Object.WH
            udPos = Object.XY + Object.WH
            self.HandleRL = self.Canvas.AddBitmap(Resources.getMoveRLCursorBitmap(), rlPos, Position='cc')
            self.HandleUD = self.Canvas.AddBitmap(Resources.getMoveUDCursorBitmap(), udPos, Position='cc')
    
            self.SetHandles(Object)
            
            self.HandleRL.Bind(FC.EVT_FC_LEFT_DOWN, self.HandleSizeRL)
            self.HandleUD.Bind(FC.EVT_FC_LEFT_DOWN, self.HandleSizeUD)
            
            Canvas.Draw()

    def SetHandles(self, object):
        ((x,y),(w,h)) = object.XY, object.WH

        y2 = y + h/2
        self.HandleRL.SetPoint((x, y2))

        x += w
        x3 = x - w/2
        self.HandleUD.SetPoint((x3,y))

    def HandleSizeRL(self, event=None):
        if not self.Resizing:
            self.Resizing = True
            self.RL = True
            self.UD = False

    def HandleSizeUD(self, event=None):
        if not self.Resizing:
            self.Resizing = True
            self.UD = True
            self.RL = False

    def OnLeftUp(self, event):
        if self.Moving:
            self.Moving = False
            if self.MoveShape is not None:
                dxy = event.GetPosition() - self.StartPoint
                dxy = self.Canvas.ScalePixelToWorld(dxy)
##                dxy = self.Snap(dxy)
                self.SelectedObject.Move(dxy)
                self.MoveShape = None

            self.Canvas.Draw(True)
        
            try:
                shapeTip = self.SelectedObject.GetShapeTip()
            except:
                shapeTip = ''
            self.SetStatusText(shapeTip, 1)
            
        elif self.Resizing:
            self.Resizing = False
            self.ResizeRect = None
            diff = self.SelectedRect.XY - event.GetCoords()

            if self.UD:
                diff[0] = 0
                newWH = self.SelectedRect.WH + diff
            else:
                diff[1] = 0
                newWH = self.SelectedRect.WH + diff
            self.SelectedRectOrig.XY -= diff
            self.SelectedRectOrig.WH = newWH
            self.PointSelected = False
            self.SelectedRect.HasChanged = True
            self.DeSelectRect()
            self.Canvas.Draw(True)

    def Snap(self, point):
        """Borrowed from wx.lib.ogl
        'Snaps' the coordinate to the nearest grid position
        A numpy version
        
        Currently not used as I can not make triangles and rectangles line up nicely
        """
        gridSpacing = 10.0
        return (point/gridSpacing).round()*gridSpacing

    def GetRackItem(self):
        # remove return and adjust to your db the following
        return (wx.NewId(), 'some tip information')

        # get information about a rack item
        bins = []
        binsid = []
        where = 'fk_winerackid = %i' % self.dbItemRack.winerackid
        orderby = 'binno, subbinno'
        dbItem = wx.GetApp().Getds().selectByClauses(beans.winerackb, 
                                                     where=where,
                                                     orderby=orderby).fetchall()
        for bin in dbItem:
            shapetip = 'Bin no: %i, Sub-bin no: %i, Capacity: %i, Description: %s' % (bin.binno,
                                                                        bin.subbinno,
                                                                        bin.capacity,
                                                                        bin.description)
            bins.append(shapetip)
            binsid.append(bin.winerackbid)
            
        dlg = wx.SingleChoiceDialog(self, 'Double click or select and click OK',
                                          'Select the bin number', bins)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.dataToSave = True
                return (binsid[dlg.GetSelection()], dlg.GetStringSelection())
            else:
                return (0, '')
        finally:
            dlg.Destroy()

    def OnTBSave(self, event):
        if len(self.shapes) > 0:
            # create xml and write to db
            doc_header = '''<shapes></shapes>'''
            xmlDoc = binderytools.bind_string(doc_header)
            for shape in self.shapes:
                shape.Save(xmlDoc)
    
            #self.dbItemRack.shapeinfo = xmlDoc.xml(indent=u'yes')
            # adjust above to your db and remove below
            print(xmlDoc.xml(indent='yes'))
        else:
            pass
            # adjust to your db
            #self.dbItemRack.shapeinfo = ''
        
        # adjust to your db
        #wx.GetApp().Getds().commit()
        self.dataToSave = False

    def OnTBDelete(self, event):
        self.DelShape()
        self.dataToSave = True

    def DelShape(self):
        if self.SelectedObject:
            self.Canvas.RemoveObject(self.SelectedObject)
            self.shapes.remove(self.SelectedObject)
            self.Canvas.Draw()
            self.SelectedObject = None
        
    def OnRackDesignerClose(self, event):
        if self.dataToSave:
            dlgText = 'You entered data which is not saved! Click on "No" to return and save it\n\nor on "Yes" to quit and lose it!'
            dlgName = 'Unsaved data warning!'
            
            try:
                dlg =wx.MessageDialog(self, dlgText, dlgName,
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        
                if dlg.ShowModal() == wx.ID_YES:
                    # roll back database - adjust to your db
                    #wx.GetApp().Getds().rollback()
                    pass
                else:
                    return
            finally:
                dlg.Destroy()
        else:
            # roll back database - adjust to your db
            #wx.GetApp().Getds().rollback()
            pass
        
        self.MakeModal(False)
        event.Skip()

    def LoadFromXML(self):
        # create xml and write to db
        doc_header = '''<shapes>
  <RectangleShape>
    <width>100.0</width>
    <height>100.0</height>
    <x>170.0</x>
    <y>96.0</y>
    <rackitemid>113</rackitemid>
  </RectangleShape>
  <PolygonShape>
    <points>
      <point>
        <x>-122</x>
        <y>196</y>
      </point>
      <point>
        <x>-22</x>
        <y>96</y>
      </point>
      <point>
        <x>-122</x>
        <y>96</y>
      </point>
    </points>
    <rackitemid>114</rackitemid>
  </PolygonShape>
  <PolygonShape>
    <points>
      <point>
        <x>-124</x>
        <y>96</y>
      </point>
      <point>
        <x>-224</x>
        <y>196</y>
      </point>
      <point>
        <x>-124</x>
        <y>196</y>
      </point>
    </points>
    <rackitemid>115</rackitemid>
  </PolygonShape>
</shapes>'''
        xmlDoc = binderytools.bind_string(doc_header)
        if hasattr(xmlDoc.shapes, 'RectangleShape'):
            for shape in xmlDoc.shapes.RectangleShape:
                x = float(str(shape.x))
                y = float(str(shape.y))
                w = float(str(shape.width))
                h = float(str(shape.height))
                rid = (str(shape.rackitemid))
                if rid != 0:
                    shapetip = 'some dummy info for rectangle which normally comes from db'
                else:
                    shapetipe = ''
    
                shape = RectangleShape((x, y), (w, h), "Red", rid, shapetip)
                self.Canvas.AddObject(shape)
                shape.Bind(FC.EVT_FC_LEFT_DOWN, self.MoveRect)
                self.dataToSave = True
                self.shapes.append(shape)

        if hasattr(xmlDoc.shapes, 'PolygonShape'):
            for shape in xmlDoc.shapes.PolygonShape:
                shapePoints = []
                for point in shape.points.point:
                    shapePoints.append((float(str(point.x)), 
                                        float(str(point.y))))
                Points = N.array(shapePoints,
                                 N.float_)
                                 
                rid = (str(shape.rackitemid))
                if rid != 0:
                    shapetip = 'some dummy info for triangle which normally comes from db'
                else:
                    shapetip = ''

                shape = TriangleShape(Points, "Red", rid, shapetip)
                self.Canvas.AddObject(shape)
                shape.Bind(FC.EVT_FC_LEFT_DOWN, self.MovePoly)
                self.dataToSave = True
                self.shapes.append(shape)
        
        self.Canvas.Draw()


app = wx.PySimpleApp()
DrawFrame(None, -1, "A start for Wine Rack designer using FloatCanvas", wx.DefaultPosition, (700,700) )
app.MainLoop()
