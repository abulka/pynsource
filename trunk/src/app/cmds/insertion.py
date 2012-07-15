import sys
if ".." not in sys.path: sys.path.append("..")
from base_cmd import CmdBase
import wx
import random

class CmdInsertNewComment(CmdBase):
    """ Insert node """

    def execute(self):
        """ insert comment node """
        assert self.umlwin
        self.umlwin.CmdInsertNewComment()
            
    def undo(self):  # override
        """ undo insert new comment """
        # not implemented


class CmdInsertOrEditNode(CmdBase):
    def DisplayDialogUmlNodeEdit(self, id, attrs, methods):
        """
        id, attrs, methods are lists of strings
        returns id, attrs, methods as lists of strings
        """
        from dialogs.DialogUmlNodeEdit import DialogUmlNodeEdit
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


class CmdInsertNewNode(CmdInsertOrEditNode):
    """ Insert new node """

    def __init__(self, umlwin, wxapp, umlworkspace):
        """ pass in all the relevant context """
        super(CmdInsertNewNode, self).__init__(umlwin)
        self.wxapp = wxapp
        self.umlworkspace = umlworkspace

    def execute(self):
        """ insert the new node and refresh the ascii tab too """
        assert self.umlwin
        assert self.wxapp
        assert self.umlworkspace
        
        #self.umlwin.CmdInsertNewNode()
        
        result, id, attrs, methods = self.DisplayDialogUmlNodeEdit(id='D' + str(random.randint(1,99)),
                                            attrs=['attribute 1', 'attribute 2', 'attribute 3'],
                                            methods=['method A', 'method B', 'method C', 'method D'])

        if result:
            # Ensure unique name
            while self.umlworkspace.graph.FindNodeById(id):
                id += '2'

            node = self.umlworkspace.AddUmlNode(id, attrs, methods)
            shape = self.umlwin.CreateUmlShape(node)
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
            
            node.shape.Show(True)
            
            #self.umlwin.stateofthenation() # if want simple refresh
            #self.umlwin.stage2() # if want overlap removal
            self.umlwin.stage2(force_stateofthenation=True) # if want overlap removal and proper refresh
            
            self.umlwin.SelectNodeNow(node.shape)        
        
            self.wxapp.RefreshAsciiUmlTab()

    def undo(self):  # override
        """ undo insert new node """
        # not implemented


class CmdEditShape(CmdInsertOrEditNode):
    """ Edit node properties """

    def __init__(self, umlwin, wxapp, umlworkspace, shape):
        """ pass in all the relevant context """
        super(CmdEditShape, self).__init__(umlwin)
        self.wxapp = wxapp
        self.umlworkspace = umlworkspace
        self.shape = shape

    def execute(self):
        """  """
        assert self.umlwin
        assert self.wxapp
        assert self.umlworkspace
        assert self.shape

        node = self.shape.node
         
        result, id, attrs, methods = self.DisplayDialogUmlNodeEdit(node.id, node.attrs, node.meths)
        if result:
            self.umlworkspace.graph.RenameNode(node, id)   # need special rename cos of underlying graph plumbing - perhaps put setter on id?
            node.attrs = attrs
            node.meths = methods
    
            self.umlwin.CmdZapShape(self.shape, deleteNodeToo=False)  # TODO turn this into a sub command
            
            shape = self.umlwin.CreateUmlShape(node)
            self.umlworkspace.classnametoshape[node.id] = shape  # Record the name to shape map so that we can wire up the links later.
    
            # TODO Hmmm - how does new shape get hooked up if the line mapping uses old name!??  Cos of graph's edge info perhaps?
            for edge in self.umlworkspace.graph.edges:
                self.umlwin.CreateUmlEdge(edge)
                
            node.shape.Show(True)
            self.umlwin.stateofthenation()

            # TODO Why doesn't this select the node?
            #self.SelectNodeNow(node.shape)
            #self.stateofthenation()

    def undo(self):  # override
        """ undo insert new node """
        # not implemented


class CmdInsertImage(CmdBase):
    """ Insert image """

    def __init__(self, umlwin, frame, config):
        """ pass in all the relevant context """
        super(CmdInsertImage, self).__init__(umlwin)
        self.config = config
        self.frame = frame

    def execute(self):
        """ Docstring """
        assert self.umlwin
        assert self.config

        filename = None
        
        thisdir = self.config.get('LastDirInsertImage', '.') # remember dir path
        dlg = wx.FileDialog(parent=self.frame, message="choose", defaultDir=thisdir,
            defaultFile="", wildcard="*.jpg", style=wx.OPEN, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            self.config['LastDirInsertImage'] = dlg.GetDirectory()  # remember dir path
            self.config.write()
        dlg.Destroy()
        
        self.umlwin.CmdInsertNewImageNode(filename)
            
    def undo(self):  # override
        """ Docstring """
        # not implemented
        

