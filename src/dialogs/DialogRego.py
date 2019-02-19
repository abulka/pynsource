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
## Class RegoDialog
###########################################################################

class RegoDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Enter Registration Details", pos = wx.DefaultPosition, size = wx.Size( 326,184 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		vsizer1 = wx.BoxSizer( wx.VERTICAL )

		row0 = wx.BoxSizer( wx.VERTICAL )


		row0.Add( ( 0, 3), 1, wx.EXPAND, 5 )

		self.info = wx.StaticText( self, wx.ID_ANY, u"Enter your name exactly the same way as when you purchased your serial.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.info.Wrap( 300 )

		row0.Add( self.info, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM|wx.TOP, 8 )


		vsizer1.Add( row0, 1, wx.EXPAND, 5 )

		row1 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		row1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_textCtrl_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		row1.Add( self.m_textCtrl_name, 1, wx.ALIGN_CENTER|wx.RIGHT, 20 )


		vsizer1.Add( row1, 1, wx.EXPAND, 5 )

		row2 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"Serial", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )

		row2.Add( self.m_staticText11, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_textCtrl_serial = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		row2.Add( self.m_textCtrl_serial, 1, wx.ALIGN_CENTER|wx.RIGHT, 20 )


		vsizer1.Add( row2, 1, wx.EXPAND, 5 )

		row3 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_button1 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		row3.Add( self.m_button1, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

		self.m_button2 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		row3.Add( self.m_button2, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		vsizer1.Add( row3, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )


		self.SetSizer( vsizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


