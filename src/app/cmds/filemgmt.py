from .base_cmd import CmdBase
from generate_code.gen_java import PySourceAsJava
import wx
import os
from parsing.api import old_parser, new_parser
from app.settings import RefreshPlantUmlEvent
from gui.coord_utils import setpos, getpos
from gui.settings import PRO_EDITION
from gui.uml_lines import LineShape, LineShapeUml
import logging
from common.logger import config_log
if PRO_EDITION:
    from gui.uml_canvas import DividedShapeOglTwo as DividedShape
else:
    from gui.uml_canvas import DividedShape

try:
    OPEN = wx.OPEN  # classic
    MULTIPLE = wx.MULTIPLE
except AttributeError:
    OPEN = wx.FD_OPEN  # pheonix
    MULTIPLE = wx.FD_MULTIPLE

log = logging.getLogger(__name__)
config_log(log)

class CmdFileNew(CmdBase):
    def execute(self):
        self.context.umlcanvas.Clear()
        self.context.wxapp.RefreshAsciiUmlTab()
        self.context.wxapp.set_app_title("(Untitled)")
        self.context.umlcanvas.mega_refresh()

        # was: self.context.wxapp.refresh_plantuml_view()
        wx.PostEvent(self.context.frame, RefreshPlantUmlEvent())


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

            # self.context.wxapp.refresh_plantuml_view()
            wx.PostEvent(self.context.frame, RefreshPlantUmlEvent())


class CmdFileImportFromFilePath(CmdFileImportBase):  # was class CmdFileImportSource(CmdBase):
    def __init__(self, files=None):
        self.files = files


class CmdFileImportViaDialog(CmdFileImportBase):  # was class CmdFileImport(CmdBase):
    def __init__(self, mode=2):
        self.mode = mode

    def execute(self):
        self.context.wxapp.switch_to_ogl_uml_view()

        thisdir = self.context.config.get("LastDirFileImport", os.path.expanduser("~/"))

        dlg = wx.FileDialog(
            parent=self.context.frame,
            message="Import Python files (*.py)   Hold Ctrl/Cmd to select multiple.",
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
            log.info("Importing... %s" % self.files)
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)

            super(CmdFileImportViaDialog, self).execute()

            wx.EndBusyCursor()
            # print 'Import - Done.'

        dlg.Destroy()


class CmdFileImportViaArgs(CmdFileImportBase):
    def __init__(self, files=None):
        self.files = files


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
                filepath=os.path.abspath("../src/samples/a simple example.pyns")
            )

        def bootstrap04():
            self.app.run.CmdFileImportFromFilePath(files=[os.path.abspath("pynsource-gui.py")])

        def bootstrap05():
            self.app.run.CmdFileImportFromFilePath(
                files=[
                    os.path.abspath("common/printframework.py"),
                    os.path.abspath("common/png.py"),
                ]
            )

        def bootstrap06():
            self.app.run.CmdFileImportFromFilePath(files=[os.path.abspath("gui/uml_shapes.py")])

        def bootstrap07():
            # Load an initial sample - handy for development
            self.app.run.CmdFileLoadWorkspaceSample1()

        def bootstrap08():
            # simple shape
            self.app.run.CmdInsertSimple()

        def bootstrap08():
            # two simple shapes joined by a line
            self.app.run.CmdInsertSingleLine()

        # bootstrap03()
        # bootstrap05()
        bootstrap07()  # <-- good one
        # bootstrap08()

        # self.umlcanvas.set_uml_canvas_size((9000,9000))
        # self.context.frame.ShowFullScreen(True)



# ------- Refresh


class CmdRefreshUmlWindow(CmdBase):
    def execute(self):
        # self.context.umlcanvas.extra_refresh()
        # self.context.umlcanvas.Refresh()
        # self.context.wxapp.RefreshAsciiUmlTab()

        self.context.umlcanvas.mega_refresh()

# ------- Saving to persistence


