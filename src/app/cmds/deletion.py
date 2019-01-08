from .base_cmd import CmdBase

# Cannot multi-select nodes at present.


class CmdNodeDeleteBase(CmdBase):
    def delete_shape(self, shape):
        displaymodel = self.context.displaymodel
        gui = self.context.umlcanvas

        displaymodel.delete_node_for_shape(shape)
        gui.delete_shape_view(shape)

        self.context.frame.Layout()  # needed when running phoenix
        # self.context.umlcanvas.Refresh()
        # self.context.wxapp.RefreshAsciiUmlTab()


class CmdNodeDelete(CmdNodeDeleteBase):
    """ Delete specific shape/node. """

    def __init__(self, shape):
        self.shape = shape

    def execute(self):
        """ Delete specific shape/node. """
        self.delete_shape(self.shape)


class CmdNodeDeleteSelected(CmdNodeDeleteBase):
    """ Delete selected node """

    def execute(self):
        """ Delete selected node. """
        selected = [s for s in self.context.umlcanvas.GetDiagram().GetShapeList() if s.Selected()]
        if selected:
            shape = selected[0]
            self.delete_shape(shape)
