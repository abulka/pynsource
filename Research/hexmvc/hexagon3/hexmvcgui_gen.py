# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Mar 22 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.aui

###########################################################################
## Class HexMvcGuiFrame1
###########################################################################

class HexMvcGuiFrame1 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"HexMvc Gui 1", pos = wx.DefaultPosition, size = wx.Size( 514,413 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.m_mgr = wx.aui.AuiManager()
		self.m_mgr.SetManagedWindow( self )
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menuItem1 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"New", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.AppendItem( self.m_menuItem1 )
		
		self.m_menuItem2 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Load", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.AppendItem( self.m_menuItem2 )
		
		self.m_menuItem3 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Save", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.AppendItem( self.m_menuItem3 )
		
		self.m_menubar1.Append( self.m_menu1, u"File" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_mgr.AddPane( self.m_panel1, wx.aui.AuiPaneInfo() .Left() .CloseButton( False ).MaximizeButton( False ).MinimizeButton( False ).PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).CentrePane() )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_textCtrl1 = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,80 ), wx.TE_MULTILINE )
		bSizer1.Add( self.m_textCtrl1, 0, wx.ALL|wx.EXPAND, 5 )
		
		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button3 = wx.Button( self.m_panel1, wx.ID_ANY, u"Dump Model", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button3, 0, wx.ALL, 5 )
		
		self.m_button9 = wx.Button( self.m_panel1, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button9, 0, wx.ALL, 5 )
		
		self.m_button4 = wx.Button( self.m_panel1, wx.ID_ANY, u"Add Junk Text", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button4, 0, wx.ALL, 5 )
		
		self.m_button5 = wx.Button( self.m_panel1, wx.ID_ANY, u"MessageBox", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button5, 0, wx.ALL, 5 )
		
		bSizer7.Add( bSizer3, 0, 0, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button11 = wx.Button( self.m_panel1, wx.ID_ANY, u"Background Task 1", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button11, 0, wx.ALL, 5 )
		
		self.m_button12 = wx.Button( self.m_panel1, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button12, 0, wx.ALL, 5 )
		
		self.m_gauge1 = wx.Gauge( self.m_panel1, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		bSizer5.Add( self.m_gauge1, 0, wx.ALL, 5 )
		
		bSizer7.Add( bSizer5, 1, wx.EXPAND, 5 )
		
		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button6 = wx.Button( self.m_panel1, wx.ID_ANY, u"New", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button6, 0, wx.ALL, 5 )
		
		self.m_button7 = wx.Button( self.m_panel1, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button7, 0, wx.ALL, 5 )
		
		self.m_button8 = wx.Button( self.m_panel1, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button8, 0, wx.ALL, 5 )
		
		bSizer7.Add( bSizer4, 1, wx.EXPAND, 5 )
		
		m_listBox1Choices = []
		self.m_listBox1 = wx.ListBox( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0 )
		bSizer7.Add( self.m_listBox1, 2, wx.ALL, 5 )
		
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button1 = wx.Button( self.m_panel1, wx.ID_ANY, u"Add Thing", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_button1, 0, wx.ALL, 5 )
		
		self.m_button2 = wx.Button( self.m_panel1, wx.ID_ANY, u"Delete Thing", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_button2, 0, wx.ALL, 5 )
		
		self.m_button121 = wx.Button( self.m_panel1, wx.ID_ANY, u"Add Info To Thing", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_button121, 0, wx.ALL, 5 )
		
		bSizer7.Add( bSizer2, 1, wx.EXPAND, 5 )
		
		bSizer6.Add( bSizer7, 1, 0, 5 )
		
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_hyperlink1 = wx.HyperlinkCtrl( self.m_panel1, wx.ID_ANY, u"/", u"http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8.Add( self.m_hyperlink1, 0, wx.ALL, 5 )
		
		self.m_hyperlink2 = wx.HyperlinkCtrl( self.m_panel1, wx.ID_ANY, u"/aa", u"http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8.Add( self.m_hyperlink2, 0, wx.ALL, 5 )
		
		self.m_hyperlink3 = wx.HyperlinkCtrl( self.m_panel1, wx.ID_ANY, u"/hello", u"http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8.Add( self.m_hyperlink3, 0, wx.ALL, 5 )
		
		self.m_hyperlink4 = wx.HyperlinkCtrl( self.m_panel1, wx.ID_ANY, u"/hello/man", u"http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8.Add( self.m_hyperlink4, 0, wx.ALL, 5 )
		
		self.m_hyperlink5 = wx.HyperlinkCtrl( self.m_panel1, wx.ID_ANY, u"/ajax", u"http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8.Add( self.m_hyperlink5, 0, wx.ALL, 5 )
		
		self.m_hyperlink6 = wx.HyperlinkCtrl( self.m_panel1, wx.ID_ANY, u"/ajax_info1", u"http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8.Add( self.m_hyperlink6, 0, wx.ALL, 5 )
		
		self.m_hyperlink8 = wx.HyperlinkCtrl( self.m_panel1, wx.ID_ANY, u"/xml", u"http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8.Add( self.m_hyperlink8, 0, wx.ALL, 5 )
		
		bSizer6.Add( bSizer8, 0, 0, 5 )
		
		bSizer1.Add( bSizer6, 1, wx.EXPAND, 5 )
		
		self.m_panel1.SetSizer( bSizer1 )
		self.m_panel1.Layout()
		bSizer1.Fit( self.m_panel1 )
		
		self.m_mgr.Update()
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_MENU, self.FileNew, id = self.m_menuItem1.GetId() )
		self.Bind( wx.EVT_MENU, self.FileLoad, id = self.m_menuItem2.GetId() )
		self.m_button3.Bind( wx.EVT_BUTTON, self.DumpModel )
		self.m_button9.Bind( wx.EVT_BUTTON, self.DumpClear )
		self.m_button4.Bind( wx.EVT_BUTTON, self.AddJunkText )
		self.m_button5.Bind( wx.EVT_BUTTON, self.MiscMessageBox )
		self.m_button11.Bind( wx.EVT_BUTTON, self.BackgroundTask1 )
		self.m_button12.Bind( wx.EVT_BUTTON, self.StopBackgroundTask1 )
		self.m_button6.Bind( wx.EVT_BUTTON, self.FileNew )
		self.m_button7.Bind( wx.EVT_BUTTON, self.FileLoad )
		self.m_button1.Bind( wx.EVT_BUTTON, self.AddThing )
		self.m_button2.Bind( wx.EVT_BUTTON, self.DeleteThing )
		self.m_button121.Bind( wx.EVT_BUTTON, self.AddInfoToThing )
	
	def __del__( self ):
		self.m_mgr.UnInit()
		
	
	
	# Virtual event handlers, overide them in your derived class
	def FileNew( self, event ):
		event.Skip()
	
	def FileLoad( self, event ):
		event.Skip()
	
	def DumpModel( self, event ):
		event.Skip()
	
	def DumpClear( self, event ):
		event.Skip()
	
	def AddJunkText( self, event ):
		event.Skip()
	
	def MiscMessageBox( self, event ):
		event.Skip()
	
	def BackgroundTask1( self, event ):
		event.Skip()
	
	def StopBackgroundTask1( self, event ):
		event.Skip()
	
	
	
	def AddThing( self, event ):
		event.Skip()
	
	def DeleteThing( self, event ):
		event.Skip()
	
	def AddInfoToThing( self, event ):
		event.Skip()
	

