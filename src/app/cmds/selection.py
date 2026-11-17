from .base_cmd import CmdBase
import wx

class CmdDeselectAllShapes(CmdBase):
    def execute(self):
        self.context.umlcanvas.deselect()

    def undo(self):  # override
        """ Docstring """
        # not implemented
