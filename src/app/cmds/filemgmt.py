from base_cmd import CmdBase
from generate_code.gen_java import PySourceAsJava
import wx
import os

class CmdFileNew(CmdBase):
    def execute(self):
        self.context.umlwin.Clear()
        self.context.wxapp.RefreshAsciiUmlTab()

class CmdFileImport(CmdBase):
    def execute(self):
        self.context.wxapp.notebook.SetSelection(0)
        
        thisdir = self.context.config.get('LastDirFileImport', os.getcwd()) # remember dir path
        
        dlg = wx.FileDialog(parent=self.context.frame, message="choose", defaultDir=thisdir,
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            
            self.context.config['LastDirFileImport'] = dlg.GetDirectory()  # remember dir path
            self.context.config.write()
            
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            
            self.context.wxapp.app.run.CmdFileImportSource(files=filenames)   # Command calling another command!
                                                                # Hmmm subcommand does a layout too!????
            self.context.umlwin.redraw_everything()
            
            wx.EndBusyCursor()
            print 'Import - Done.'


class CmdFileImportSource(CmdBase):
    def __init__(self, files=None, path=None):
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
        self.context.umlwin.layout_and_position_shapes()
        

class CmdBootStrap(CmdBase):
    def execute(self):
        self.frame = self.context.frame
        self.app = self.context.wxapp.app
        self.umlwin = self.context.umlwin
        
        def bootstrap01():
            self.frame.SetSize((1024,768))
            self.app.run.CmdFileImportSource(files=[os.path.abspath( __file__ )])
        def bootstrap02():
            self.app.run.CmdFileImportSource(files=[os.path.abspath( "../Research/state chart editor/Editor.py" )])
            self.umlwin.redraw_everything()
        def bootstrap03():
            self.umlwin.redraw_everything()  # Allow main frame to resize and thus allow world coords to calibrate before we generate layout coords for loaded graph
            self.app.run.CmdFileLoadWorkspaceFromFilepath(filepath=os.path.abspath("../tests/saved uml workspaces/uml05.txt"))
            # Don't need to redraw everything after, because persisted
            # workspace is already laid out ok?  Or because we did it first?
        def bootstrap04():
            self.app.run.CmdFileImportSource(files=[os.path.abspath( "pyNsourceGui.py" )])
            self.umlwin.redraw_everything()
        def bootstrap05():
            self.app.run.CmdFileImportSource(files=[os.path.abspath("printframework.py"), os.path.abspath("png.py")])
            self.umlwin.redraw_everything()
        def bootstrap06():
            self.app.run.CmdFileImportSource(files=[os.path.abspath("gui/uml_shapes.py")])
            self.umlwin.redraw_everything()
            
        bootstrap03()
        #self.umlwin.set_uml_canvas_size((9000,9000))
        



class CmdRefreshUmlWindow(CmdBase):
    def execute(self):
        self.context.umlwin.redraw_everything()
        #self.context.umlwin.stateofthenation()
        self.context.wxapp.RefreshAsciiUmlTab()


class CmdFileSaveWorkspace(CmdBase):
    def execute(self):
        dlg = wx.FileDialog(parent=self.context.frame, message="choose", defaultDir='..\\tests\\saved uml workspaces',
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
    def __init__(self, filepath):
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
        thisdir = self.context.config.get('LastDirFileOpen', '..\\tests\\saved uml workspaces') # remember dir path
        
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
