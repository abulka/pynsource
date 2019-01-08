# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Feb  9 2012)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class GuiFrame
###########################################################################

class GuiFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "HexMvc Architecture2 Gui", pos = wx.DefaultPosition, size = wx.Size( 500,439 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menuItem1FileNew = wx.MenuItem( self.m_menu1, wx.ID_ANY, "New", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.AppendItem( self.m_menuItem1FileNew )
		
		self.m_menubar1.Append( self.m_menu1, "File" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer10NewLoadSave = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button12 = wx.Button( self, wx.ID_ANY, "New / Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10NewLoadSave.Add( self.m_button12, 0, wx.ALL, 5 )
		
		self.m_button13 = wx.Button( self, wx.ID_ANY, "Load", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10NewLoadSave.Add( self.m_button13, 0, wx.ALL, 5 )
		
		self.m_button20 = wx.Button( self, wx.ID_ANY, "Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10NewLoadSave.Add( self.m_button20, 0, wx.ALL, 5 )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		
		bSizer10NewLoadSave.Add( bSizer6, 1, wx.EXPAND, 5 )
		
		
		bSizer4.Add( bSizer10NewLoadSave, 0, wx.EXPAND, 5 )
		
		bSizer21Dump = wx.BoxSizer( wx.VERTICAL )
		
		self.m_textCtrlDump = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		bSizer21Dump.Add( self.m_textCtrlDump, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer4.Add( bSizer21Dump, 1, wx.EXPAND, 5 )
		
		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button11 = wx.Button( self, wx.ID_ANY, "Dump Model", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button11, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( bSizer5, 1, wx.EXPAND, 5 )
		
		bSizer8Hyperlinks = wx.BoxSizer( wx.VERTICAL )
		
		self.m_hyperlink1 = wx.HyperlinkCtrl( self, wx.ID_ANY, "/", "http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8Hyperlinks.Add( self.m_hyperlink1, 0, wx.ALL, 5 )
		
		self.m_hyperlink2 = wx.HyperlinkCtrl( self, wx.ID_ANY, "/modelsize", "http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8Hyperlinks.Add( self.m_hyperlink2, 0, wx.ALL, 5 )
		
		self.m_hyperlink3 = wx.HyperlinkCtrl( self, wx.ID_ANY, "/dumpthings", "http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		bSizer8Hyperlinks.Add( self.m_hyperlink3, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( bSizer8Hyperlinks, 1, wx.EXPAND, 5 )
		
		
		bSizer4.Add( bSizer7, 0, wx.EXPAND, 5 )
		
		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer4.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer17Things = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizer18Commands = wx.BoxSizer( wx.VERTICAL )
		
		bSizer102Add = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button122 = wx.Button( self, wx.ID_ANY, "Add Thing", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer102Add.Add( self.m_button122, 0, wx.ALL, 5 )
		
		self.inputFieldTxt = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer102Add.Add( self.inputFieldTxt, 0, wx.ALL, 5 )
		
		
		bSizer18Commands.Add( bSizer102Add, 1, wx.EXPAND, 5 )
		
		bSizer101AddInfo = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button121 = wx.Button( self, wx.ID_ANY, "Add Info to Thing", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer101AddInfo.Add( self.m_button121, 0, wx.ALL, 5 )
		
		self.inputFieldTxtZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer101AddInfo.Add( self.inputFieldTxtZ, 0, wx.ALL, 5 )
		
		
		bSizer18Commands.Add( bSizer101AddInfo, 1, wx.EXPAND, 5 )
		
		bSizer20 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_button131 = wx.Button( self, wx.ID_ANY, "Delete Thing", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer20.Add( self.m_button131, 0, wx.ALL, 5 )
		
		
		bSizer18Commands.Add( bSizer20, 1, wx.EXPAND, 5 )
		
		bSizer9 = wx.BoxSizer( wx.VERTICAL )
		
		
		bSizer18Commands.Add( bSizer9, 1, wx.EXPAND, 5 )
		
		
		bSizer17Things.Add( bSizer18Commands, 1, wx.EXPAND, 5 )
		
		bSizer19Listbox = wx.BoxSizer( wx.VERTICAL )
		
		m_listBox1Choices = []
		self.m_listBox1 = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0 )
		bSizer19Listbox.Add( self.m_listBox1, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer17Things.Add( bSizer19Listbox, 1, wx.EXPAND, 5 )
		
		
		bSizer4.Add( bSizer17Things, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer4 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_MENU, self.OnFileNew, id = self.m_menuItem1FileNew.GetId() )
		self.m_button12.Bind( wx.EVT_BUTTON, self.OnFileNew )
		self.m_button11.Bind( wx.EVT_BUTTON, self.onDumpModel )
		self.m_button122.Bind( wx.EVT_BUTTON, self.OnAddThing )
		self.m_button121.Bind( wx.EVT_BUTTON, self.OnAddInfoToThing )
		self.m_button131.Bind( wx.EVT_BUTTON, self.OnDeleteThing )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnFileNew( self, event ):
		event.Skip()
	
	
	def onDumpModel( self, event ):
		event.Skip()
	
	def OnAddThing( self, event ):
		event.Skip()
	
	def OnAddInfoToThing( self, event ):
		event.Skip()
	
	def OnDeleteThing( self, event ):
		event.Skip()
	

###########################################################################
## Class MyMenuBar2
###########################################################################

class MyMenuBar2 ( wx.MenuBar ):
	
	def __init__( self ):
		wx.MenuBar.__init__ ( self, style = 0 )
		
	
	def __del__( self ):
		pass
	

###########################################################################
## Class MyMenuBar1
###########################################################################

class MyMenuBar1 ( wx.MenuBar ):
	
	def __init__( self ):
		wx.MenuBar.__init__ ( self, style = 0 )
		
	
	def __del__( self ):
		pass
	

