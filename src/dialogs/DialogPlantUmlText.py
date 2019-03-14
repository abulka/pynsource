# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.adv

###########################################################################
## Class DialogPlantUmlText
###########################################################################

class DialogPlantUmlText ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Generated PlantUML Markup", pos = wx.DefaultPosition, size = wx.Size( 427,525 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer9 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer11 = wx.BoxSizer( wx.VERTICAL )

		bSizer13 = wx.BoxSizer( wx.VERTICAL )

		self.txt_plantuml = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		self.txt_plantuml.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Courier" ) )
		self.txt_plantuml.Enable( False )

		bSizer13.Add( self.txt_plantuml, 5, wx.ALL|wx.EXPAND, 5 )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_bitmap1 = wx.StaticBitmap( self.m_panel2, wx.ID_ANY, wx.Bitmap( u"help-images/pro.jpg", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_bitmap1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Pro Edition enables the selection and copying of generated PlantUML text.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( 380 )

		bSizer4.Add( self.m_staticText1, 0, wx.ALL, 5 )


		bSizer6.Add( bSizer4, 0, wx.EXPAND, 5 )

		bSizer7 = wx.BoxSizer( wx.VERTICAL )

		self.m_hyperlink1 = wx.adv.HyperlinkCtrl( self.m_panel2, wx.ID_ANY, u"Learn about PlantUML markup", u"http://plantuml.com/class-diagram", wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
		bSizer7.Add( self.m_hyperlink1, 1, wx.ALIGN_CENTER, 5 )

		self.m_staticText11 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Tip: Add additional PlantUML markup to create customised and more complex diagrams, with all the features that PlantUML has to offer.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( 380 )

		bSizer7.Add( self.m_staticText11, 0, wx.ALL, 5 )


		bSizer6.Add( bSizer7, 1, wx.EXPAND, 5 )


		bSizer13.Add( bSizer6, 1, wx.EXPAND, 5 )


		bSizer11.Add( bSizer13, 5, wx.EXPAND, 5 )

		m_sdbSizer1 = wx.StdDialogButtonSizer()
		self.m_sdbSizer1OK = wx.Button( self.m_panel2, wx.ID_OK )
		m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
		m_sdbSizer1.Realize();

		bSizer11.Add( m_sdbSizer1, 0, wx.ALIGN_CENTER, 1 )


		self.m_panel2.SetSizer( bSizer11 )
		self.m_panel2.Layout()
		bSizer11.Fit( self.m_panel2 )
		bSizer9.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer9 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


