# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Mar 22 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.aui
from fbpyn1_scintilla import PythonSTC
import wx.lib.ogl as ogl

###########################################################################
## Class FramePyIdea_gen
###########################################################################

class FramePyIdea_gen ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"PyIdea UML", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.m_mgr = wx.aui.AuiManager()
		self.m_mgr.SetManagedWindow( self )
		
		self.m_code = PythonSTC(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		self.m_mgr.AddPane( self.m_code, wx.aui.AuiPaneInfo() .Name( u"pane_code" ).Right() .Caption( u"Source Code" ).MaximizeButton( False ).MinimizeButton( False ).PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ) )
		
		self.m_menubar4 = wx.MenuBar( 0 )
		self.m_menu5 = wx.Menu()
		self.m_menuItem8 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Show Source", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem8 )
		
		self.m_menuItem2 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Add Pane", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem2 )
		
		self.m_menuItem3 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Fold1", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem3 )
		
		self.m_menuItem4 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Fold All", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem4 )
		
		self.m_menuItem5 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Hier", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem5 )
		
		self.m_menubar4.Append( self.m_menu5, u"Debug" ) 
		
		self.SetMenuBar( self.m_menubar4 )
		
		self.canvas = ogl.ShapeCanvas( self )
		diagram = ogl.Diagram()
		self.canvas.SetDiagram( diagram )
		diagram.SetCanvas( self.canvas )
		self.m_mgr.AddPane( self.canvas, wx.aui.AuiPaneInfo() .Left() .Caption( u"UML" ).MaximizeButton( False ).MinimizeButton( False ).PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ).CentrePane() )
		
		
		self.m_mgr.Update()
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_MENU, self.OnShowSource, id = self.m_menuItem8.GetId() )
		self.Bind( wx.EVT_MENU, self.OnAddPane, id = self.m_menuItem2.GetId() )
		self.Bind( wx.EVT_MENU, self.OnFold1, id = self.m_menuItem3.GetId() )
		self.Bind( wx.EVT_MENU, self.OnFoldAll, id = self.m_menuItem4.GetId() )
		self.Bind( wx.EVT_MENU, self.OnHier, id = self.m_menuItem5.GetId() )
	
	def __del__( self ):
		self.m_mgr.UnInit()
		
	
	
	# Virtual event handlers, overide them in your derived class
	def OnShowSource( self, event ):
		event.Skip()
	
	def OnAddPane( self, event ):
		event.Skip()
	
	def OnFold1( self, event ):
		event.Skip()
	
	def OnFoldAll( self, event ):
		event.Skip()
	
	def OnHier( self, event ):
		event.Skip()
	

