from base_cmd import CmdBase
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
            def OnClassNameEnter( self, event ):
                self.EndModal(wx.ID_OK) 
        dialog = EditDialog(None)

        dialog.txtClassName.Value, dialog.txtAttrs.Value, dialog.txtMethods.Value = id, "\n".join(attrs), "\n".join(methods)
        if dialog.ShowModal() == wx.ID_OK:
            #wx.MessageBox("got wx.ID_OK")
            result = True
            id = dialog.txtClassName.Value

            def string_to_list_smart(s):
                s = s.strip()
                if s == "":
                    return []
                else:
                    return s.split('\n')

            attrs = string_to_list_smart(dialog.txtAttrs.Value)
            methods = string_to_list_smart(dialog.txtMethods.Value)
            print id, attrs, methods
        else:
            result, id, attrs, methods = False, None, None, None
        dialog.Destroy()
        return (result, id, attrs, methods)


class CmdInsertUmlClass(UtilCmdUmlClass):
    """ Insert new node """
    def execute(self):
        """ insert the new node and refresh the ascii tab too """
        umlwin = self.context.umlwin
        wxapp = self.context.wxapp
        model = self.context.model
        
        #self.umlwin.CmdInsertNewNode()
        
        result, id, attrs, methods = self.display_dialog(id='D' + str(random.randint(1,99)),
                                            attrs=['attribute 1', 'attribute 2', 'attribute 3'],
                                            methods=['method A', 'method B', 'method C', 'method D'])

        if result:
            # Ensure unique name
            while model.graph.FindNodeById(id):
                id += '2'

            node = model.AddUmlNode(id, attrs, methods)
            shape = umlwin.CreateUmlShape(node)
            model.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            
            node.shape.Show(True)
            
            umlwin.remove_overlaps()
            umlwin.mega_refresh()

            umlwin.SelectNodeNow(node.shape)

            # wxapp.RefreshAsciiUmlTab()  # Don't do this because somehow the onKeyChar and onKeyPress handlers are unbound from the UmlCanvas shape canvas

    def undo(self):  # override
        """ undo insert new node """
        # not implemented


class CmdEditUmlClass(UtilCmdUmlClass):  # TODO rename CmdEditUmlItem cos can apply to classes or comments
    """ Edit node properties """

    def __init__(self, shape):
        self.shape = shape

    def execute(self):
        """  """
        umlwin = self.context.umlwin
        wxapp = self.context.wxapp
        model = self.context.model
        shape = self.shape
        gui = self.context.umlwin

        node = shape.node

        # node is a regular node, its the node.shape that is different for a comment
        if isinstance(node.shape, DividedShape):
            result, id, attrs, methods = self.display_dialog(node.id, node.attrs,
                                                                       node.meths)
            if result:
                model.graph.RenameNode(node,
                                       id)  # need special rename cos of underlying graph plumbing - perhaps put setter on id?
                node.attrs = attrs
                node.meths = methods

                model.decouple_node_from_shape(shape)
                gui.delete_shape_view(shape)

                shape = umlwin.CreateUmlShape(node)
                model.classnametoshape[
                    node.id] = shape  # Record the name to shape map so that we can wire up the links later.

                # TODO Hmmm - how does new shape get hooked up if the line mapping uses old name!??  Cos of graph's edge info perhaps?
                for edge in model.graph.edges:
                    umlwin.CreateUmlEdge(edge)

                node.shape.Show(True)
                umlwin.mega_refresh()

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
            comment = dialog.txt_comment.GetValue()
            result = True
        else:
            result, comment = False, None
        dialog.Destroy()
        return (result, comment)


class CmdInsertComment(UtilCmdComment):
    """ Insert comment """

    def execute_v1(self):
        """
        Pops up a comment dialog box, creates both a graph node and a shape,
        associates them, then adds them to the `self.context.model.classnametoshape` mapping.
        """

        id = 'D' + str(random.randint(1, 9999))

        # Old single line dialog - using built in dialog
        # dialog = wx.TextEntryDialog ( None, 'Enter a comment:', 'New Comment', "hello\nthere", style=wx.TE_MULTILINE)
        # dialog.SetSize((200, 100))

        # Custom dialog built via wxformbuilder - subclass it first, to hook up event handlers
        class EditDialog(DialogComment):
            def OnClassNameEnter(self, event):
                self.EndModal(wx.ID_OK)

        dialog = EditDialog(None)
        dialog.txt_comment.SetFocus()

        if dialog.ShowModal() == wx.ID_OK:
            comment = dialog.txt_comment.GetValue()
            # wx.MessageBox("got wx.ID_OK " + comment)

            node = self.context.model.AddCommentNode(id, comment)
            shape = self.context.umlwin.createCommentShape(node)
            self.context.model.classnametoshape[
                node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            node.shape.Show(True)
            self.context.umlwin.mega_refresh()
        dialog.Destroy()

    def execute(self):
        """
        Pops up a comment dialog box, creates both a graph node and a shape,
        associates them, then adds them to the `self.context.model.classnametoshape` mapping.
        """

        id = 'C' + str(random.randint(1, 9999))
        result, comment = self.display_dialog(comment="initial comment")
        if result:
            # Ensure unique name
            while self.context.model.graph.FindNodeById(id):
                id += '2'
            node = self.context.model.AddCommentNode(id, comment)
            shape = self.context.umlwin.createCommentShape(node)
            self.context.model.classnametoshape[
                node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            node.shape.Show(True)
            self.context.umlwin.mega_refresh()


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
        
        thisdir = config.get('LastDirInsertImage', '.') # remember dir path
        dlg = wx.FileDialog(parent=frame, message="choose", defaultDir=thisdir,
            defaultFile="", wildcard="*.jpg", style=wx.FC_OPEN, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            config['LastDirInsertImage'] = dlg.GetDirectory()  # remember dir path
            config.write()
        dlg.Destroy()
        
        self.create_new_image_node(filename)

    def create_new_image_node(self, filename=None):
        import os
        if not filename:
            curr_dir = os.path.dirname( os.path.abspath( __file__ ) )
            filename = os.path.join(curr_dir, '..\\..\..\\Research\\wx doco\\Images\\SPLASHSCREEN.BMP')
            print filename
            
        self.context.umlwin.CreateImageShape(filename)
        self.context.umlwin.remove_overlaps()
        self.context.umlwin.mega_refresh()
        #self.SelectNodeNow(node.shape)
        
    def undo(self):  # override
        """ Docstring """
        # not implemented
        

