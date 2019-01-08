from .base_cmd import CmdBase
import wx
import random
from dialogs.DialogComment import DialogComment
from gui.uml_shapes import DividedShape
from dialogs.DialogUmlNodeEdit import DialogUmlNodeEdit


"""
Inserting and editing regular UML Class nodes/shapes

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
            print(id, attrs, methods)
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
            displaymodel.classnametoshape[
                node.id
            ] = shape  # Record the name to shape map so that we can wire up the links later.

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
        wxapp = self.context.wxapp
        displaymodel = self.context.displaymodel
        shape = self.shape

        node = shape.node

        # node is a regular node, its the node.shape that is different for a comment
        if isinstance(node.shape, DividedShape):
            result, id, attrs, methods = self.display_dialog(node.id, node.attrs, node.meths)
            if result:
                displaymodel.graph.RenameNode(
                    node, id
                )  # need special rename cos of underlying graph plumbing - perhaps put setter on id?
                node.attrs = attrs
                node.meths = methods

                displaymodel.decouple_node_from_shape(shape)
                gui.delete_shape_view(shape)

                shape = umlcanvas.CreateUmlShape(node)
                displaymodel.classnametoshape[
                    node.id
                ] = shape  # Record the name to shape map so that we can wire up the links later.

                # TODO Hmmm - how does new shape get hooked up if the line mapping uses old name!??  Cos of graph's edge info perhaps?
                for edge in displaymodel.graph.edges:
                    umlcanvas.CreateUmlEdge(edge)

                node.shape.Show(True)
                umlcanvas.mega_refresh()

                # TODO Why doesn't this select the node?
                # self.SelectNodeNow(node.shape)
                # self.mega_refresh()
        else:
            # Comment node
            wx.MessageBox(node.comment)

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
        Pops up a comment dialog box, creates both a graph node and a shape,
        associates them, then adds them to the `self.context.displaymodel.classnametoshape` mapping.
        """

        id = "C" + str(random.randint(1, 9999))
        result, comment = self.display_dialog(comment="initial comment")
        if result:
            # Ensure unique name
            while self.context.displaymodel.graph.FindNodeById(id):
                id += "2"
            node = self.context.displaymodel.AddCommentNode(id, comment)
            shape = self.context.umlcanvas.createCommentShape(node)
            self.context.displaymodel.classnametoshape[
                node.id
            ] = shape  # Record the name to shape map so that we can wire up the links later.
            node.shape.Show(True)
            self.context.umlcanvas.mega_refresh()


class CmdEditComment(UtilCmdComment):
    """ Edit node properties """

    def __init__(self, shape):
        self.shape = shape

    def execute(self):
        """  """
        umlcanvas = gui = self.context.umlcanvas
        wxapp = self.context.wxapp
        displaymodel = self.context.displaymodel
        shape = self.shape

        node = shape.node

        # node is a regular node, its the node.shape that is different for a comment
        assert not isinstance(node.shape, DividedShape)

        result, comment = self.display_dialog(node.comment)

        # TODO review this code !!!!! and also need to call this class instead of the above umlclass class
        # somehow - perhaps by checking in the GUI invoker of the type.
        # also make comment shape unique - not just a rectangle.
        if result:
            node.comment = comment

            displaymodel.decouple_node_from_shape(shape)
            gui.delete_shape_view(shape)

            shape = umlcanvas.createCommentShape(node)
            displaymodel.classnametoshape[
                node.id
            ] = shape  # Record the name to shape map so that we can wire up the links later.

            # # TODO Hmmm - how does new shape get hooked up if the line mapping uses old name!??  Cos of graph's edge info perhaps?
            # for edge in model.graph.edges:
            #     umlcanvas.CreateUmlEdge(edge)

            node.shape.Show(True)
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
            wildcard="*.jpg",
            style=wx.FC_OPEN,
            pos=wx.DefaultPosition,
        )
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            config["LastDirInsertImage"] = dlg.GetDirectory()  # remember dir path
            config.write()
        dlg.Destroy()

        self.create_new_image_node(filename)

    def create_new_image_node(self, filename=None):
        import os

        if not filename:
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(
                curr_dir, "..\\..\..\\Research\\wx doco\\Images\\SPLASHSCREEN.BMP"
            )
            print(filename)

        self.context.umlcanvas.CreateImageShape(filename)
        self.context.umlcanvas.remove_overlaps()
        self.context.umlcanvas.mega_refresh()
        # self.SelectNodeNow(node.shape)

    def undo(self):  # override
        """ Docstring """
        # not implemented
