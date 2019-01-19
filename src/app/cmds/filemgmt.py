from .base_cmd import CmdBase
from generate_code.gen_java import PySourceAsJava
import wx
import os
from parsing.api import old_parser, new_parser

try:
    OPEN = wx.OPEN  # classic
    MULTIPLE = wx.MULTIPLE
except AttributeError:
    OPEN = wx.FD_OPEN  # pheonix
    MULTIPLE = wx.FD_MULTIPLE


class CmdFileNew(CmdBase):
    def execute(self):
        self.context.umlcanvas.Clear()
        self.context.wxapp.RefreshAsciiUmlTab()
        self.context.wxapp.set_app_title("(Untitled)")
        self.context.umlcanvas.mega_refresh()


# ----- Importing python source code


class CmdFileImportBase(CmdBase):  # BASE
    def execute(self):
        workspace_was_empty: bool = len(self.context.displaymodel.graph.nodes) == 0
        if self.files:
            for f in self.files:
                # pmodel, debuginfo = old_parser(f)
                # pmodel, debuginfo = new_parser(f)
                mode = getattr(self, "mode", 2)
                # print(f"Importing Python in syntax mode {mode}")
                pmodel, debuginfo = new_parser(f, options={"mode": mode})
                if pmodel.errors:
                    # print(pmodel.errors)
                    self.context.wxapp.MessageBox(pmodel.errors)

                # from parsing.dump_pmodel import dump_old_structure
                # print(dump_old_structure(pmodel))

                self.context.displaymodel.build_graphmodel(pmodel)
                # self.context.displaymodel.Dump(msg="import, after build_graphmodel")

            # translatecoords being True is the culprit which keeps resetting the node positions
            self.context.umlcanvas.displaymodel.build_view(translatecoords=False)
            # self.context.displaymodel.Dump(msg="import, after build_view")

            self.context.umlcanvas.GetDiagram().ShowAll(1)  # need this, yes

            if workspace_was_empty:  # don't layout if importing into canvas with existing shapes
                self.context.umlcanvas.layout_and_position_shapes()
            else:
                # At least remove overlaps
                self.context.overlap_remover.RemoveOverlaps(watch_removals=True)

            self.context.umlcanvas.mega_refresh()


class CmdFileImportFromFilePath(CmdFileImportBase):  # was class CmdFileImportSource(CmdBase):
    def __init__(self, files=None):
        self.files = files


class CmdFileImportViaDialog(CmdFileImportBase):  # was class CmdFileImport(CmdBase):
    def __init__(self, mode=2):
        self.mode = mode

    def execute(self):
        self.context.wxapp.switch_to_ogl_uml_view()

        thisdir = self.context.config.get("LastDirFileImport", os.getcwd())  # remember dir path

        dlg = wx.FileDialog(
            parent=self.context.frame,
            message="choose",
            defaultDir=thisdir,
            defaultFile="",
            wildcard="*.py",
            style=OPEN | MULTIPLE,
            pos=wx.DefaultPosition,
        )
        if dlg.ShowModal() == wx.ID_OK:

            self.context.config["LastDirFileImport"] = dlg.GetDirectory()  # remember dir path
            self.context.config.write()

            self.files = dlg.GetPaths()
            print("Importing...", self.files)
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)

            super(CmdFileImportViaDialog, self).execute()

            wx.EndBusyCursor()
            # print 'Import - Done.'

        dlg.Destroy()


class CmdBootStrap(CmdBase):
    def execute(self):
        self.frame = self.context.frame
        self.app = self.context.wxapp.app
        self.umlcanvas = self.context.umlcanvas

        def bootstrap01():
            self.frame.SetSize((1024, 768))
            self.app.run.CmdFileImportFromFilePath(files=[os.path.abspath(__file__)])

        def bootstrap02():
            self.app.run.CmdFileImportFromFilePath(
                files=[os.path.abspath("../Research/state chart editor/Editor.py")]
            )

        def bootstrap03():
            self.app.run.CmdFileLoadWorkspaceFromFilepath(
                filepath=os.path.abspath("../tests/saved uml workspaces/uml05.pyns")
            )

        def bootstrap04():
            self.app.run.CmdFileImportFromFilePath(files=[os.path.abspath("pyNsourceGui.py")])

        def bootstrap05():
            self.app.run.CmdFileImportFromFilePath(
                files=[
                    os.path.abspath("common/printframework.py"),
                    os.path.abspath("common/png.py"),
                ]
            )

        def bootstrap06():
            self.app.run.CmdFileImportFromFilePath(files=[os.path.abspath("gui/uml_shapes.py")])

        # bootstrap03()
        # self.umlcanvas.set_uml_canvas_size((9000,9000))

        # Load an initial sample - handy for development
        # self.app.run.CmdFileLoadWorkspaceSample1()


