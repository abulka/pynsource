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
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,445 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_button1 = wx.Button( self, wx.ID_ANY, u"AAAA", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button1, 0, wx.ALL, 5 )

		self.m_button2 = wx.Button( self, wx.ID_ANY, u"BBBBB", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button2, 0, wx.ALL, 5 )

		self.m_button3 = wx.Button( self, wx.ID_ANY, u"CCCCC", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button3, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer5, 0, 0, 5 )

		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"label" ), wx.VERTICAL )

		self.m_button5 = wx.Button( sbSizer1.GetStaticBox(), wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer1.Add( self.m_button5, 0, wx.ALL, 5 )

		self.m_button4 = wx.Button( sbSizer1.GetStaticBox(), wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer1.Add( self.m_button4, 0, wx.ALL, 5 )


		bSizer1.Add( sbSizer1, 1, wx.EXPAND, 5 )

		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

		self.m_button11 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button11, 0, wx.ALL, 5 )

		self.m_button10 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button10, 0, wx.ALL, 5 )

		self.m_button6 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button6, 0, wx.ALL, 5 )

		self.m_button7 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button7, 0, wx.ALL, 5 )

		self.m_button8 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button8, 0, wx.ALL, 5 )

		self.m_button9 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button9, 0, wx.ALL, 5 )


		bSizer1.Add( gSizer1, 1, wx.EXPAND, 5 )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_button12 = wx.Button( self.m_panel1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button12, 0, wx.ALL, 5 )

		self.m_button13 = wx.Button( self.m_panel1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button13, 0, wx.ALL, 5 )

		self.m_button14 = wx.Button( self.m_panel1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button14, 0, wx.ALL, 5 )

		bSizer4 = wx.BoxSizer( wx.VERTICAL )

		self.m_button15 = wx.Button( self.m_panel1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button15, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_button16 = wx.Button( self.m_panel1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button16, 0, wx.ALL, 5 )


		bSizer3.Add( bSizer4, 1, wx.ALIGN_CENTER, 5 )


		bSizer2.Add( bSizer3, 1, wx.EXPAND, 5 )


		self.m_panel1.SetSizer( bSizer2 )
		self.m_panel1.Layout()
		bSizer2.Fit( self.m_panel1 )
		bSizer6.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )


		bSizer1.Add( bSizer6, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


###########################################################################
## Class MyPanel1
###########################################################################

class MyPanel1 ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )


	def __del__( self ):
		pass


###########################################################################
## Class MyDialog1
###########################################################################

class MyDialog1 ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )


		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


###########################################################################
## Class MyMenuBar1
###########################################################################

class MyMenuBar1 ( wx.MenuBar ):

	def __init__( self ):
		wx.MenuBar.__init__ ( self, style = 0 )

		self.m_menu1 = wx.Menu()
		self.m_menu11 = wx.Menu()
		self.m_menuItem1 = wx.MenuItem( self.m_menu11, wx.ID_ANY, u"MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu11.Append( self.m_menuItem1 )

		self.m_menuItem2 = wx.MenuItem( self.m_menu11, wx.ID_ANY, u"MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu11.Append( self.m_menuItem2 )

		self.m_menuItem3 = wx.MenuItem( self.m_menu11, wx.ID_ANY, u"MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu11.Append( self.m_menuItem3 )

		self.m_menu1.AppendSubMenu( self.m_menu11, u"MyMenu" )

		self.Append( self.m_menu1, u"MyMenu" )

		self.m_menu2 = wx.Menu()
		self.m_menuItem5 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.Append( self.m_menuItem5 )

		self.m_menuItem6 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.Append( self.m_menuItem6 )

		self.m_menuItem7 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.Append( self.m_menuItem7 )

		self.Append( self.m_menu2, u"MyMenu" )


	def __del__( self ):
		pass


###########################################################################
## Class MyToolBar1
###########################################################################

class MyToolBar1 ( wx.ToolBar ):

	def __init__( self, parent ):
		wx.ToolBar.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TB_HORIZONTAL )

		self.m_checkBox1 = wx.CheckBox( self, wx.ID_ANY, u"Check Me!", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.AddControl( self.m_checkBox1 )
		m_comboBox1Choices = []
		self.m_comboBox1 = wx.ComboBox( self, wx.ID_ANY, u"Combo!", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices, 0 )
		self.AddControl( self.m_comboBox1 )
		self.m_bpButton1 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		self.AddControl( self.m_bpButton1 )
		self.m_bpButton2 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		self.AddControl( self.m_bpButton2 )
		self.m_button21 = wx.Button( self, wx.ID_ANY, u"feeling", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.AddControl( self.m_button21 )

		self.Realize()

	def __del__( self ):
		pass


###########################################################################
## Class MyFrame2
###########################################################################

class MyFrame2 ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer13 = wx.BoxSizer( wx.VERTICAL )

		self.m_scrolledWindow1 = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_scrolledWindow1.SetScrollRate( 5, 5 )
		bSizer14 = wx.BoxSizer( wx.VERTICAL )

		self.m_button30 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button30, 0, wx.ALL, 5 )

		self.m_button31 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button31, 0, wx.ALL, 5 )

		self.m_button32 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button32, 0, wx.ALL, 5 )

		self.m_button33 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button33, 0, wx.ALL, 5 )

		self.m_button34 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button34, 0, wx.ALL, 5 )

		self.m_button35 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button35, 0, wx.ALL, 5 )

		self.m_button36 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button36, 0, wx.ALL, 5 )

		self.m_button37 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button37, 0, wx.ALL, 5 )

		self.m_button38 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button38, 0, wx.ALL, 5 )

		self.m_button39 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button39, 0, wx.ALL, 5 )

		self.m_button40 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button40, 0, wx.ALL, 5 )

		self.m_button41 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button41, 0, wx.ALL, 5 )

		self.m_button42 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button42, 0, wx.ALL, 5 )

		self.m_button43 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button43, 0, wx.ALL, 5 )

		self.m_button44 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button44, 0, wx.ALL, 5 )

		self.m_button45 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button45, 0, wx.ALL, 5 )

		self.m_button46 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_button46, 0, wx.ALL, 5 )


		self.m_scrolledWindow1.SetSizer( bSizer14 )
		self.m_scrolledWindow1.Layout()
		bSizer14.Fit( self.m_scrolledWindow1 )
		bSizer13.Add( self.m_scrolledWindow1, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer13 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


