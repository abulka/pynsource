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
## Class DialogComment
###########################################################################

class DialogComment ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Comment", pos = wx.DefaultPosition, size = wx.Size( 372,332 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer9 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer11 = wx.BoxSizer( wx.VERTICAL )

		bSizer13 = wx.BoxSizer( wx.HORIZONTAL )

		self.txt_comment = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		# self.txt_comment.SetMaxLength( 0 )
		bSizer13.Add( self.txt_comment, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer11.Add( bSizer13, 5, wx.EXPAND, 5 )


		self.m_panel2.SetSizer( bSizer11 )
		self.m_panel2.Layout()
		bSizer11.Fit( self.m_panel2 )
		bSizer9.Add( self.m_panel2, 6, wx.EXPAND |wx.ALL, 5 )

		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer5 = wx.BoxSizer( wx.VERTICAL )

		self.m_button1 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button1, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer4.Add( bSizer5, 1, wx.EXPAND, 5 )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		self.m_button2 = wx.Button( self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button2, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer4.Add( bSizer6, 1, wx.EXPAND, 5 )


		bSizer9.Add( bSizer4, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )


		self.SetSizer( bSizer9 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