# ------- Refresh


class CmdRefreshUmlWindow(CmdBase):
    def execute(self):
        self.context.frame.Layout()  # needed when running phoenix
        self.context.umlcanvas.Refresh()
        self.context.wxapp.RefreshAsciiUmlTab()


# ------- Saving to persistence


class CmdFileSaveWorkspace(CmdBase):
    def execute(self):
        dlg = wx.FileDialog(
            parent=self.context.frame,
            message="choose",
            defaultDir="..\\tests\\saved uml workspaces",
            defaultFile="",
            wildcard="*.pyns",
            style=wx.FD_SAVE,
            pos=wx.DefaultPosition,
        )
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()

            fp = open(filename, "w")
            fp.write(self.context.displaymodel.graph.GraphToString())
            fp.close()

            self.context.wxapp.set_app_title(filename)

        dlg.Destroy()


class CmdFileSaveWorkspaceToConsole(CmdBase):
    def execute(self):
        print(self.context.displaymodel.graph.GraphToString())


# ------- Loading from persistence


class CmdFileLoadWorkspaceBase(CmdBase):  # BASE
    def __init__(self):
        self.filepath = None

    def load_model_from_text_and_build_shapes(self, filedata=""):
        umlcanvas = self.context.umlcanvas

        force = False
        canread, msg = self.context.displaymodel.graph.persistence.can_I_read(filedata)
        if not canread:
            # self.context.wxapp.MessageBox(msg)
            retCode = wx.MessageBox(
                msg + "\n\nTry anyway?", "File Open Error", wx.YES_NO | wx.ICON_QUESTION
            )  # MessageBox simpler than MessageDialog
            if retCode == wx.YES:
                force = True
            else:
                return

        umlcanvas.Clear()

        if not self.context.displaymodel.graph.LoadGraphFromStrings(filedata, force):
            self.context.wxapp.MessageBox("Open failed.")
            return

        # build view from display model
        umlcanvas.displaymodel.build_view(translatecoords=False)

        # set layout coords to be in sync with world, so that if expand scale things will work
        self.context.coordmapper.Recalibrate()
        umlcanvas.AllToLayoutCoords()

        self.context.frame.Layout()  # needed when running phoenix

        # refresh view
        umlcanvas.GetDiagram().ShowAll(1)  # need this, yes
        umlcanvas.mega_refresh()

        self.context.wxapp.RefreshAsciiUmlTab()
        self.context.wxapp.set_app_title(self.filepath)

        self.filepath = None

    def execute(self):
        fp = open(self.filepath, "r")
        s = fp.read()
        fp.close()
        self.load_model_from_text_and_build_shapes(s)


class CmdFileLoadWorkspaceFromFilepath(CmdFileLoadWorkspaceBase):
    def __init__(self, filepath):
        self.filepath = filepath


class CmdFileLoadWorkspaceFromQuickPrompt(CmdFileLoadWorkspaceBase):
    def __init__(self):
        self.filepath = "Console"

    def execute(self):
        eg = "{'type':'node', 'id':'A', 'x':142, 'y':129, 'width':250, 'height':250}"
        dialog = wx.TextEntryDialog(
            parent=self.context.frame,
            message="Enter node/edge persistence strings:",
            caption="Load Graph From Text",
            value=eg,
            style=wx.OK | wx.CANCEL | wx.TE_MULTILINE,
        )
        dialog.SetClientSize(wx.Size(400, 200))  # make bigger
        if dialog.ShowModal() == wx.ID_OK:
            txt = dialog.GetValue()
            print(txt)
            self.load_model_from_text_and_build_shapes(txt)
        dialog.Destroy()


