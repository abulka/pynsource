# Image viewer

import wx
import sys
import io
import urllib.request, urllib.parse, urllib.error
from urllib.request import Request, urlopen
import asyncio
from io import StringIO
# from pydbg import dbg
from gui.coord_utils import ZoomInfo
from typing import List, Set, Dict, Tuple, Optional
from generate_code.gen_plantuml import plant_uml_create_png_and_return_image_url_async
from generate_code.gen_plantuml import plant_uml_fetch_svg_bytes_async
from dialogs.DialogPlantUmlText import DialogPlantUmlText
from common.dialog_dir_path import dialog_path_pyinstaller_push, dialog_path_pyinstaller_pop
from common.messages import *
import datetime
from app.settings import CancelRefreshPlantUmlEvent, EVT_CANCEL_REFRESH_PLANTUML_EVENT
from common.url_to_data import url_to_data
import logging
from common.logger import config_log


log = logging.getLogger(__name__)
config_log(log)

ALLOW_DRAWING = True
DEFAULT_IMAGE_SIZE = (21, 21)  # used to be 2000, 2000 for some reason
BMP_EXTRA_MARGIN = 20  # margin for plantuml images to allow scrolling them fully into view


class PlantUmlMarkupDialog(DialogPlantUmlText):
    """The generated markup, plus copy and browser buttons.

    Copying markup out of Pynsource into a browser can pick up macOS "smart
    dashes", which rewrite `--|>` as an em dash and make PlantUML answer with a
    syntax error. The copy button verifies what actually landed on the
    clipboard, so it is obvious whether the clipboard or the receiving app is at
    fault, and "Open in browser" avoids the clipboard entirely.
    """

    def __init__(self, parent, pure_text, server_url=""):
        DialogPlantUmlText.__init__(self, parent)
        self.pure_text = pure_text
        self.server_url = server_url
        self._add_copy_buttons()

    def _add_copy_buttons(self):
        panel = self.m_panel2
        panel_sizer = panel.GetSizer()

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_copy_pure = wx.Button(panel, label="Copy pure markup")
        self.btn_open_browser = wx.Button(panel, label="Open in browser")
        button_row.Add(self.btn_copy_pure, 0, wx.RIGHT, 6)
        button_row.Add(self.btn_open_browser, 0, wx.RIGHT, 8)
        panel_sizer.Insert(len(panel_sizer.GetChildren()) - 1, button_row, 0, wx.EXPAND | wx.ALL, 5)

        self.lbl_copy = wx.StaticText(panel, label="")
        self.lbl_copy.Wrap(400)
        panel_sizer.Insert(len(panel_sizer.GetChildren()) - 1, self.lbl_copy, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        panel.Layout()
        self.btn_copy_pure.Bind(wx.EVT_BUTTON, self.OnCopyPure)
        self.btn_open_browser.Bind(wx.EVT_BUTTON, self.OnOpenInBrowser)

    def OnCopyPure(self, event):
        message = self.copy_to_clipboard(self.pure_text, "pure markup")
        # changing the button label too - the message line can be easy to miss
        self.btn_copy_pure.SetLabel("Copied!")
        wx.CallLater(1500, self._restore_copy_button)
        return message

    def _restore_copy_button(self):
        try:
            self.btn_copy_pure.SetLabel("Copy pure markup")
        except RuntimeError:  # dialog already destroyed
            pass

    def OnOpenInBrowser(self, event):
        from common.plantuml import plant_uml_view_url

        url = plant_uml_view_url(self.pure_text, self.server_url)
        wx.LaunchDefaultBrowser(url)
        self.show_message(f"Opened in your browser: {url}")

    @staticmethod
    def read_clipboard():
        """What the clipboard actually holds, as another app will see it."""
        text = ""
        if wx.TheClipboard.Open():
            try:
                data = wx.TextDataObject()
                if wx.TheClipboard.GetData(data):
                    text = data.GetText()
            finally:
                wx.TheClipboard.Close()
        return text

    def copy_to_clipboard(self, text, what):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()

        message = f"Copied {what} ({len(text)} chars)"
        on_clipboard = self.read_clipboard()
        if on_clipboard != text:
            position, char_sent, char_clip = first_difference(text, on_clipboard)
            message += (f" - CLIPBOARD CHANGED IT at char {position}: sent "
                        f"{describe_char(char_sent)} got {describe_char(char_clip)}")
        else:
            message += " - clipboard verified"

        box_text = self.txt_plantuml.GetValue()
        if box_text != self.pure_text:
            position, char_pure, char_box = first_difference(self.pure_text, box_text)
            message += (f" - text box differs from markup at char {position}: "
                        f"markup {describe_char(char_pure)} vs box {describe_char(char_box)}")
        self.show_message(message)
        return message

    def show_message(self, message):
        self.lbl_copy.SetLabel(message)
        self.lbl_copy.Wrap(400)
        self.m_panel2.Layout()
        self.Layout()
        self.Refresh()
        self.Update()

    def OnClassNameEnter(self, event):
        self.EndModal(wx.ID_OK)


def first_difference(a, b):
    """(index, char_in_a, char_in_b) of the first difference, or (None, '', '')."""
    for i, (char_a, char_b) in enumerate(zip(a, b)):
        if char_a != char_b:
            return i, char_a, char_b
    if len(a) != len(b):
        i = min(len(a), len(b))
        return i, a[i:i + 1], b[i:i + 1]
    return None, "", ""


def describe_char(char):
    if not char:
        return "<end>"
    return f"{char!r} (U+{ord(char):04X})"


class ImageViewer(wx.ScrolledWindow):
    def __init__(self, parent, id=-1, size=wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)

        self.lines = []
        self.maxWidth, self.maxHeight = DEFAULT_IMAGE_SIZE
        self.x = self.y = 0
        self.curLine = []
        self.drawing = False

        self.SetBackgroundColour("WHITE")  # for areas of the frame not covered by the bmp
        # TODO these areas don't get refreshed properly when scrolling when pen marks are around, we only refresh bmp area and when bmp area < client window we get artifacts.

        bmp, dc = self._CreateNewWhiteBmp(self.maxWidth, self.maxHeight)

        self.bmp = bmp
        self.bmp_transparent_ori = None

        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(1, 1)  # set the ScrollRate to 1 in order for panning to work nicely
        self.zoomscale = 1.0
        self.clear_whole_window = False

        if ALLOW_DRAWING:
            self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftButtonEvent)
            self.Bind(wx.EVT_LEFT_UP, self.OnLeftButtonEvent)
            self.Bind(wx.EVT_MOTION, self.OnLeftButtonEvent)
            self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonEvent)
            # self.Bind(wx.EVT_IDLE, self.OnIdle)  # ANDY HACK

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelScroll)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
        self.Bind(wx.EVT_CHAR, self.onKeyChar)  # 2019 added
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightButtonMenu)
        self.was_dragging = False  # True if dragging map
        self.move_dx = 0  # drag delta values
        self.move_dy = 0
        self.last_drag_x = None  # previous drag position
        self.last_drag_y = None
        self.SetScrollbars(1, 1, int(self.GetVirtualSize()[0]), int(self.GetVirtualSize()[1]))
        self.mywheelscroll = 0
        self.popupmenu = None

        # self.repaint_needed = False
        self.working = False  # key press re-entrancy protection

        self.plantuml_text = ""

        # Image fetching states and flags
        self.error_msg = ""  # message to display on big screen, when there is an error
        self.fetching_msg = ""  # message to display on big screen, use as flag for when working
        self.fetching_started_time = None

    @property
    def working_fetching(self):  # stop multiple plant uml refreshes
        return self.fetching_msg != ""  # if there is a message, that's a flag that we are http-ing

    @property
    def time_taken_fetching(self) -> float:
        raw_diff = datetime.datetime.utcnow() - self.fetching_started_time
        return raw_diff.total_seconds()

    def clear(self):
        self.error_msg = PLANTUML_VIEW_INITAL_HELP
        self.fetching_msg = ""
        self.bmp, dc = self._CreateNewWhiteBmp(self.maxWidth, self.maxHeight)
        self.bmp_transparent_ori = None
        self.plantuml_text = ""
        self.lines = []
        self.Refresh()

    def clear_cos_connection_error(self, msg=""):
        self.clear()
        self.error_msg = PLANTUML_VIEW_INTERNET_FAIL % msg
        # print(plant_uml_create_png_and_return_image_url.cache_info())
        plant_uml_create_png_and_return_image_url_async.cache_clear()
        plant_uml_fetch_svg_bytes_async.cache_clear()
        url_to_data.cache_clear()
        self.Refresh()

    def user_aborted(self):
        self.error_msg = PLANTUML_VIEW_USER_ABORT
        plant_uml_create_png_and_return_image_url_async.cache_clear()
        plant_uml_fetch_svg_bytes_async.cache_clear()
        url_to_data.cache_clear()
        self.Refresh()

    def render_in_progress(self, rendering: bool, frame):
        if rendering:
            self.error_msg = ""
            self.fetching_msg = PLANTUML_VIEW_FETCHING_MSG
            self.fetching_started_time = datetime.datetime.utcnow()
        else:
            self.fetching_msg = ""

        # Update PlantUML view, guarding against the situation where when shutting down app
        # and killing pending tasks, the window may not exist anymore
        try:
            self.Refresh()
            wx.SafeYield()  # Needed to "breathe" and refresh the UI
            # print("warning use of safe yield in image viewer")
        except RuntimeError:
            pass  # avoid error when shutting down tasks

    async def ViewImage(self, thefile="", url=""):
        """Loads url or file and sets .bmp and .bmp_transparent_ori, the img is discarded"""
        self.error_msg = None
        bmp = None
        if thefile:
            img = wx.Image(thefile, wx.BITMAP_TYPE_ANY)
            bmp = wx.Bitmap(img)  # ANDY added 2019
        elif url:
            # print(url_to_data.cache_info())
            try:
                data, status = await url_to_data(url)
                log.info(f"(2nd, image grabbing) Response from plant_uml_server status_code {status}")

            except asyncio.TimeoutError as e:  # there is no string repr of this exception
                self.clear_cos_connection_error(msg="(timeout)")
                url_to_data.cache_clear()  # so if retry you won't get the same error
                log.error("TimeoutError getting plantuml IMAGE")
                return

            if status != 200:
                self.clear_cos_connection_error(msg=f"(bad response {status})")
                log.error(f"Error getting plantuml IMAGE, (bad response {status})")
                return

            stream = io.BytesIO(data)
            img = wx.Image(stream)
            bmp = wx.Bitmap(img)

        # try:
        #     bmp = img.ConvertToBitmap()
        # except Exception as e:
        #     print(e)
        #     return

        if bmp is not None and bmp.IsOk():
            self._set_bitmap(bmp)

    def _set_bitmap(self, bmp):
        """Adopt a freshly rasterized bitmap as the viewed image."""
        self.maxWidth, self.maxHeight = bmp.GetWidth(), bmp.GetHeight()
        self.maxHeight += BMP_EXTRA_MARGIN  # stop bitmaps getting slightly clipped

        # dbg(bmp)
        # ANDY bmp.HasAlpha() does not work, since wx.Image has this method but wx.Bitmap
        # does not.  But Bitmaps have some alpha channel concepts in them too...?

        # Render bmp to a second white bmp to remove transparency effects
        # if False and bmp.HasAlpha():
        img = bmp.ConvertToImage()
        if img.HasAlpha():
            self.bmp_transparent_ori = bmp
            bmp2 = wx.Bitmap(bmp.GetWidth(), bmp.GetHeight())
            dc = wx.MemoryDC()
            dc.SelectObject(bmp2)
            # PlantUML's transparent PNG assumes a white page.  Clear to an
            # explicit white background: a freshly created wx.Bitmap is
            # uninitialised on GTK, which made thin black shape borders
            # disappear or turn random colours on Linux.
            dc.SetBackground(wx.Brush(wx.WHITE))
            dc.Clear()
            dc.DrawBitmap(bmp, 0, 0, False)
            dc.SelectObject(wx.NullBitmap)
            self.bmp = bmp2
        else:
            self.bmp_transparent_ori = None
            self.bmp = bmp

    # def OnIdle(self, event):
    #     """Idle Handler."""
    #     if self.working:
    #         dbg("re-entrancy avoided")
    #         return
    #     self.working = True
    #     if self.repaint_needed:
    #         dbg("repaint needed mate")
    #         self.Refresh()
    #         self.Update()  # or wx.SafeYield()  # Without this the nodes don't paint during a "L" layout (edges do!?)
    #         wx.SafeYield()  # Needed on Mac to see result if in a compute loop.
    #         self.repaint_needed = False
    #     self.working = 0

    def _CreateNewWhiteBmp(self, width, height, wantdc=False):
        bmp = wx.Bitmap(width, height)
        # Could simply return here, but bitmap would be black (or a bit random, under linux)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        # dbg(wantdc)
        if wantdc:  # just in case want to continue drawing
            return bmp, dc
        else:
            dc.SelectObject(wx.NullBitmap)
            return bmp, dc

    def OnHandleSaveImage(self, event):
        pass  # pro feature

    def OnHandleSaveImagePreserveTransparencies(self, event):
        pass  # pro feature

    def OnHandleSaveImageInclDoodles(self, event):
        pass  # pro feature

    def OnHandleSaveSvg(self, event):
        pass  # overridden in PynsourceImageViewer - saves server SVG bytes

    def OnHandleQuickLoadImage(self, event):
        self.ViewImage(FILE)

    def OnHandleQuickLoadFromYumlUrl(self, event):
        baseUrl = "http://yuml.me/diagram/dir:lr;scruffy/class/"
        yuml_txt = (
            "[Customer]+1->*[Order],[Order]++1-items >*[LineItem],[Order]-0..1>[PaymentMethod]"
        )
        url = baseUrl + urllib.parse.quote(yuml_txt)
        self.ViewImage(url=url)

    def OnRightButtonMenu(self, event):  # Menu
        if event.ShiftDown():
            event.Skip()
            return

        """
        Accelerator tables need unique ids, whereas direct menuitem binding with Bind(...source=menuitem)
        doesn't care about ids and can thus use wx.ID_ANY (which is always -1)
        Use wx.NewIdRef() if you want a real fresh id.
        """

        x, y = event.GetPosition()
        frame = self.GetTopLevelParent()

        if self.popupmenu:
            self.popupmenu.Destroy()  # wx.Menu objects need to be explicitly destroyed (e.g. menu.Destroy()) in this situation. Otherwise, they will rack up the USER Objects count on Windows; eventually crashing a program when USER Objects is maxed out. -- U. Artie Eoff  http://wiki.wxpython.org/index.cgi/PopupMenuOnRightClick
        self.popupmenu = wx.Menu()  # Create a menu

        if event.AltDown():
            # Debug menu items
            item = self.popupmenu.Append(wx.ID_ANY, "Load Image...")
            frame.Bind(wx.EVT_MENU, self.OnHandleFileLoad, item)

            item = self.popupmenu.Append(wx.ID_ANY, "Quick Load Image from Disk")
            frame.Bind(wx.EVT_MENU, self.OnHandleQuickLoadImage, item)

            item = self.popupmenu.Append(wx.ID_ANY, "Quick Load Image from Yuml Url")
            frame.Bind(wx.EVT_MENU, self.OnHandleQuickLoadFromYumlUrl, item)

            self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.ID_ANY, "Save Image as PNG...")
        frame.Bind(wx.EVT_MENU, self.OnHandleSaveImage, item)

        if getattr(self, "plantuml_text", None):
            # SVG export fetches vector bytes on demand, so it is offered in
            # every display mode - not just when viewing the SVG render.
            item = self.popupmenu.Append(wx.ID_ANY, "Save Image as SVG...")
            frame.Bind(wx.EVT_MENU, self.OnHandleSaveSvg, item)

        if self.bmp_transparent_ori:
            item = self.popupmenu.Append(wx.ID_ANY, "Save Image as PNG... (preserve transparent areas)")
            frame.Bind(wx.EVT_MENU, self.OnHandleSaveImagePreserveTransparencies, item)

        item = self.popupmenu.Append(wx.ID_ANY, "Save Image as PNG... (incl. pen doodles)")
        frame.Bind(wx.EVT_MENU, self.OnHandleSaveImageInclDoodles, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.ID_ANY, "Clear pen doodles (SHIFT drag to create)\tE")
        frame.Bind(wx.EVT_MENU, self.OnClearPenLines, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.ID_ANY, "View PlantUML markup...")
        frame.Bind(wx.EVT_MENU, self.OnViewPlantUmlMarkup, item)

        self.popupmenu.AppendSeparator()

        item = self.popupmenu.Append(wx.ID_ANY, "Cancel")

        frame.PopupMenu(self.popupmenu, wx.Point(x, y))

    def OnViewPlantUmlMarkup(self, event, alt_down=False):
        mouse_state: wx.MouseState = wx.GetMouseState()
        if mouse_state.AltDown():
            print(self.plantuml_text)

        # change cwd so that dialog can find the 'pro' image jpg which is relative to dialogs/
        # when deployed via pyinstaller, this path is a bit tricky to find, so use this func.
        dir = dialog_path_pyinstaller_push(frame = self)
        try:
            server_url = ""
            config = getattr(getattr(self, "context", None), "config", None)
            if config is not None:
                server_url = config.get("PlantUmlServerUrl", "") or ""
            dialog = PlantUmlMarkupDialog(None, self.plantuml_text, server_url=server_url)
            dialog.txt_plantuml.Value = self.plantuml_text
            dialog.txt_plantuml.SetFocus()
            dialog.ShowModal()
            # dialog.Show()
            dialog.Destroy()
        finally:
            dialog_path_pyinstaller_pop()

    def OnHandleFileLoad(self, event):
        frame = self.GetTopLevelParent()
        wildcard = (
            "Images (*.png; *.jpeg; *.jpg; *.bmp)|*.png;*.jpeg;*.jpg;*.bmp|" "All files (*.*)|*.*"
        )
        dlg = wx.FileDialog(
            parent=frame,
            message="choose",
            defaultDir=".",
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN,
            pos=wx.DefaultPosition,
        )
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.ViewImage(filename)

    def zoom_initial(self, scale=1.0):
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(1, 1)  # set the ScrollRate to 1 in order for panning to work nicely
        self.Scroll(0, 0)
        self.zoomscale = scale
        self.clear_whole_window = False
        self.Refresh()

    def SetScrollRateSmart(self, newstep=None, printinfo=False):
        """changing scrollwindow scroll unit without scroll pos changing - utility.

        There is a slight jump when going from small scroll step e.g. 1 to large e.g. 20
        because the resolution isn't the same (scroll step might be 3 out of 10 instead of the
        more precise 30 out of 100).  I couldn't get rid of this jump, even by fiddling with
        the virtual size - might just have to live with it.
        and
        """
        oldstep = self.GetScrollPixelsPerUnit()[0]
        oldscrollx = self.GetScrollPos(wx.HORIZONTAL)
        oldscrolly = self.GetScrollPos(wx.VERTICAL)
        oldvirtx = self.GetVirtualSize()[0]
        oldvirty = self.GetVirtualSize()[1]
        # rot = event.GetWheelRotation()
        if printinfo:
            print(f"\nIN  step {oldstep} newstep {newstep} old scroll {oldscrollx}, {oldscrolly} virt {oldvirtx}, {oldvirty}")

        if newstep is not None:
            if oldstep == newstep:
                if printinfo:
                    print(f"Nothing to do, step of {newstep} already set.")
            else:
                q = newstep / oldstep  # min(1, newstep)
                newscrollx = int(oldscrollx / q)
                newscrolly = int(oldscrolly / q)
                # newvirtx = oldvirtx / q
                # newvirty = oldvirty / q
                # Aha - image size * step => virtual bounds
                newvirtx = int(self.maxWidth / newstep * self.zoomscale)
                newvirty = int(self.maxHeight / newstep * self.zoomscale)
                if printinfo:
                    print(f"OUT step {newstep}          new scroll {newscrollx}, {newscrolly} virt {newvirtx}, {newvirty} q {q}")

                self.SetScrollbars(
                    int(newstep), int(newstep),
                    int(newvirtx), int(newvirty),  # new virtual size
                    int(newscrollx), int(newscrolly),  # new scroll positions
                    noRefresh=True)
            # self.Refresh()
            if printinfo:
                print(self.GetVirtualSize())

    def onKeyChar(self, event):
        if event.GetKeyCode() >= 256:
            event.Skip()
            return
        if self.working:
            event.Skip()
            return
        self.working = True

        keycode = chr(event.GetKeyCode())
        # print("imgkeycode", keycode)

        if keycode == "a":
            self.SetScrollRateSmart(newstep=None, printinfo=True)

        # elif keycode in ["1", "2", "3", "4", "5", "6", "7", "8"]:
        #     todisplay = ord(keycode) - ord("1")
        #     self.snapshot_mgr.Restore(todisplay)  # snapshot 1 becomes 0 as a param
        #     self.mega_refresh()

        elif keycode == "d":
            self.SetScrollRateSmart(newstep=20, printinfo=True)
        elif keycode == "s":
            self.SetScrollRateSmart(newstep=1, printinfo=True)

        elif keycode == "e":
            self.clear_pen_lines()

        self.working = False

    def onKeyPress(self, event):  # ANDY
        keycode = event.GetKeyCode()
        # dbg(keycode)
        if event.ShiftDown():
            self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))

        if keycode == wx.WXK_ESCAPE:
            if self.working_fetching:
                frame = self.GetTopLevelParent()
                frame.SetStatusText("ESC key detected: PlantUML render Aborted")
                wx.PostEvent(frame, CancelRefreshPlantUmlEvent())
                self.user_aborted()
            else:
                if self.plantuml_text:
                    self.error_msg = ""  # clear any annoying error message, so can see bmp
                    self.Refresh()
                else:
                    self.error_msg = PLANTUML_VIEW_INITAL_HELP

        # if self.working:
        #     event.Skip()
        #     return
        # self.working = True
        #
        # keycode = event.GetKeyCode()  # http://www.wxpython.org/docs/api/wx.KeyEvent-class.html
        # self.working = False

        event.Skip()

    def onKeyUp(self, event):  # ANDY
        self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
        event.Skip()

    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight

    def OnErase(self, event):  # ANDY
        pass

    def OnWheelScroll(self, event):
        ## This is an example of what to do for the EVT_MOUSEWHEEL event,
        ## but since wx.ScrolledWindow does this already it's not
        ## necessary to do it ourselves.
        #
        # ANDY
        # But since I set the ScrollRate to 1
        # in order for panning to work nicely
        # scrolling is too slow.  So invoke this code!!
        #
        # dbg(f"OnWheelScroll {self.GetScrollPixelsPerUnit()}")

        if event.ControlDown():
            event.Skip()
            return

        # Version 1 - too jumpy
        # self.SetScrollRate(20, 20)

        # Version 2 - nicer, but need a common routine callable from multiple places
        #
        # oldscrollx = self.GetScrollPos(wx.HORIZONTAL)
        # oldscrolly = self.GetScrollPos(wx.VERTICAL)
        # # dbg(oldscrollx)
        # # dbg(oldscrolly)
        #
        # # How to adjust ?  take into account the 1 to 20 factor, as well as the zoom level
        # delta = event.GetWheelDelta()
        # rot = event.GetWheelRotation()
        # # dbg(delta)
        # # dbg(rot)
        # # if rot > 0:
        # if self.GetScrollPixelsPerUnit()[0] != 20:
        #     dbg(self.GetScrollPixelsPerUnit())
        #
        #     # dbg(oldscrollx)
        #     # dbg(oldscrolly)
        #     oldscrollx = oldscrollx /20#- (1 * rot) / 20 * self.zoomscale
        #     oldscrolly = oldscrolly /20#- (1 * rot) / 20 * self.zoomscale
        #     # oldscrollx = oldscrollx + 20 * rot / self.zoomscale
        #     # oldscrolly = oldscrolly + 20 * rot / self.zoomscale
        #     # dbg(oldscrollx)
        #     # dbg(oldscrolly)
        #
        #     self.SetScrollbars(
        #         20, 20,  # each scroll unit is 1 pixel, meaning scroll units match client coord units
        #         self.GetVirtualSize()[0] / 20, self.GetVirtualSize()[1] / 20,  # new virtual size
        #         oldscrollx, oldscrolly,  # new scroll positions
        #         noRefresh=True
        #     )

        # Version 3
        self.SetScrollRateSmart(20)

        # Old version 0 - complex and buggy and jumpy
        #
        # delta = event.GetWheelDelta()
        # rot = event.GetWheelRotation()
        # linesPer = event.GetLinesPerAction()
        # # print delta, rot, linesPer
        # linesPer *= 20  # ANDY trick to override the small ScrollRate
        # ws = self.mywheelscroll
        # ws = ws + rot
        # lines = ws / delta
        # ws = ws - lines * delta
        # self.mywheelscroll = ws
        # if lines != 0:
        #     lines = lines * linesPer
        #     vsx, vsy = self.GetViewStart()
        #     scrollTo = vsy - lines
        #     self.Scroll(-1, scrollTo)

        event.Skip()

    def OnResize(self, event):  # ANDY  interesting - GetVirtualSize grows when resize frame
        self.DebugSizez("resize")
        if self.NeedToClear() and self.IsShownOnScreen():
            self.clear_whole_window = True
            self.Refresh()

    def CalcVirtSize(self):
        # VirtualSize is essentially the visible picture
        return (self.maxWidth * self.zoomscale, self.maxHeight * self.zoomscale)

    def NeedToClear(self):
        # Since VirtualSize auto grows when resize frame, can't rely on it to know if client area is bigger than visible pic.
        # Need to rederive the original VirtualSize set when zoom calculated rather than relying on calls to self.GetVirtualSize()
        return (
            self.GetClientSize()[0] > self.CalcVirtSize()[0]
            or self.GetClientSize()[1] > self.CalcVirtSize()[1]
        )

    def DebugSizez(self, fromwheremsg):
        return
        if self.NeedToClear():
            msg = "!!!!!!! "
        else:
            msg = "!       "
        print(
            msg
            + "(%s) visible %d NeedToClear %s GetVirtualSize %d getWidth %d GetClientSize %d self.GetViewStart() %d self.maxWidth %d "
            % (
                fromwheremsg,
                self.IsShownOnScreen(),
                self.NeedToClear(),
                self.GetVirtualSize()[0],
                self.getWidth(),
                self.GetClientSize()[0],
                self.GetViewStart()[0],
                self.maxWidth,
            )
        )

    def OnPaint(self, event):  # ANDY
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        dc.SetUserScale(self.zoomscale, self.zoomscale)
        # since we're not buffering in this case, we have to
        # paint the whole window, potentially very time consuming.
        self.DoDrawing(dc)

    def Redraw(self, dc):
        self.DoDrawing(dc)

    def OnLeftDown(self, event):  # ANDY some PAN ideas from http://code.google.com/p/pyslip/
        """Left mouse button down. Prepare for possible drag."""
        if event.ShiftDown():
            event.Skip()
            return
        click_posn = event.GetPosition()
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        (self.last_drag_x, self.last_drag_y) = click_posn
        event.Skip()

    def OnLeftUp(self, event):  # ANDY PAN
        """Left mouse button up."""
        if event.ShiftDown():
            event.Skip()
            return
        self.last_drag_x = self.last_drag_y = None
        self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
        # turn off drag
        self.was_dragging = False
        # force PAINT event to remove selection box (if required)
        # self.Update()
        event.Skip()

    def OnMove(self, event):  # ANDY PAN
        """Handle a mouse move (map drag).
        event  the mouse move event
        """
        if event.ShiftDown():
            event.Skip()
            return

        # for windows, set focus onto pyslip window
        # linux seems to do this automatically
        if sys.platform == "win32" and self.FindFocus() != self:
            self.SetFocus()

        # get current mouse position
        (x, y) = event.GetPosition()
        # from common.architecture_support import whoscalling2
        # dbg(whoscalling2())

        # self.RaiseMousePositionEvent((x, y))

        if event.Dragging() and event.LeftIsDown():
            # are we doing box select?
            if not self.last_drag_x is None:
                # no, just a map drag
                self.was_dragging = True
                dx = self.last_drag_x - x
                dy = self.last_drag_y - y

                # dx /= 20
                # dy /= 20
                # dbg(dx)
                # dbg(dy)

                # print "PAN %d %d" % (dx, dy)
                # print self.GetViewStart()
                currx, curry = self.GetViewStart()
                self.Scroll(
                    currx + dx, curry + dy
                )  # Note The positions are in scroll units, not pixels, so to convert to pixels you will have to multiply by the number of pixels per scroll increment. If either parameter is -1, that position will be ignored (no change in that direction).
                # print "Scroll pan %d %d" % (currx+dx, curry+dy)

                # adjust remembered X,Y
                self.last_drag_x = x
                self.last_drag_y = y

            # redraw client area
            self.Update()

    def DoDrawing(self, dc, printing=False):
        # dbg(f"DoDrawing {len(self.curLine)}")

        if self.clear_whole_window:
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
            self.clear_whole_window = False

        if self.bmp:
            dc.DrawBitmap(self.bmp, 0, 0, False)  # false means don't use mask

            # dc.SetTextForeground('BLUE')
            # text = "UML via Pynsource and PlantUML"
            # dc.DrawText(text, 2, 2)

            self.DrawSavedLines(dc)

        if self.error_msg:
            dc.DrawText(self.error_msg, 2, 2)

        if self.fetching_msg and self.time_taken_fetching > 0.5:
            """
            Text is never drawn with the current pen.  It's drawn with the current 
            text color.  Try 
               dc.SetTextForeground((255,255,0)) 
            
            This is a historical implementation detail in Windows GDI.  The pen is 
            used for lines, the brush is used for fills, and text had its own 
            attributes.             
            """
            # dc.SetPen(wx.Pen("MEDIUM FOREST GREEN", 4))
            # dc.SetBrush(wx.Brush("RED"))
            # dc.SetTextForeground((204, 0, 0))  # red
            # dc.SetTextForeground((204, 102, 0))  # dark orange
            dc.SetTextForeground((255, 255, 255))  # white
            dc.SetTextBackground((0, 0, 0))  # black
            dc.SetBackgroundMode(wx.SOLID)
            dc.DrawText(self.fetching_msg, 2, 2)

    def DrawSavedLines(self, dc):  # PEN DRAWING
        dc.SetPen(wx.Pen("MEDIUM FOREST GREEN", 4))
        for line in self.lines:
            for coords in line:
                dc.DrawLine(*map(int, coords))

    def OnClearPenLines(self, event):
        self.clear_pen_lines()

    def clear_pen_lines(self):
        self.lines = []
        self.Refresh()

    def SetXY(self, event):  # PEN DRAWING
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):  # PEN DRAWING
        newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        newpos = (
            newpos[0] * self.GetScaleX() / self.zoomscale,
            newpos[1] * self.GetScaleY() / self.zoomscale,
        )
        return newpos

    def OnRightButtonEvent(self, event):  # PEN DRAWING - ANDY
        if event.ShiftDown():
            self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))
            self.clear_pen_lines()
        event.Skip()

    def OnLeftButtonEvent(self, event):  # PEN DRAWING
        if event.ShiftDown():
            self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))

        if event.LeftDown():
            # self.SetScrollRate(1, 1)  # works to slow the scrolling, but causes scroll jump to 0,0
            self.SetScrollRateSmart(1)  # smoother pan when scroll step is 1

            # dbg(f"LeftDown {self.GetScrollPixelsPerUnit()}")
            self.SetFocus()
            self.SetXY(event)
            self.curLine = []
            self.CaptureMouse()
            self.drawing = True

        elif event.Dragging() and self.drawing:
            # print("dragging.....")

            # ANDY UPDATE 2019 - Drawing to wx.ClientDC doesn't work well these days and you only
            # see the result when an on paint occurs much later - and often cannot force the paint?
            # instead, issue a Refresh() which triggers a paint, and draw there instead.
            coords = (self.x, self.y) + self.ConvertEventCoords(event)
            self.curLine.append(coords)
            self.lines.append(self.curLine)
            self.curLine = []
            self.SetXY(event)  # reset line drawing start point to current mouse pos
            self.Refresh()

            # Version 0. Old version.draw directly to a wx.ClientDC
            # dc = wx.ClientDC(self)
            # self.PrepareDC(dc)
            # dc.SetUserScale(self.zoomscale, self.zoomscale)
            #
            # dc.SetPen(wx.Pen("MEDIUM FOREST GREEN", 4))
            # coords = (self.x, self.y) + self.ConvertEventCoords(event)
            # self.curLine.append(coords)  # For when we are not double buffering  #ANDY
            # dc.DrawLine(*coords)
            # self.SetXY(event)
            #
            # Failed Hacks to try and make version 0 work.
            #
            # self.Refresh()  # ANDY added, pheonix
            # # frame = self.GetTopLevelParent()
            # # frame.Layout()  # needed when running phoenix
            # self.Update()  # or wx.SafeYield()  # Without this the nodes don't paint during a "L" layout (edges do!?)
            # wx.SafeYield()  # Needed on Mac to see result if in a compute loop.
            # self.repaint_needed = True

        elif event.LeftUp() and self.drawing:
            self.lines.append(self.curLine)
            self.curLine = []
            self.ReleaseMouse()
            self.drawing = False

            self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
            self.Refresh()  # ANDY added, pheonix

class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        ImageViewer(self)


class App(wx.App):
    def OnInit(self):
        frame = TestFrame(None, title="Andy Image Viewer")
        frame.Show(True)
        frame.Centre()
        return True


if __name__ == "__main__":
    app = App(0)
    app.MainLoop()
