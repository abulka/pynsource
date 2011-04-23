# prototype pynsource gui possibilities

import wx
from fbpyn1_gen import FramePyIdea_gen
import wx.lib.ogl as ogl

class FramePyIdea(FramePyIdea_gen):
    def OnShowSource( self, event ):
        print frame.m_mgr.GetAllPanes()
        print frame.m_mgr.GetPane('pane_code')
        #frame.m_mgr.RestorePane( frame.m_mgr.GetPane('pane_code') )
        print '-'*88
        print frame.m_mgr.GetAllPanes()
        print frame.m_mgr.GetPane('pane_code')
        frame.m_mgr.AddPane( frame.m_code, wx.aui.AuiPaneInfo() .Name( u"pane_code" ).Right() .Caption( u"Source Code" ).MaximizeButton( False ).MinimizeButton( False ).PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ) )

app = wx.App()
ogl.OGLInitialize()
frame = FramePyIdea(None)
frame.m_code.SetText(open(r'fbpyn1_gen.py').read())
frame.m_code.EmptyUndoBuffer()
frame.Show()

frame.canvas.SetBackgroundColour( "LIGHT BLUE" )
# Optional - add a shape
shape = ogl.RectangleShape( 60, 60 )
shape.SetX( 50 )
shape.SetY( 50 )
frame.canvas.AddShape( shape )
frame.canvas.GetDiagram().ShowAll(True)


app.MainLoop()