class CmdFileSaveWorkspace(CmdBase):
    def execute(self):
        thisdir = self.context.config.get("LastDirFileOpen", os.path.expanduser("~/"))
        dlg = wx.FileDialog(
            parent=self.context.frame,
            message="Save Pynsource UML diagram (*.pyns)",
            defaultDir=thisdir,
            defaultFile="",
            wildcard="*.pyns",
            style=wx.FD_SAVE,
            pos=wx.DefaultPosition,
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.context.config["LastDirFileOpen"] = dlg.GetDirectory()  # remember dir path
            self.context.config.write()

            filename = dlg.GetPath()

            # Split the extension from the path and normalise it to lowercase.
            ext = os.path.splitext(filename)[-1].lower()
            if ext != ".pyns":
                print("correcting filename cos it has no extension", filename)
                filename += ".pyns"
                print(filename)
                
            self.context.wxapp.filehistory.AddFileToHistory(filename)  # remember file

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

        umlcanvas.extra_refresh()

        # refresh view
        umlcanvas.GetDiagram().ShowAll(1)  # need this, yes
        umlcanvas.mega_refresh()

        self.context.wxapp.RefreshAsciiUmlTab()  # could do later, on demand, but if viewing ascii tab then want now
        self.context.wxapp.set_app_title(self.filepath)

        self.filepath = None

        # send to frame not self to avoid EVT_WINDOW_DESTROY shutdown error
        wx.PostEvent(self.context.frame, RefreshPlantUmlEvent())

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
            self.load_model_from_text_and_build_shapes(txt)
        dialog.Destroy()


class CmdFileLoadWorkspaceViaDialog(CmdFileLoadWorkspaceBase):
    def execute(self):
        thisdir = self.context.config.get("LastDirFileOpen", os.path.expanduser("~/"))

        dlg = wx.FileDialog(
            parent=self.context.frame,
            message="Open Pynsource diagram file (*.pyns)",
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
            self.context.wxapp.filehistory.AddFileToHistory(self.filepath)  # remember file

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
    
    Run bin/_buildsamples.py to update it.
    """

    def execute(self):
        from base64 import b64decode
        from samples.files_as_resource import sample_files_dict

        # print "samples_dir_files", sample_files_dict.keys()

        dlg = wx.SingleChoiceDialog(
            self.context.frame,
            "Diagrams:",
            "Open a Sample UML Diagram",
            list(sample_files_dict.keys()),
            wx.CHOICEDLG_STYLE,
        )

        if dlg.ShowModal() == wx.ID_OK:
            # self.log.WriteText('You selected: %s\n' % dlg.GetStringSelection())
            k = dlg.GetStringSelection()
            self.filepath = "(Sample - %s)" % k

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



# For development use

class CmdFileLoadWorkspaceSample1(CmdFileLoadWorkspaceBase):
    """
    Quick load initial example for development purposes.
    """

    def execute(self):
        from base64 import b64decode
        from samples.files_as_resource import sample_files_dict

        # k = "classic example.pyns"
        k = "simple inheritance.pyns"

        self.filepath = "(Sample %s)" % k
        s = b64decode(sample_files_dict[k]).decode("utf-8")
        self.load_model_from_text_and_build_shapes(s)

import random
class CmdInsertSimple(CmdFileLoadWorkspaceBase):
    """ Insert new node """

    def execute(self):
        """ insert the new node and refresh the ascii tab too """
        umlcanvas = self.context.umlcanvas
        wxapp = self.context.wxapp
        displaymodel = self.context.displaymodel

        # self.umlcanvas.CmdInsertNewNode()

        result, id, attrs, methods = True, \
                                     "D" + str(random.randint(1, 99)),\
                                     ["attribute 1", "attribute 2", "attribute 3"], \
                                     ["method A", "method B", "method C", "method D"]

        if result:
            # Ensure unique name
            while displaymodel.graph.FindNodeById(id):
                id += "2"

            node = displaymodel.AddUmlNode(id, attrs, methods)
            node.left = 0
            node.top = 0
            node.width = 76
            node.height = 124
            shape = umlcanvas.CreateUmlShape(node)
            # assert shape.x[0] == 0
            # assert shape.y[0] == 0
            # assert shape._width == 70
            # assert shape._height == 70
            node.shape.Show(True)
            # umlcanvas.remove_overlaps()
            umlcanvas.mega_refresh()
            umlcanvas.SelectNodeNow(node.shape)
            # wxapp.RefreshAsciiUmlTab()  # Don't do this because somehow the onKeyChar and onKeyPress handlers are unbound from the UmlCanvas shape canvas


class CmdInsertSingleLine(CmdFileLoadWorkspaceBase):
    """ two nodes joined by line - pure shape level test"""

    def execute(self):
        """ insert the new node and refresh the ascii tab too """
        umlcanvas = self.context.umlcanvas
        wxapp = self.context.wxapp
        displaymodel = self.context.displaymodel

        # assert PRO_EDITION

        width = 50
        height = 50

        # fromShape = ogl.Block()
        fromShape = DividedShape(width, height, umlcanvas, log=None, frame=self.context.frame)
        umlcanvas.InsertShape(fromShape)  # , 999)  wx.ogl doesn't take depth index
        fromShape.label = "A"
        setpos(fromShape, 100, 0)
        # fromShape.SetSize(50, 50)
        fromShape.SetCanvas(umlcanvas)
        fromShape.Show(True)  # needed for wx.ogl

        # toShape = ogl.Block()
        toShape = DividedShape(width, height, umlcanvas, log=None, frame=self.context.frame)
        umlcanvas.InsertShape(toShape)  # , 999)  wx.ogl doesn't take depth index
        toShape.label = "A"
        setpos(toShape, 200, 0)
        # toShape.SetSize(50, 50)
        toShape.SetCanvas(umlcanvas)
        toShape.Show(True)  # needed for wx.ogl

        umlcanvas.Refresh()

        # If don't want the line - development purposes
        # return

        arrowtype = None
        line = LineShape()
        line.SetCanvas(umlcanvas)
        line.SetPen(wx.BLACK_PEN)
        line.SetBrush(wx.BLACK_BRUSH)
        if arrowtype:
            line.AddArrow(arrowtype)
        line.MakeLineControlPoints(2)

        fromShape.AddLine(line, toShape)
        umlcanvas.GetDiagram().AddShape(line)
        line.Show(True)
    
        umlcanvas.Refresh()
        if not PRO_EDITION:
            umlcanvas.extra_refresh()  # wx.ogl needs

        umlcanvas.select(line)
        umlcanvas.zoom_in()
        umlcanvas.zoom_in()
        umlcanvas.zoom_in()
