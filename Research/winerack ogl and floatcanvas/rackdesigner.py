# -*- coding: iso-8859-1 -*-#
# -----------------------------------------------------------------------------
# Name:        rackdesigner.py
# Purpose:     Design custom wine rack layout
#
#              Heavily based on the wxPython wx.lib.ogl demo
#
# Created:     2006/06/16
# RCS-ID:      $Id: rackdesigner.py,v 1.6 2006/07/19 16:54:51 wbruhin Exp $
# -----------------------------------------------------------------------------
# Boa:Frame:RackDesigner
import os

import wx
import wx.lib.imageutils as imgutil
import wx.lib.ogl as ogl

from amara import binderytools

import myimages


def create(parent):
    return RackDesigner(parent)


[wxID_RACKDESIGNER, wxID_RACKDESIGNERSTATUSBAR1, wxID_RACKDESIGNERTB] = [
    wx.NewId() for _init_ctrls in range(3)
]

# xml - using amara
def ucode(value):
    if isinstance(value, str):
        return str(value.strip(), "iso-8859-1")
    else:
        return str(str(value).strip(), "iso-8859-1")


def addElement(doc, element, name):
    return element.xml_append(doc.xml_create_element(name))


def addValueElement(doc, element, name, value):
    return element.xml_append(doc.xml_create_element(name, content=value))


class ShapeMixin:
    def __init__(self):
        self._rackItemId = 0
        self._shapeTip = ""

    def SetRackItemId(self, id):
        self._rackItemId = id

    def GetRackItemId(self):
        return self._rackItemId

    def SetShapeTip(self, tip):
        self._shapeTip = tip

    def GetShapeTip(self):
        return self._shapeTip

    def Save(self, xmlDoc):
        if isinstance(self, ogl.RectangleShape):
            klass = addElement(xmlDoc, xmlDoc.shapes, ucode("RectangleShape"))
            addValueElement(xmlDoc, klass, "width", ucode(self.GetWidth()))
            addValueElement(xmlDoc, klass, "height", ucode(self.GetHeight()))

        else:
            klass = addElement(xmlDoc, xmlDoc.shapes, ucode("PolygonShape"))
            shapePoints = self.GetPoints()
            points = addElement(xmlDoc, klass, "points")
            for wxp in shapePoints:
                points.xml_append_fragment("<point><x>%i</x><y>%i</y></point>" % (wxp.x, wxp.y))

            addValueElement(xmlDoc, klass, "width", ucode(self.GetOriginalWidth()))
            addValueElement(xmlDoc, klass, "height", ucode(self.GetOriginalHeight()))

        addValueElement(xmlDoc, klass, "x", ucode(self.GetX()))
        addValueElement(xmlDoc, klass, "y", ucode(self.GetY()))
        addValueElement(xmlDoc, klass, "rackitemid", ucode(self.GetRackItemId()))


