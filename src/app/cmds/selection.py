from base_cmd import CmdBase
import wx

class CmdDeselectAllShapes(CmdBase):
    def execute(self):
        selected = [s for s in self.context.umlwin.GetDiagram().GetShapeList() if s.Selected()]
        if selected:
            assert len(selected) == 1
            s = selected[0]
            canvas = s.GetCanvas()
            
            dc = wx.ClientDC(canvas)
            canvas.PrepareDC(dc)
            s.Select(False, dc)
            canvas.Refresh(False)   # Need this or else Control points ('handles') leave blank holes
    
    def undo(self):  # override
        """ Docstring """
        # not implemented
