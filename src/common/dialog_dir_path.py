import pathlib
import sys
import os
import wx

# remember current working directory, since opening help window and plantuml text dialog
# changes it (via dialog_dir_path function)
original_working_dir = os.getcwd()  # initial guess but can be wrong if run from a different dir, so adjust later

def set_original_working_dir(path):
    global original_working_dir
    original_working_dir = path

def _display_dir(d: str = '.', frame: wx.Frame = None):
    currentDirectory = pathlib.Path(d)
    currentPattern = "*"
    zz = [str(p) for p in currentDirectory.glob(currentPattern)]
    zz.sort()
    zz.insert(0, f"Directory {d}\n\n")
    msg = "\n".join(zz)
    if frame:
        dlg = wx.MessageDialog(frame, msg, "Message", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

def _clean_path(path):
    # realpath takes into account symlinks, normpath doesn't, abspath fixes .. and . refs
    return os.path.realpath(os.path.abspath(path))

def dialog_path_pyinstaller_pop():
    """Reset to original working dir"""
    dir = original_working_dir
    fs = wx.FileSystem()

    if _clean_path(fs.GetPath()) != _clean_path(dir):
        fs.ChangePathTo(dir)
        # print("changed BACK to", dir)

    if _clean_path(os.getcwd()) != _clean_path(dir):
        os.chdir(dir)
        # print("python changed BACK to", dir)

def dialog_path_pyinstaller_push(frame: wx.Frame = None):
    """
    Changes the both the

        - wx notion of current directory (need for html help viewer to find images)
        - python notion of current directory (need for plantuml_text dialog to find image)

    to be the dialogs/ dir.

    When deployed via pyinstaller, this will be the pyinstaller .app temp dir,
    not the dist/ dir
    """
    dialogs_dir = "dialogs/"  # for Pyinstaller
    try:
        wd = sys._MEIPASS
    except AttributeError:
        wd = original_working_dir # os.getcwd()
    # _display_dir(".", frame)
    # _display_dir(wd, frame)
    dir = os.path.join(wd, dialogs_dir)
    # dir = os.path.join(wd)
    # dir = os.path.join(wd, dialogs_dir, "help-images")
    # _display_dir(dir, frame)

    # Change the current directory, so that the html window sees image resources etc
    fs = wx.FileSystem()
    if _clean_path(fs.GetPath()) != _clean_path(dir):
        fs.ChangePathTo(dir)
        # print("changed to", dir)

    # Also change the python current dir, so that dialog boxes which create images from relative
    # paths can build the path properly.  wxformbuilder runs projects from the dialog/ dir
    # so the path root is dialog/
    if _clean_path(os.getcwd()) != _clean_path(dir):
        os.chdir(dir)
        # print("python changed to", dir)

    # self.MessageBox(fs.GetPath())
    return dir

# Scraps

# For old py2app deployments
#
# if os.path.exists("../Resources"):
#     dir = "../Resources"
# else:
#     dir = "dialogs/"