class TriangleShape1(ogl.PolygonShape, ShapeMixin):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        ShapeMixin.__init__(self)
        if w == 0.0:
            w = 50.0
        if h == 0.0:
            h = 50.0

        points = [(0.0, -h / 2.0), (w / 2.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        print(points)

        self.Create(points)


class TriangleShape2(ogl.PolygonShape, ShapeMixin):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        ShapeMixin.__init__(self)
        if w == 0.0:
            w = 50.0
        if h == 0.0:
            h = 50.0

        points = [(0.0, h / 2.0), (-w / 2.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        self.Create(points)


class TriangleShape3(ogl.PolygonShape, ShapeMixin):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        ShapeMixin.__init__(self)
        if w == 0.0:
            w = 50.0
        if h == 0.0:
            h = 50.0

        points = [(0.0, w / 2.0), (h / 2.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        self.Create(points)


class TriangleShape4(ogl.PolygonShape, ShapeMixin):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        ShapeMixin.__init__(self)
        if w == 0.0:
            w = 50.0
        if h == 0.0:
            h = 50.0

        points = [(0.0, -w / 2.0), (-h / 2.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        self.Create(points)


class TriangleShape5(ogl.PolygonShape, ShapeMixin):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        ShapeMixin.__init__(self)
        if w == 0.0:
            w = 50.0
        if h == 0.0:
            h = 50.0

        points = [(h / 4.0, w / 4.0), (-h / 4.0, w / 4.0), (0.0, 0.0), (0.0, 0.0)]

        self.Create(points)


class TriangleShape6(ogl.PolygonShape, ShapeMixin):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        ShapeMixin.__init__(self)
        if w == 0.0:
            w = 50.0
        if h == 0.0:
            h = 50.0

        points = [(h / 4.0, -w / 4.0), (h / 4.0, w / 4.0), (0.0, 0.0), (0.0, 0.0)]

        self.Create(points)


class TriangleShape7(ogl.PolygonShape, ShapeMixin):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        ShapeMixin.__init__(self)
        if w == 0.0:
            w = 50.0
        if h == 0.0:
            h = 50.0

        points = [(-h / 4.0, w / 4.0), (-h / 4.0, -w / 4.0), (0.0, 0.0), (0.0, 0.0)]

        self.Create(points)


class TriangleShape8(ogl.PolygonShape, ShapeMixin):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        ShapeMixin.__init__(self)
        if w == 0.0:
            w = 50.0
        if h == 0.0:
            h = 50.0

        points = [(-h / 4.0, -w / 4.0), (h / 4.0, -w / 4.0), (0.0, 0.0), (0.0, 0.0)]

        self.Create(points)


class RectangleShape(ogl.RectangleShape, ShapeMixin):
    def __init__(self, w=0.0, h=0.0):
        ogl.RectangleShape.__init__(self, w, h)
        ShapeMixin.__init__(self)


class PolygonShape(ogl.PolygonShape, ShapeMixin):
    """This is here so that rebuilding from DB is easier, don't have to worry
    about the different triangles
    """

    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        ShapeMixin.__init__(self)
        if w == 0.0:
            w = 50.0
        if h == 0.0:
            h = 50.0

        points = [(0.0, -h / 2.0), (w / 2.0, 0.0), (0.0, 0.0), (0.0, 0.0)]

        self.Create(points)


class RackDesigner(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(
            self,
            id=wxID_RACKDESIGNER,
            name="RackDesigner",
            parent=prnt,
            pos=wx.Point(478, 242),
            size=wx.Size(600, 600),
            style=wx.DEFAULT_FRAME_STYLE,
            title="Wine rack layout designer",
        )
        self.SetClientSize(wx.Size(592, 566))
        self.Bind(wx.EVT_CLOSE, self.OnRackDesignerClose)

        self.statusBar1 = wx.StatusBar(
            id=wxID_RACKDESIGNERSTATUSBAR1, name="statusBar1", parent=self, style=0
        )
        self.SetStatusBar(self.statusBar1)

        self.TB = wx.ToolBar(
            id=wxID_RACKDESIGNERTB,
            name="TB",
            parent=self,
            pos=wx.Point(0, 0),
            size=wx.Size(592, 28),
            style=wx.TB_HORIZONTAL | wx.NO_BORDER,
        )
        self.SetToolBar(self.TB)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.CreateToolBar()
        ogl.OGLInitialize()
        self.SetGetText()

        self.dataToSave = False
        self.designWindow = DesignWindow(self)

    def SetGetText(self):
        """Normally I use _('text') for gettext
        """
        self.SetTitle("Wine Rack layout designer")

    def CreateToolBar(self):
        toolSize = (24, 24)
        self.TB.SetToolBitmapSize(toolSize)

        # save
        self.wxId_TBSave = wx.NewId()
        img = myimages.getsaveImage()
        imgGO = myimages.getsaveImage()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Save rack design",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBSave,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBSave, id=self.wxId_TBSave)

        self.TB.AddSeparator()

        # delete
        self.wxId_TBDelete = wx.NewId()
        img = myimages.getwrDeleteImage()
        imgGO = myimages.getwrDeleteImage()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Delete shape",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBDelete,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBDelete, id=self.wxId_TBDelete)

        self.TB.AddSeparator()

        # Add rectangle
        self.wxId_TBAddRect = wx.NewId()
        img = myimages.getwrRectangleImage()
        imgGO = myimages.getwrRectangleImage()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Add rectangle",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBAddRect,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBAddRect, id=self.wxId_TBAddRect)

        # Add triangle 1
        self.wxId_TBAddTri1 = wx.NewId()
        img = myimages.getwrTriangle1Image()
        imgGO = myimages.getwrTriangle1Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Add triangle 1",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBAddTri1,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri1, id=self.wxId_TBAddTri1)

        # Add triangle 2
        self.wxId_TBAddTri2 = wx.NewId()
        img = myimages.getwrTriangle2Image()
        imgGO = myimages.getwrTriangle2Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Add triangle 2",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBAddTri2,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri2, id=self.wxId_TBAddTri2)

        # Add triangle 3
        self.wxId_TBAddTri3 = wx.NewId()
        img = myimages.getwrTriangle3Image()
        imgGO = myimages.getwrTriangle3Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Add triangle 3",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBAddTri3,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri3, id=self.wxId_TBAddTri3)

        # Add triangle 4
        self.wxId_TBAddTri4 = wx.NewId()
        img = myimages.getwrTriangle4Image()
        imgGO = myimages.getwrTriangle4Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Add triangle 4",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBAddTri4,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri4, id=self.wxId_TBAddTri4)

        # Add triangle 5
        self.wxId_TBAddTri5 = wx.NewId()
        img = myimages.getwrTriangle5Image()
        imgGO = myimages.getwrTriangle5Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Add triangle 5",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBAddTri5,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri5, id=self.wxId_TBAddTri5)

        # Add triangle 6
        self.wxId_TBAddTri6 = wx.NewId()
        img = myimages.getwrTriangle6Image()
        imgGO = myimages.getwrTriangle6Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Add triangle 6",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBAddTri6,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri6, id=self.wxId_TBAddTri6)

        # Add triangle 7
        self.wxId_TBAddTri7 = wx.NewId()
        img = myimages.getwrTriangle7Image()
        imgGO = myimages.getwrTriangle7Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Add triangle 7",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBAddTri7,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri7, id=self.wxId_TBAddTri7)

        # Add triangle 8
        self.wxId_TBAddTri8 = wx.NewId()
        img = myimages.getwrTriangle8Image()
        imgGO = myimages.getwrTriangle8Image()
        imgutil.grayOut(imgGO)
        bmp = wx.BitmapFromImage(img)
        bmpDA = wx.BitmapFromImage(imgGO)

        self.TB.AddLabelTool(
            label="Add triangle 8",
            bitmap=bmp,
            bmpDisabled=bmpDA,
            id=self.wxId_TBAddTri8,
            longHelp="",
            shortHelp="",
        )
        self.Bind(wx.EVT_TOOL, self.OnTBAddTri8, id=self.wxId_TBAddTri8)

        self.TB.Realize()
        self.TB.Layout()
        self.TB.Refresh()

    def OnTBSave(self, event):
        if len(self.designWindow.shapes) > 0:
            # create xml and write to db
            doc_header = """<shapes></shapes>"""
            xmlDoc = binderytools.bind_string(doc_header)
            for shape in self.designWindow.shapes:
                shape.Save(xmlDoc)

            # self.dbItemRack.shapeinfo = xmlDoc.xml(indent=u'yes')
            # adjust above to your db and remove below
            print(xmlDoc.xml(indent="yes"))
        else:
            pass
            # adjust to your db
            # self.dbItemRack.shapeinfo = ''

        # adjust to your db
        # wx.GetApp().Getds().commit()
        self.dataToSave = False

    def OnTBDelete(self, event):
        self.designWindow.DelShape()

    def OnTBAddRect(self, event):
        rackitemid, racktip = self.GetRackItem()
        if rackitemid != 0:
            self.designWindow.AddRectangle(rackitemid, racktip)
            self.dataToSave = True

    def OnTBAddTri1(self, event):
        rackitemid, racktip = self.GetRackItem()
        if rackitemid != 0:
            self.designWindow.AddTriangle1(rackitemid, racktip)
            self.dataToSave = True

    def OnTBAddTri2(self, event):
        rackitemid, racktip = self.GetRackItem()
        if rackitemid != 0:
            self.designWindow.AddTriangle2(rackitemid, racktip)
            self.dataToSave = True

    def OnTBAddTri3(self, event):
        rackitemid, racktip = self.GetRackItem()
        if rackitemid != 0:
            self.designWindow.AddTriangle3(rackitemid, racktip)
            self.dataToSave = True

    def OnTBAddTri4(self, event):
        rackitemid, racktip = self.GetRackItem()
        if rackitemid != 0:
            self.designWindow.AddTriangle4(rackitemid, racktip)
            self.dataToSave = True

    def OnTBAddTri5(self, event):
        rackitemid, racktip = self.GetRackItem()
        if rackitemid != 0:
            self.designWindow.AddTriangle5(rackitemid, racktip)
            self.dataToSave = True

    def OnTBAddTri6(self, event):
        rackitemid, racktip = self.GetRackItem()
        if rackitemid != 0:
            self.designWindow.AddTriangle6(rackitemid, racktip)
            self.dataToSave = True

    def OnTBAddTri7(self, event):
        rackitemid, racktip = self.GetRackItem()
        if rackitemid != 0:
            self.designWindow.AddTriangle7(rackitemid, racktip)
            self.dataToSave = True

    def OnTBAddTri8(self, event):
        rackitemid, racktip = self.GetRackItem()
        if rackitemid != 0:
            self.designWindow.AddTriangle8(rackitemid, racktip)
            self.dataToSave = True

    def OnRackDesignerClose(self, event):
        if self.dataToSave:
            dlgText = 'You entered data which is not saved! Click on "No" to return and save it\n\nor on "Yes" to quit and lose it!'
            dlgName = "Unsaved data warning!"

            try:
                dlg = wx.MessageDialog(
                    self, dlgText, dlgName, wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
                )

                if dlg.ShowModal() == wx.ID_YES:
                    # roll back database - adjust to your db
                    # wx.GetApp().Getds().rollback()
                    pass
                else:
                    return
            finally:
                dlg.Destroy()
        else:
            # roll back database - adjust to your db
            # wx.GetApp().Getds().rollback()
            pass

        self.MakeModal(False)
        event.Skip()

    def GetRackItem(self):
        # remove return and adjust to your db the following
        return (wx.NewId(), "some tip information")

        # get information about a rack item
        bins = []
        binsid = []
        where = "fk_winerackid = %i" % self.dbItemRack.winerackid
        orderby = "binno, subbinno"
        dbItem = (
            wx.GetApp()
            .Getds()
            .selectByClauses(beans.winerackb, where=where, orderby=orderby)
            .fetchall()
        )
        for bin in dbItem:
            shapetip = "Bin no: %i, Sub-bin no: %i, Capacity: %i, Description: %s" % (
                bin.binno,
                bin.subbinno,
                bin.capacity,
                bin.description,
            )
            bins.append(shapetip)
            binsid.append(bin.winerackbid)

        dlg = wx.SingleChoiceDialog(
            self, "Double click or select and click OK", "Select the bin number", bins
        )
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.dataToSave = True
                return (binsid[dlg.GetSelection()], dlg.GetStringSelection())
            else:
                return (0, "")
        finally:
            dlg.Destroy()

    def SetDbItem(self, dbitem):
        # remove return and adjust to your db
        # this loads an existing design from the db
        return

        self.dbItemRack = dbitem
        # load diagram from db
        if self.dbItemRack.shapeinfo:
            xmlDoc = binderytools.bind_string(self.dbItemRack.shapeinfo)
            if hasattr(xmlDoc.shapes, "RectangleShape"):
                for shape in xmlDoc.shapes.RectangleShape:
                    x = float(str(shape.x))
                    y = float(str(shape.y))
                    width = float(str(shape.width))
                    height = float(str(shape.height))
                    newShape = self.designWindow.MyAddShape(
                        RectangleShape(width, height), x, y, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
                    )
                    newShape.SetRackItemId(int(str(shape.rackitemid)))
                    if newShape.GetRackItemId() != 0:
                        bin = (
                            wx.GetApp()
                            .Getds()
                            .selectByPrimaryKey(beans.winerackb, newShape.GetRackItemId())
                        )
                        shapetip = "Bin no: %i, Sub-bin no: %i, Capacity: %i, Description: %s" % (
                            bin.binno,
                            bin.subbinno,
                            bin.capacity,
                            bin.description,
                        )
                        newShape.SetShapeTip(shapetip)
                    newShape.GetCanvas().Refresh()
            if hasattr(xmlDoc.shapes, "PolygonShape"):
                for shape in xmlDoc.shapes.PolygonShape:
                    x = float(str(shape.x))
                    y = float(str(shape.y))
                    width = float(str(shape.width))
                    height = float(str(shape.height))
                    shapePoints = []
                    for point in shape.points.point:
                        shapePoints.append((float(str(point.x)), float(str(point.y))))
                    newShape = self.designWindow.MyAddShape(
                        PolygonShape(width, height), x, y, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
                    )
                    newShape.Create(shapePoints)
                    newShape.SetRackItemId(int(str(shape.rackitemid)))
                    if newShape.GetRackItemId() != 0:
                        bin = (
                            wx.GetApp()
                            .Getds()
                            .selectByPrimaryKey(beans.winerackb, newShape.GetRackItemId())
                        )
                        shapetip = "Bin no: %i, Sub-bin no: %i, Capacity: %i" % (
                            bin.binno,
                            bin.subbinno,
                            bin.capacity,
                        )
                        newShape.SetShapeTip(shapetip)
                    newShape.GetCanvas().Refresh()


class MyEvtHandler(ogl.ShapeEvtHandler):
    def __init__(self, frame):
        ogl.ShapeEvtHandler.__init__(self)
        self.statbarFrame = frame

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        width, height = shape.GetBoundingBoxMax()
        try:
            shapeTip = shape.GetShapeTip()
        except:
            shapeTip = ""

        self.statbarFrame.SetStatusText(
            "Pos: (%d, %d)  Size: (%d, %d)   %s" % (x, y, width, height, shapeTip)
        )

    def OnLeftClick(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        canvas = shape.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(False, dc)
            canvas.Redraw(dc)
            canvas.selectedShape = None
        else:
            canvas.selectedShape = shape
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

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)

        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)

        self.UpdateStatusBar(shape)
        shape.GetCanvas().Refresh()

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
        self.UpdateStatusBar(self.GetShape())

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        self.UpdateStatusBar(self.GetShape())

    def OnRightClick(self, *dontcare):
        shape = self.GetShape()
        rackdesigner = shape.GetCanvas().GetParent()
        rackitemid, shapetip = rackdesigner.GetRackItem()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        self.UpdateStatusBar(shape)


# ----------------------------------------------------------------------


class DesignWindow(ogl.ShapeCanvas):
    def __init__(self, frame):
        ogl.ShapeCanvas.__init__(self, frame)

        maxWidth = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth / 20, maxHeight / 20)

        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE")
        self.diagram = ogl.Diagram()
        ##        # can't get below to work for triangles, aligment is wrong
        self.diagram.SetGridSpacing(1)
        self.diagram.SetSnapToGrid(True)
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.shapes = []
        self.save_gdi = []

        rRectBrush = wx.Brush("MEDIUM TURQUOISE", wx.SOLID)
        dsBrush = wx.Brush("WHEAT", wx.SOLID)

        dc = wx.ClientDC(self)
        self.PrepareDC(dc)

        self.selectedShape = None

    def DelShape(self):
        if self.selectedShape != None:
            shape = self.selectedShape
            if shape.Selected():
                canvas = shape.GetCanvas()
                shape.RemoveFromCanvas(canvas)
                canvas.Refresh()
                self.shapes.remove(shape)
                self.selectedShape = None

    def AddRectangle(self, rackitemid, shapetip):
        shape = self.MyAddShape(
            RectangleShape(50, 50), 60, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
        )
        shape.GetCanvas().Refresh()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        return shape

    def AddTriangle1(self, rackitemid, shapetip):
        shape = self.MyAddShape(
            TriangleShape1(100, 100), 60, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
        )
        shape.GetCanvas().Refresh()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        return shape

    def AddTriangle2(self, rackitemid, shapetip):
        shape = self.MyAddShape(
            TriangleShape2(100, 100), 60, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
        )
        shape.GetCanvas().Refresh()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        return shape

    def AddTriangle3(self, rackitemid, shapetip):
        shape = self.MyAddShape(
            TriangleShape3(100, 100), 60, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
        )
        shape.GetCanvas().Refresh()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        return shape

    def AddTriangle4(self, rackitemid, shapetip):
        shape = self.MyAddShape(
            TriangleShape4(100, 100), 60, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
        )
        shape.GetCanvas().Refresh()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        return shape

    def AddTriangle5(self, rackitemid, shapetip):
        shape = self.MyAddShape(
            TriangleShape5(100, 100), 60, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
        )
        shape.GetCanvas().Refresh()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        return shape

    def AddTriangle6(self, rackitemid, shapetip):
        shape = self.MyAddShape(
            TriangleShape6(100, 100), 60, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
        )
        shape.GetCanvas().Refresh()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        return shape

    def AddTriangle7(self, rackitemid, shapetip):
        shape = self.MyAddShape(
            TriangleShape7(100, 100), 60, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
        )
        shape.GetCanvas().Refresh()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        return shape

    def AddTriangle8(self, rackitemid, shapetip):
        shape = self.MyAddShape(
            TriangleShape8(100, 100), 60, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, ""
        )
        shape.GetCanvas().Refresh()
        shape.SetRackItemId(rackitemid)
        shape.SetShapeTip(shapetip)
        return shape

    def MyAddShape(self, shape, x, y, pen, brush, text):
        # Composites have to be moved for all children to get in place
        if isinstance(shape, ogl.CompositeShape):
            dc = wx.ClientDC(self)
            self.PrepareDC(dc)
            shape.Move(dc, x, y)
        else:
            shape.SetDraggable(True, True)

        if isinstance(shape, ogl.RectangleShape):
            shape.SetCentreResize(False)

        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        if pen:
            shape.SetPen(wx.Pen(wx.BLACK, 2))
        if brush:
            shape.SetBrush(brush)
        if text:
            for line in text.split("\n"):
                shape.AddText(line)
        self.diagram.AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler(self.frame)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)
        return shape

    def OnBeginDragLeft(self, x, y, keys):
        pass

    def OnEndDragLeft(self, x, y, keys):
        pass


if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = create(None)
    frame.Show()

    app.MainLoop()