class CmdFileLoadWorkspaceViaDialog(CmdFileLoadWorkspaceBase):
    def execute(self):
        thisdir = self.context.config.get(
            "LastDirFileOpen", "..\\tests\\saved uml workspaces"
        )  # remember dir path

        dlg = wx.FileDialog(
            parent=self.context.frame,
            message="choose",
            defaultDir=thisdir,
            defaultFile="",
            wildcard="*.pyns",
            style=OPEN,
            pos=wx.DefaultPosition,
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.filepath = dlg.GetPath()

            self.context.config["LastDirFileOpen"] = dlg.GetDirectory()  # remember dir path
            self.context.config.write()

            super(CmdFileLoadWorkspaceViaDialog, self).execute()

        dlg.Destroy()


class CmdFileLoadWorkspaceSampleViaDialog(CmdFileLoadWorkspaceBase):
    """
    Load from the samples directory
    """

    def execute_from_dir(self):

        thisdir = os.path.dirname(os.path.realpath(__file__))
        thisdir = os.path.join(thisdir, "../../samples")

        dlg = wx.FileDialog(
            parent=self.context.frame,
            message="choose",
            defaultDir=thisdir,
            defaultFile="",
            wildcard="*.pyns",
            style=OPEN,
            pos=wx.DefaultPosition,
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.filepath = dlg.GetPath()
            super(CmdFileLoadWorkspaceSampleViaDialog, self).execute()
        dlg.Destroy()


from dialogs.DialogChooseFromList import MyDialogChooseFromList


class DialogChooser(MyDialogChooseFromList):
    def SetMyData(self, data):
        self.data = data
        self.m_listBox1.InsertItems(data, 0)

    # TODO how to get doubleclick to exit the ShowModal() call?
    # def OnListDoubleClick( self, event ):
    #    print self.GetChosenItem()
    #    self.Close()

    def GetChosenItem(self):
        index = self.m_listBox1.GetSelection()
        return self.data[index]


class CmdFileLoadWorkspaceSampleViaPickList(CmdFileLoadWorkspaceBase):
    """
    Load from the samples base64 dictionary.
    
    Reason for doing this: allows us to keep 'file' resources in the app itself,
    thus no need for loading external file - which is problematic e.g. on the mac
    
    Run buildsamples.py to update it.
    """

    def execute(self):
        from base64 import b64decode
        from samples.files_as_resource import sample_files_dict

        # print "samples_dir_files", sample_files_dict.keys()

        dlg = wx.SingleChoiceDialog(
            self.context.frame,
            "Choice:",
            "Choose a Sample Uml Diagram",
            list(sample_files_dict.keys()),
            wx.CHOICEDLG_STYLE,
        )

        if dlg.ShowModal() == wx.ID_OK:
            # self.log.WriteText('You selected: %s\n' % dlg.GetStringSelection())
            k = dlg.GetStringSelection()
            self.filepath = "(Sample %s)" % k

            s = b64decode(sample_files_dict[k]).decode("utf-8")
            self.load_model_from_text_and_build_shapes(s)
        dlg.Destroy()

        # dialog = DialogChooser(None)
        # dialog.m_staticTextInstruction.Value = "Please Choose:"
        # dialog.SetMyData(sample_files_dict.keys())
        # if dialog.ShowModal() == wx.ID_OK:
        #    #print dialog.GetChosenItem()
        #    k = dialog.GetChosenItem() # sample_files_dict.keys()[0]
        #    self.filepath = "(Sample %s)" % k
        #
        #    s = b64decode(sample_files_dict[k])
        #    self.load_model_from_text_and_build_shapes(s)
        #
        # dialog.Destroy()


class CmdFileLoadWorkspaceSample1(CmdFileLoadWorkspaceBase):
    """
    Quick load initial example for development purposes.
    """

    def execute(self):
        from base64 import b64decode
        from samples.files_as_resource import sample_files_dict

        k = "hexmvc_architecture1.pyns"
        self.filepath = "(Sample %s)" % k
        s = b64decode(sample_files_dict[k]).decode("utf-8")
        self.load_model_from_text_and_build_shapes(s)
