from .base_cmd import CmdBase

# Cannot multi-select nodes at present.


class CmdNodeDeleteBase(CmdBase):
    def delete_shape(self, shape):
        displaymodel = self.context.displaymodel
        gui = self.context.umlcanvas

        # Currently images are not nodes, just shapes, so skip deleting the node
        if shape.GetShape().__class__.__name__ != "BitmapShapeResizable":
            displaymodel.delete_node_or_edge_for_shape(shape)

        gui.delete_shape_view(shape)

        self.context.umlcanvas.extra_refresh()
        self.context.umlcanvas.Refresh()  # needed for ogltwo
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
