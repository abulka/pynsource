from base_cmd import CmdBase

# Cannot multi-select nodes at present.

class CmdNodeDeleteBase(CmdBase):

    def execute(self):
        raise "virtual"
    
    def undo(self):  # override
        """ Docstring """
        # not implemented

    def delete_shape(self, shape):
        model = self.context.model
        gui = self.context.umlwin
        
        model.delete_node_for_shape(shape)
        gui.delete_shape_view(shape)
        
        
class CmdNodeDelete(CmdNodeDeleteBase):
    """ Delete specific shape/node. """

    def __init__(self, context, shape):
        """ pass in all the relevant context as well as the shape/class """
        super(CmdNodeDelete, self).__init__(context)
        self.shape = shape

    def execute(self):
        """ Delete specific shape/node. """
        self.delete_shape(self.shape)
        
class CmdNodeDeleteSelected(CmdNodeDeleteBase):
    """ Delete selected node """

    def execute(self):
        """ Delete selected node. """
        selected = [s for s in self.context.umlwin.GetDiagram().GetShapeList() if s.Selected()]
        if selected:
            shape = selected[0]
            self.delete_shape(shape)

        
