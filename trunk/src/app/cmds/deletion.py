from base_cmd import CmdBase

class CmdNodeDelete(CmdBase):
    """ Delete nodes """

    def execute(self):
        """ Delete selected node.  Cannot multi-select at present. """
        
        for shape in self.context.umlwin.GetDiagram().GetShapeList():
            if shape.Selected():
                self.context.umlwin.CmdZapShape(shape)

    def undo(self):  # override
        """ Docstring """
        # not implemented
        
