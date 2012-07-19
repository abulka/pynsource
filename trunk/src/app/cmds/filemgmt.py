from base_cmd import CmdBase
from generate_code.gen_java import PySourceAsJava
import wx

class CmdFileNew(CmdBase):

    def execute(self):
        self.context.umlwin.Clear()
        self.context.wxapp.RefreshAsciiUmlTab()

        
class CmdFileImportSource(CmdBase):

    def __init__(self, context, files=None, path=None):
        """ pass in all the relevant context as well as the files to import """
        super(CmdFileImportSource, self).__init__(context)
        self.files = files
        self.path = path
        
    def execute(self):
        # these are tuples between class names.
        self.context.model.ClearAssociations()       # WHY DO WE WANT TO DESTROY THIS VALUABLE INFO?

        if self.files:
            for f in self.files:
                p = PySourceAsJava()
                p.optionModuleAsClass = 0
                p.verbose = 0
                p.Parse(f)
                self.context.model.ConvertParseModelToUmlModel(p)

        self.context.umlwin.stage1()

        # Layout
        self.context.umlwin.LayoutAndPositionShapes()
        
    def undo(self):  # override
        """ Docstring """
        # not implemented

class CmdFileSaveWorkspace(CmdBase):

    def execute(self):
        dlg = wx.FileDialog(parent=self.context.frame, message="choose", defaultDir='.\\saved uml workspaces',
            defaultFile="", wildcard="*.txt", style=wx.FD_SAVE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            
            fp = open(filename, "w")
            fp.write(self.context.model.graph.GraphToString())
            fp.close()
        dlg.Destroy()

class CmdFileSaveWorkspaceToConsole(CmdBase):

    def execute(self):
        print self.context.model.graph.GraphToString()

class CmdFileLoadWorkspaceBase(CmdBase):   # BASE
    def LoadGraph(self, filedata=""):
        umlcanvas = self.context.umlwin
        
        umlcanvas.Clear()
        
        self.context.model.graph.LoadGraphFromStrings(filedata)
                
        # build view from model
        umlcanvas.stage1(translatecoords=False)

        # set layout coords to be in sync with world, so that if expand scale things will work
        self.context.coordmapper.Recalibrate()
        umlcanvas.AllToLayoutCoords()
        
        # refresh view
        umlcanvas.GetDiagram().ShowAll(1) # need this, yes
        umlcanvas.stateofthenation()
        
        self.context.wxapp.RefreshAsciiUmlTab()

    def execute(self):
        raise "base/virtual only"
        
class CmdFileLoadWorkspaceFromFilepath(CmdFileLoadWorkspaceBase):

    def __init__(self, context, filepath):
        """ pass in all the relevant context as well as the files to import """
        super(CmdFileLoadWorkspaceFromFilepath, self).__init__(context)
        self.filepath = filepath
        
    def execute(self):
            fp = open(self.filepath, "r")
            s = fp.read()
            fp.close()
            self.LoadGraph(s)
            
class CmdFileLoadWorkspaceFromQuickPrompt(CmdFileLoadWorkspaceBase):

    def execute(self):
        eg = "{'type':'node', 'id':'A', 'x':142, 'y':129, 'width':250, 'height':250}"
        dialog = wx.TextEntryDialog (parent=self.context.frame, message='Enter node/edge persistence strings:', caption='Load Graph From Text', defaultValue=eg, style=wx.OK|wx.CANCEL|wx.TE_MULTILINE )
        if dialog.ShowModal() == wx.ID_OK:
            txt = dialog.GetValue()
            print txt
            self.LoadGraph(txt)
        dialog.Destroy()
        
class CmdFileLoadWorkspaceViaDialog(CmdFileLoadWorkspaceBase):
    def execute(self):
        thisdir = self.context.config.get('LastDirFileOpen', '.\\saved uml workspaces') # remember dir path
        
        dlg = wx.FileDialog(parent=self.context.frame, message="choose", defaultDir=thisdir,
            defaultFile="", wildcard="*.txt", style=wx.OPEN, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            self.context.config['LastDirFileOpen'] = dlg.GetDirectory()  # remember dir path
            self.context.config.write()

            fp = open(filename, "r")
            s = fp.read()
            fp.close()

            self.LoadGraph(s)
        dlg.Destroy()


