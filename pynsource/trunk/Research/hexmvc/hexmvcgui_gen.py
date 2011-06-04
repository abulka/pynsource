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
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"HexMvc Gui 1", pos = wx.DefaultPosition, size = wx.Size( 500,396 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
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
		
		self.m_textCtrl1 = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		bSizer1.Add( self.m_textCtrl1, 2, wx.ALL|wx.EXPAND, 5 )
		
		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button3 = wx.Button( self.m_panel1, wx.ID_ANY, u"Dump Model", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button3, 0, wx.ALL, 5 )
		
		self.m_button9 = wx.Button( self.m_panel1, wx.ID_ANY, u"Dump Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button9, 0, wx.ALL, 5 )
		
		self.m_button4 = wx.Button( self.m_panel1, wx.ID_ANY, u"Misc1", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button4, 0, wx.ALL, 5 )
		
		self.m_button5 = wx.Button( self.m_panel1, wx.ID_ANY, u"MessageBox", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button5, 0, wx.ALL, 5 )
		
		bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )
		
		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button6 = wx.Button( self.m_panel1, wx.ID_ANY, u"New", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button6, 0, wx.ALL, 5 )
		
		self.m_button7 = wx.Button( self.m_panel1, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button7, 0, wx.ALL, 5 )
		
		self.m_button8 = wx.Button( self.m_panel1, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_button8, 0, wx.ALL, 5 )
		
		bSizer1.Add( bSizer4, 1, wx.EXPAND, 5 )
		
		m_listBox1Choices = []
		self.m_listBox1 = wx.ListBox( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0 )
		bSizer1.Add( self.m_listBox1, 2, wx.ALL, 5 )
		
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button1 = wx.Button( self.m_panel1, wx.ID_ANY, u"Add Thing", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_button1, 0, wx.ALL, 5 )
		
		self.m_button2 = wx.Button( self.m_panel1, wx.ID_ANY, u"Delete Thing", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_button2, 0, wx.ALL, 5 )
		
		bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
		
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
		self.m_button4.Bind( wx.EVT_BUTTON, self.Misc1 )
		self.m_button5.Bind( wx.EVT_BUTTON, self.MiscMessageBox )
		self.m_button6.Bind( wx.EVT_BUTTON, self.FileNew )
		self.m_button7.Bind( wx.EVT_BUTTON, self.FileLoad )
	
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
	
	def Misc1( self, event ):
		event.Skip()
	
	def MiscMessageBox( self, event ):
		event.Skip()
	
	
	

