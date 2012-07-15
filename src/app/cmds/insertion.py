from base_cmd import CmdBase
import wx

class CmdInsertNewComment(CmdBase):
    """ Insert node """

    def execute(self):
        """ insert comment node """
        assert self.umlwin
        self.umlwin.CmdInsertNewComment()
            
    def undo(self):  # override
        """ undo insert new comment """
        # not implemented

class CmdInsertNewNode(CmdBase):
    """ Insert new node """

    def __init__(self, umlwin, wxapp):
        """ pass in all the relevant context """
        super(CmdInsertNewNode, self).__init__(umlwin)
        self.wxapp = wxapp

    def execute(self):
        """ insert the new node and refresh the ascii tab too """
        assert self.umlwin
        assert self.wxapp
        self.umlwin.CmdInsertNewNode()
        self.wxapp.RefreshAsciiUmlTab()
            
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
        

