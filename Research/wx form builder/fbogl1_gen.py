# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Mar 22 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.lib.ogl as ogl

###########################################################################
## Class MyFrame2
###########################################################################


class MyFrame2(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=wx.EmptyString,
            pos=wx.DefaultPosition,
            size=wx.Size(500, 300),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer9 = wx.BoxSizer(wx.VERTICAL)

        self.canvas = ogl.ShapeCanvas(self)
        diagram = ogl.Diagram()
        self.canvas.SetDiagram(diagram)
        diagram.SetCanvas(self.canvas)
        bSizer9.Add(self.canvas, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(bSizer9)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
