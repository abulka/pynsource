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
		self.m_menu2 = wx.Menu()
		self.m_menuItem15 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Import Python Source..."+ u"\t" + u"Ctrl+I", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.AppendItem( self.m_menuItem15 )
		
		self.m_menu2.AppendSeparator()
		
		self.m_menuItem16 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"New"+ u"\t" + u"Ctrl+N", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.AppendItem( self.m_menuItem16 )
		
		self.m_menuItem17 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Open..."+ u"\t" + u"Ctrl-O", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.AppendItem( self.m_menuItem17 )
		
		self.m_menuItem18 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Save"+ u"\t" + u"Ctrl-S", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.AppendItem( self.m_menuItem18 )
		
		self.m_menuItem21 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Save As...", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.AppendItem( self.m_menuItem21 )
		
		self.m_menu2.AppendSeparator()
		
		self.m_menuItem20 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Print / Print Preview..."+ u"\t" + u"Ctrl-P", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.AppendItem( self.m_menuItem20 )
		
		self.m_menu2.AppendSeparator()
		
		self.m_menuItem19 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Exit"+ u"\t" + u"Alt+F4", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.AppendItem( self.m_menuItem19 )
		
		self.m_menubar4.Append( self.m_menu2, u"File" ) 
		
		self.m_menu6 = wx.Menu()
		self.m_menuItem26 = wx.MenuItem( self.m_menu6, wx.ID_ANY, u"Add Class..."+ u"\t" + u"Ins", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu6.AppendItem( self.m_menuItem26 )
		
		self.m_menuItem14 = wx.MenuItem( self.m_menu6, wx.ID_ANY, u"Delete Class"+ u"\t" + u"Del", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu6.AppendItem( self.m_menuItem14 )
		
		self.m_menu6.AppendSeparator()
		
		self.m_menuItem29 = wx.MenuItem( self.m_menu6, wx.ID_ANY, u"Class Properties..."+ u"\t" + u"a", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu6.AppendItem( self.m_menuItem29 )
		
		self.m_menuItem28 = wx.MenuItem( self.m_menu6, wx.ID_ANY, u"Class Source Code..."+ u"\t" + u"s", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu6.AppendItem( self.m_menuItem28 )
		
		self.m_menubar4.Append( self.m_menu6, u"Edit" ) 
		
		self.m_menu7 = wx.Menu()
		self.m_menuItem81 = wx.MenuItem( self.m_menu7, wx.ID_ANY, u"Layout"+ u"\t" + u"L", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu7.AppendItem( self.m_menuItem81 )
		
		self.m_menuItem35 = wx.MenuItem( self.m_menu7, wx.ID_ANY, u"Layout Optimal (slower)", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu7.AppendItem( self.m_menuItem35 )
		
		self.m_menu7.AppendSeparator()
		
		self.m_menuItem30 = wx.MenuItem( self.m_menu7, wx.ID_ANY, u"Increase Node Spread"+ u"\t" + u"x", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu7.AppendItem( self.m_menuItem30 )
		
		self.m_menuItem31 = wx.MenuItem( self.m_menu7, wx.ID_ANY, u"Decrease Node Spread"+ u"\t" + u"z", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu7.AppendItem( self.m_menuItem31 )
		
		self.m_menu7.AppendSeparator()
		
		self.m_menuItem24 = wx.MenuItem( self.m_menu7, wx.ID_ANY, u"UML", wx.EmptyString, wx.ITEM_CHECK )
		self.m_menu7.AppendItem( self.m_menuItem24 )
		self.m_menuItem24.Enable( False )
		self.m_menuItem24.Check( True )
		
		self.m_menuItem22 = wx.MenuItem( self.m_menu7, wx.ID_ANY, u"Ascii Art Uml", wx.EmptyString, wx.ITEM_CHECK )
		self.m_menu7.AppendItem( self.m_menuItem22 )
		
		self.m_menuItem23 = wx.MenuItem( self.m_menu7, wx.ID_ANY, u"yUml", wx.EmptyString, wx.ITEM_CHECK )
		self.m_menu7.AppendItem( self.m_menuItem23 )
		
		self.m_menu7.AppendSeparator()
		
		self.m_menuItem7 = wx.MenuItem( self.m_menu7, wx.ID_ANY, u"Redraw Screen"+ u"\t" + u"r", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu7.AppendItem( self.m_menuItem7 )
		
		self.m_menubar4.Append( self.m_menu7, u"View" ) 
		
		self.m_menu8 = wx.Menu()
		self.m_menuItem9 = wx.MenuItem( self.m_menu8, wx.ID_ANY, u"Help..."+ u"\t" + u"F1", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu8.AppendItem( self.m_menuItem9 )
		
		self.m_menuItem11 = wx.MenuItem( self.m_menu8, wx.ID_ANY, u"Visit PyNSource Website...", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu8.AppendItem( self.m_menuItem11 )
		
		self.m_menu8.AppendSeparator()
		
		self.m_menuItem12 = wx.MenuItem( self.m_menu8, wx.ID_ANY, u"Check for Updates...", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu8.AppendItem( self.m_menuItem12 )
		
		self.m_menuItem13 = wx.MenuItem( self.m_menu8, wx.ID_ANY, u"About...", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu8.AppendItem( self.m_menuItem13 )
		
		self.m_menubar4.Append( self.m_menu8, u"Help" ) 
		
		self.m_menu5 = wx.Menu()
		self.m_menuItem8 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Show Pane", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem8 )
		
		self.m_menuItem2 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Add Pane", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem2 )
		
		self.m_menuItem6 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Add Pane (float)", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem6 )
		
		self.m_menuItem3 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Fold1", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem3 )
		
		self.m_menuItem4 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Fold All", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem4 )
		
		self.m_menuItem5 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Hier", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.AppendItem( self.m_menuItem5 )
		
		self.m_menubar4.Append( self.m_menu5, u"Debug" ) 
		
		self.SetMenuBar( self.m_menubar4 )
		
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.canvas = ogl.ShapeCanvas( self )
		diagram = ogl.Diagram()
		self.canvas.SetDiagram( diagram )
		diagram.SetCanvas( self.canvas )
		self.m_mgr.AddPane( self.canvas, wx.aui.AuiPaneInfo() .Left() .Caption( u"UML" ).MaximizeButton( False ).MinimizeButton( False ).PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ).CentrePane() )
		
		self.m_auiToolBar2 = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT ) 
		self.m_auiToolBar2.AddTool( wx.ID_ANY, u"sssddddd", wx.Bitmap( u"icons22/kcmscsi.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"ssss", wx.EmptyString, None)
		self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons22/kmoon.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None)
		self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons22/kalzium.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None)
		self.m_auiToolBar2.AddSeparator()
		self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons22/kedit.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None)
		self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons22/kcmprocessor.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None)
		self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons22/kcmmidi.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None)
		self.m_auiToolBar2.Realize()
		self.m_mgr.AddPane( self.m_auiToolBar2, wx.aui.AuiPaneInfo().Top().CaptionVisible( False ).CloseButton( False ).MaximizeButton( False ).MinimizeButton( False ).PinButton( False ).PaneBorder( False ).Movable( False ).Dock().Fixed().DockFixed( False ).Floatable( False ).Layer( 1 ) )
		
		
		self.m_mgr.Update()
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_MENU, self.OnShowPane, id = self.m_menuItem8.GetId() )
		self.Bind( wx.EVT_MENU, self.OnAddPane, id = self.m_menuItem2.GetId() )
		self.Bind( wx.EVT_MENU, self.OnAddPaneFloat, id = self.m_menuItem6.GetId() )
		self.Bind( wx.EVT_MENU, self.OnFold1, id = self.m_menuItem3.GetId() )
		self.Bind( wx.EVT_MENU, self.OnFoldAll, id = self.m_menuItem4.GetId() )
		self.Bind( wx.EVT_MENU, self.OnHier, id = self.m_menuItem5.GetId() )
	
	def __del__( self ):
		self.m_mgr.UnInit()
		
	
	
	# Virtual event handlers, overide them in your derived class
	def OnShowPane( self, event ):
		event.Skip()
	
	def OnAddPane( self, event ):
		event.Skip()
	
	def OnAddPaneFloat( self, event ):
		event.Skip()
	
	def OnFold1( self, event ):
		event.Skip()
	
	def OnFoldAll( self, event ):
		event.Skip()
	
	def OnHier( self, event ):
		event.Skip()
	

