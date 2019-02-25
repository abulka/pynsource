from .base_cmd import CmdBase
import wx
import random
from dialogs.DialogComment import DialogComment
from dialogs.DialogUmlNodeEdit import DialogUmlNodeEdit
from typing import List, Set, Dict, Tuple, Optional
import copy
from gui.settings import PRO_EDITION


"""
Inserting and editing 
    - regular UML Class nodes/shapes
    - comments
    - images (no editing)
"""


class UtilCmdUmlClass(CmdBase):  # Not Used directly, please subclass
    def display_dialog(self, id, attrs, methods):
        """
        Show uml class editor dialog

        Args:
            id: id of node (txtClassName - I think this is the name of the class !!)
            attrs: lists of strings
            methods: lists of strings

        Returns: (result, id, attrs, methods) where
            result is whether there was a successful edit?
            attrs, methods as lists of strings

        """

        class EditDialog(DialogUmlNodeEdit):
            def OnClassNameEnter(self, event):
                self.EndModal(wx.ID_OK)

        dialog = EditDialog(None)

        dialog.txtClassName.Value, dialog.txtAttrs.Value, dialog.txtMethods.Value = (
            id,
            "\n".join(attrs),
            "\n".join(methods),
        )
        if dialog.ShowModal() == wx.ID_OK:
            # wx.MessageBox("got wx.ID_OK")
            result = True
            id = dialog.txtClassName.Value

            def string_to_list_smart(s):
                s = s.strip()
                if s == "":
                    return []
                else:
                    return s.split("\n")

            attrs = string_to_list_smart(dialog.txtAttrs.Value)
            methods = string_to_list_smart(dialog.txtMethods.Value)
            # print("display_dialog", id, attrs, methods)
        else:
            result, id, attrs, methods = False, None, None, None
        dialog.Destroy()
        return (result, id, attrs, methods)


class CmdInsertUmlClass(UtilCmdUmlClass):
    """ Insert new node """

    def execute(self):
        """ insert the new node and refresh the ascii tab too """
        umlcanvas = self.context.umlcanvas
        wxapp = self.context.wxapp
        displaymodel = self.context.displaymodel

        # self.umlcanvas.CmdInsertNewNode()

        result, id, attrs, methods = self.display_dialog(
            id="D" + str(random.randint(1, 99)),
            attrs=["attribute 1", "attribute 2", "attribute 3"],
            methods=["method A", "method B", "method C", "method D"],
        )

        if result:
            # Ensure unique name
            while displaymodel.graph.FindNodeById(id):
                id += "2"

            node = displaymodel.AddUmlNode(id, attrs, methods)
            shape = umlcanvas.CreateUmlShape(node)

            node.shape.Show(True)
            umlcanvas.remove_overlaps()
            umlcanvas.mega_refresh()
            umlcanvas.SelectNodeNow(node.shape)
            # wxapp.RefreshAsciiUmlTab()  # Don't do this because somehow the onKeyChar and onKeyPress handlers are unbound from the UmlCanvas shape canvas

    def undo(self):  # override
        """ undo insert new node """
        # not implemented


class CmdEditUmlClass(UtilCmdUmlClass):
    """ Edit node properties """

    def __init__(self, shape):
        self.shape = shape

    def execute(self):
        """  """
        umlcanvas = gui = self.context.umlcanvas
        displaymodel = self.context.displaymodel
        shape = self.shape
        node = shape.node

        result, id, attrs, methods = self.display_dialog(node.id, node.attrs, node.meths)
        if result:
            displaymodel.graph.RenameNode(
                node, id
            )  # id is same as uml class name being represented
            node.attrs = attrs
            node.meths = methods

            shape.ClearRegions()
            umlcanvas.CreateUmlShape(node, update_existing_shape=shape)
            umlcanvas.mega_refresh()

    def undo(self):  # override
        """ undo insert new node """
        # not implemented


"""
Insert and edit Comment nodes/shapes
"""


class UtilCmdComment(CmdBase):  # Not Used directly, please subclass
    def display_dialog(self, comment):
        """
        Displays dialog for editing comments

        Args:
            comment: comment string

        Returns: (result, comment)
        """

        class EditDialog(DialogComment):
            # Custom dialog built via wxformbuilder - subclass it first, to hook up event handlers
            def OnClassNameEnter(self, event):
                self.EndModal(wx.ID_OK)

        dialog = EditDialog(None)
        dialog.txt_comment.Value = comment
        dialog.txt_comment.SetFocus()
        if dialog.ShowModal() == wx.ID_OK:
            comment = self.sanitise_comment(dialog.txt_comment.GetValue())
            result = True
        else:
            result, comment = False, None
        dialog.Destroy()
        return (result, comment)

    def sanitise_comment(self, txt):
        """Remove any tabs and trailing cr from comments, as they mess up shape text display"""
        return txt.replace("\t", "    ").rstrip()


