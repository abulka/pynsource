# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Mar 22 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.html

###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,366 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_notebook2 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_panel1 = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_htmlWin1 = wx.html.HtmlWindow( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
		bSizer4.Add( self.m_htmlWin1, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_panel1.SetSizer( bSizer4 )
		self.m_panel1.Layout()
		bSizer4.Fit( self.m_panel1 )
		self.m_notebook2.AddPage( self.m_panel1, u"a page", True )
		self.m_panel6 = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button5 = wx.Button( self.m_panel6, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button5, 0, wx.ALL, 5 )
		
		self.m_button6 = wx.Button( self.m_panel6, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button6, 0, wx.ALL, 5 )
		
		self.m_button7 = wx.Button( self.m_panel6, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.m_button7, 0, wx.ALL, 5 )
		
		bSizer5.Add( bSizer6, 1, wx.EXPAND, 5 )
		
		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_searchCtrl1 = wx.SearchCtrl( self.m_panel6, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_searchCtrl1.ShowSearchButton( True )
		self.m_searchCtrl1.ShowCancelButton( False )
		bSizer7.Add( self.m_searchCtrl1, 0, wx.ALL, 5 )
		
		self.m_searchCtrl2 = wx.SearchCtrl( self.m_panel6, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_searchCtrl2.ShowSearchButton( True )
		self.m_searchCtrl2.ShowCancelButton( False )
		bSizer7.Add( self.m_searchCtrl2, 0, wx.ALL, 5 )
		
		bSizer5.Add( bSizer7, 1, wx.EXPAND, 5 )
		
		self.m_panel6.SetSizer( bSizer5 )
		self.m_panel6.Layout()
		bSizer5.Fit( self.m_panel6 )
		self.m_notebook2.AddPage( self.m_panel6, u"a page", False )
		self.m_panel7 = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_panel7.SetSizer( bSizer8 )
		self.m_panel7.Layout()
		bSizer8.Fit( self.m_panel7 )
		self.m_notebook2.AddPage( self.m_panel7, u"a page", False )
		
		bSizer1.Add( self.m_notebook2, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.m_splitter1 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SP_3DBORDER|wx.SP_BORDER )
		self.m_splitter1.Bind( wx.EVT_IDLE, self.m_splitter1OnIdle )
		
		self.m_panel4 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL )
		self.m_panel4.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_button1 = wx.Button( self.m_panel4, wx.ID_ANY, u"Load Html", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_button1, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button2 = wx.Button( self.m_panel4, wx.ID_ANY, u"Load Html 2", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_button2, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_panel4.SetSizer( bSizer2 )
		self.m_panel4.Layout()
		bSizer2.Fit( self.m_panel4 )
		self.m_scrolledWindow1 = wx.ScrolledWindow( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.SIMPLE_BORDER|wx.VSCROLL )
		self.m_scrolledWindow1.SetScrollRate( 5, 5 )
		self.m_scrolledWindow1.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )
		
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_slider1 = wx.Slider( self.m_scrolledWindow1, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		bSizer3.Add( self.m_slider1, 0, wx.ALL, 5 )
		
		self.m_slider2 = wx.Slider( self.m_scrolledWindow1, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		bSizer3.Add( self.m_slider2, 0, wx.ALL|wx.EXPAND, 5 )
		
		m_comboBox1Choices = []
		self.m_comboBox1 = wx.ComboBox( self.m_scrolledWindow1, wx.ID_ANY, u"Combo!", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices, 0 )
		bSizer3.Add( self.m_comboBox1, 0, wx.ALL, 5 )
		
		self.m_gauge1 = wx.Gauge( self.m_scrolledWindow1, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		self.m_gauge1.SetValue( 3 ) 
		bSizer3.Add( self.m_gauge1, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_slider3 = wx.Slider( self.m_scrolledWindow1, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		bSizer3.Add( self.m_slider3, 0, wx.ALL, 5 )
		
		self.m_button3 = wx.Button( self.m_scrolledWindow1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button3, 0, wx.ALL, 5 )
		
		self.m_scrolledWindow1.SetSizer( bSizer3 )
		self.m_scrolledWindow1.Layout()
		bSizer3.Fit( self.m_scrolledWindow1 )
		self.m_splitter1.SplitVertically( self.m_panel4, self.m_scrolledWindow1, 162 )
		bSizer1.Add( self.m_splitter1, 1, wx.EXPAND, 5 )
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnLoadHtml1 )
		self.m_button2.Bind( wx.EVT_BUTTON, self.OnHtml2 )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnLoadHtml1( self, event ):
		event.Skip()
	
	def OnHtml2( self, event ):
		event.Skip()
	
	def m_splitter1OnIdle( self, event ):
		self.m_splitter1.SetSashPosition( 162 )
		self.m_splitter1.Unbind( wx.EVT_IDLE )
	

