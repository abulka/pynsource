# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class DialogUmlNodeEdit
###########################################################################

class DialogUmlNodeEdit ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Uml Node Properties", pos = wx.DefaultPosition, size = wx.Size( 342,469 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer9 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer11 = wx.BoxSizer( wx.VERTICAL )

		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Class Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		self.m_staticText1.SetMinSize( wx.Size( 55,-1 ) )

		bSizer12.Add( self.m_staticText1, 1, 0, 5 )

		bSizer10 = wx.BoxSizer( wx.VERTICAL )

		self.txtClassName = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.txtClassName, 1, wx.EXPAND, 5 )


		bSizer12.Add( bSizer10, 2, wx.EXPAND, 5 )


		bSizer11.Add( bSizer12, 0, wx.EXPAND, 5 )

		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText2 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Attributes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		self.m_staticText2.SetMinSize( wx.Size( 55,-1 ) )

		bSizer14.Add( self.m_staticText2, 1, 0, 5 )

		bSizer91 = wx.BoxSizer( wx.VERTICAL )

		self.txtAttrs = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		bSizer91.Add( self.txtAttrs, 3, wx.EXPAND, 5 )


		bSizer14.Add( bSizer91, 2, wx.ALL|wx.EXPAND, 5 )


		bSizer11.Add( bSizer14, 2, wx.EXPAND, 5 )

		bSizer13 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText3 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Methods", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		self.m_staticText3.SetMinSize( wx.Size( 55,-1 ) )

		bSizer13.Add( self.m_staticText3, 1, 0, 5 )

		bSizer111 = wx.BoxSizer( wx.VERTICAL )

		self.txtMethods = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		bSizer111.Add( self.txtMethods, 3, wx.ALL|wx.EXPAND, 5 )


		bSizer13.Add( bSizer111, 2, wx.EXPAND, 5 )


		bSizer11.Add( bSizer13, 2, wx.ALL|wx.EXPAND, 5 )

		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer5 = wx.BoxSizer( wx.VERTICAL )

		self.m_button1 = wx.Button( self.m_panel2, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button1, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer4.Add( bSizer5, 1, wx.ALIGN_CENTER_VERTICAL, 5 )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		self.m_button2 = wx.Button( self.m_panel2, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button2, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer4.Add( bSizer6, 1, wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer11.Add( bSizer4, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )


		self.m_panel2.SetSizer( bSizer11 )
		self.m_panel2.Layout()
		bSizer11.Fit( self.m_panel2 )
		bSizer9.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer9 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