class CmdInsertComment(UtilCmdComment):
    """ Insert comment """

    def execute(self):
        """
        Pops up a comment dialog box, creates both a graph node and a shape, and associates them
        """

        id = "C" + str(random.randint(1, 9999))
        result, comment = self.display_dialog(comment="initial comment")
        if result:
            # Ensure unique name
            while self.context.displaymodel.graph.FindNodeById(id):
                id += "2"
            node = self.context.displaymodel.AddCommentNode(id, comment)
            shape = self.context.umlcanvas.createCommentShape(node)

            node.shape.Show(True)
            self.context.umlcanvas.mega_refresh()


class CmdEditComment(UtilCmdComment):
    """ Edit node properties """

    def __init__(self, shape):
        self.shape = shape

    def execute(self):
        shape = self.shape
        umlcanvas = gui = self.context.umlcanvas
        node = shape.node

        result, comment = self.display_dialog(node.comment)
        if result:
            node.comment = comment
            shape.ClearText()
            shape.AddText(node.comment)
            umlcanvas.mega_refresh()

    def undo(self):  # override
        """ undo insert new node """
        # not implemented


"""
Insert and edit Image shapes
"""


class CmdInsertImage(CmdBase):
    """ Insert image """

    def execute(self):
        """ Docstring """
        frame = self.context.frame
        config = self.context.config

        filename = None

        thisdir = config.get("LastDirInsertImage", ".")  # remember dir path
        dlg = wx.FileDialog(
            parent=frame,
            message="choose",
            defaultDir=thisdir,
            defaultFile="",
            wildcard="Jpeg files|*.jpg;*.jpeg|(*.png)|*.png|(*.bmp)|*.bmp",
            style=wx.FC_OPEN,
            pos=wx.DefaultPosition,
        )
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            config["LastDirInsertImage"] = dlg.GetDirectory()  # remember dir path
            config.write()
            self.create_new_image_node(filename)
        dlg.Destroy()


    def create_new_image_node(self, filename=None):
        import os

        if filename:
            self.context.umlcanvas.CreateImageShape(filename)
            self.context.umlcanvas.remove_overlaps()
            self.context.umlcanvas.mega_refresh()
            # self.SelectNodeNow(node.shape)

    def undo(self):  # override
        """ Docstring """
        # not implemented


"""
Duplicate
"""

class CmdDuplicate(UtilCmdUmlClass):
    """ Duplicate UML class"""

    def execute(self):
        """ insert the new node and refresh the ascii tab too """
        umlcanvas = self.context.umlcanvas
        wxapp = self.context.wxapp
        displaymodel = self.context.displaymodel

        selected = [s for s in umlcanvas.GetDiagram().GetShapeList() if s.Selected()]
        for shape in selected:

            if not hasattr(shape, "node"):
                self.context.wxapp.MessageBox("Duplicating images currently not supported, sorry.")
                return

            node = shape.node

            # pick the next name
            found = False
            for i in range(999):
                id = f"{node.id}_copy{i}"
                if id not in displaymodel.graph.nodeSet:
                    found = True
                    break
            if not found:
                id = node.id + "_copy" + str(random.randint(1, 99999))
            # Ensure unique name
            while displaymodel.graph.FindNodeById(id):
                id += "2"


            if hasattr(node, "attrs"):
                attrs = copy.copy(node.attrs)
                methods = copy.copy(node.meths)
                new_node = displaymodel.AddUmlNode(id, attrs, methods)
                self.adjust_node_position_slightly(node, new_node)
                new_shape = umlcanvas.CreateUmlShape(new_node)
            elif hasattr(node, "comment"):
                comment = copy.copy(node.comment)
                new_node = displaymodel.AddCommentNode(id, comment)
                self.adjust_node_position_slightly(node, new_node)
                new_shape = umlcanvas.createCommentShape(new_node)
            else:
                print("Image duplication currently not supported")


            new_node.shape.Show(True)
            if PRO_EDITION:
                umlcanvas.diagram.ChangeShapeOrder(new_node.shape, 9999)

            # umlcanvas.remove_overlaps()
            umlcanvas.mega_refresh()

    def adjust_node_position_slightly(self, node, new_node):
        """Position the new shape slightly below the old one, but the same size"""
        offsetx = random.randint(2, 20)
        offsety = random.randint(-int(node.height/3), int(node.height/3))
        new_node.left = node.left + node.width + offsetx
        new_node.top = node.top + offsety
        new_node.width = node.width
        new_node.height = node.height

    def undo(self):  # override
        """ undo insert new node """
        # not implemented

