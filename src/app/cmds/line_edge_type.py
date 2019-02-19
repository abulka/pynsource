from .base_cmd import CmdBase
import wx
import random
from typing import List, Set, Dict, Tuple, Optional
from gui.settings import PRO_EDITION


class UtilCmdLineChange(CmdBase):  # Not Used directly, please subclass

    def __init__(self, shape, edge_type=""):
        self.shape = shape
        self.edge_type = edge_type

    def recreate_line_shape(self, line_shape, edge):
        umlcanvas = self.context.umlcanvas

        # delete the shape
        umlcanvas.delete_shape_view(line_shape)
        edge["shape"] = None
        # and rebuild the shape again
        umlcanvas.CreateUmlEdgeShape(edge)
        new_line_shape = edge["shape"]
        # Yuk - different logic for different underlying ogl - handler stuff is particularly gnarly
        if PRO_EDITION:
            new_line_shape._SelectNodeNow(event=None)
            umlcanvas.Refresh()
        else:
            new_line_shape.GetEventHandler()._SelectNodeNow(x=None, y=None)
            umlcanvas.mega_refresh()

    def swap_edge_direction(self):
        umlcanvas = self.context.umlcanvas
        displaymodel = self.context.displaymodel

        edge: Dict = displaymodel.graph.find_edge_for_lineshape(self.shape)
        edge["source"], edge["target"] = edge["target"], edge["source"]


class CmdLineChangeToReverse(UtilCmdLineChange):

    def execute(self):
        displaymodel = self.context.displaymodel
        line_shape = self.shape
        self.swap_edge_direction()
        edge: Dict = displaymodel.graph.find_edge_for_lineshape(line_shape)
        self.recreate_line_shape(line_shape, edge)


class CmdLineChangeToEdgeType(UtilCmdLineChange):

    def execute(self):
        umlcanvas = self.context.umlcanvas
        displaymodel = self.context.displaymodel

        line_shape = self.shape
        edge: Dict = displaymodel.graph.find_edge_for_lineshape(line_shape)
        edge["uml_edge_type"] = self.edge_type
        self.recreate_line_shape(line_shape, edge)

    def undo(self):  # override
        """ undo insert new node """
        # not implemented


