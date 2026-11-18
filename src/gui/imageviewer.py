# PlantUML image viewer (zoom + save)

import wx
import sys
import os

from gui.coord_utils import ZoomInfo
from typing import List, Set, Dict, Tuple, Optional
from common.gui_imageviewer import ImageViewer

ZOOM_INCR = 0.03


class PynsourceImageViewer(ImageViewer):
    def __init__(self, parent, id=-1, size=wx.DefaultSize):
        ImageViewer.__init__(self, parent, id=-1, size=wx.DefaultSize)

        self.zoomscale = 1.0
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheelZoom)
        # self.plantuml_text = ""

    async def ViewImage(self, thefile="", url=""):
        await ImageViewer.ViewImage(self, thefile, url)
        self.zoom_initial()

    def OnHandleSaveImage(self, event):
        self.SaveImage(self.bmp, format="png")

    def OnHandleSaveSvg(self, event):
        self.SavePlantUmlImage(default_format="svg")

    def SavePlantUmlImage(self, default_format="svg"):
        """Export the PlantUML diagram, offering SVG (default) and PNG.

        SVG export writes the raw vector bytes fetched from the server, so it
        stays sharp at any size. PNG export writes the displayed bitmap.
        """
        frame = self.GetTopLevelParent()

        thisdir = self.context.config.get("LastDirInsertImage", os.path.expanduser("~/"))

        svg_bytes = None
        if getattr(self, "plantuml_text", None):
            from generate_code.gen_plantuml import plant_uml_fetch_svg
            plantuml_server_local_url = self.context.config.get("PlantUmlServerUrl", None)
            frame.SetStatusText("Fetching PlantUML SVG for export...")
            try:
                svg_bytes = plant_uml_fetch_svg(self.plantuml_text, plantuml_server_local_url)
            finally:
                frame.SetStatusText("")

        has_svg = bool(svg_bytes)
        if has_svg:
            wildcard = "SVG vector image (*.svg)|*.svg|PNG image (*.png)|*.png"
        else:
            wildcard = "PNG image (*.png)|*.png"

        dlg = wx.FileDialog(
            parent=frame,
            message="Save PlantUML image",
            defaultDir=thisdir,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_SAVE,
            pos=wx.DefaultPosition,
        )
        if has_svg:
            dlg.SetFilterIndex(0 if default_format == "svg" else 1)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if filename.lower().endswith(".svg") and has_svg:
                with open(filename, "wb") as fp:
                    fp.write(svg_bytes)
            else:
                if not filename.lower().endswith(".png"):
                    filename += ".png"
                self.bmp.SaveFile(filename, wx.BITMAP_TYPE_PNG)
            self.context.config["LastDirInsertImage"] = dlg.GetDirectory()  # remember dir path
            self.context.config.write()
        dlg.Destroy()

    def OnHandleSaveImagePreserveTransparencies(self, event):
        self.SaveImage(self.bmp_transparent_ori, format="png")

    def OnHandleSaveImageInclDoodles(self, event):
        """
        Draw the whole client area into a fresh new bitmap
        Dont use PrepareDC since scrolling not an issue in this 'in memory' rendering (re PrepareDC: If your image is on a scrolled window, then you have two coordinate systems -- the "virtual" one and the actual pixel coords of the window in its current position. PrepareDC() sets up the DC to deal with that, so you can draw in the virtual coordinate system.)
        """
        # Version 1 - doesn't work anymore - crashes in DoDrawing()? invalid dc
        # bmp, dc = self._CreateNewWhiteBmp(self.bmp.GetWidth(), self.bmp.GetHeight())
        # dc.SetUserScale(self.zoomscale, self.zoomscale)
        # self.DoDrawing(dc)
        # dc.SelectObject(wx.NullBitmap)

        # Version 2 - works (set the scale if you want WYSIWYG, but this will save slightly incorrectly, with scrollpos not taken into account)
        # https://stackoverflow.com/questions/2195792/saving-an-image-of-what-a-device-context-drew-wxpython
        bmp = wx.Bitmap(self.bmp.GetWidth(), self.bmp.GetHeight())
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        # dc.SetUserScale(self.zoomscale, self.zoomscale)
        self.DoDrawing(dc)
        dc.SelectObject(wx.NullBitmap)

        self.SaveImage(bmp, format="png")

    def zoom_to_fit(self):

        def calc2(margin=20):
            client_sizex, client_sizey = self.GetClientSize()
            client_sizex -= margin
            client_sizey -= margin
            return self.maxWidth, self.maxHeight, client_sizex, client_sizey

        def calc_scale(shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey, debug=True):
            ratio_x = client_sizex / shapes_bounds_x
            ratio_y = client_sizey / shapes_bounds_y
            ratio = min(ratio_x, ratio_y)
            # new_scale = ratio / self.scalex
            new_scale = ratio
            if debug:
                print(
                    f"dBOUNDS {int(shapes_bounds_x)}, {int(shapes_bounds_y)} "
                    "Scale ", self.zoomscale,
                    "New Scale ", new_scale,
                    " | "
                    f"GetClientSize {self.GetClientSize()} "
                    f"ratio {ratio:5.4f} out of ({ratio_x:4.1f}, {ratio_y:3.1f}) | ",
                    f"DELTA {new_scale - self.zoomscale:3.1f}")
            return new_scale


        shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey = calc2()
        new_scale = calc_scale(shapes_bounds_x, shapes_bounds_y, client_sizex, client_sizey, debug=False)

        # self._zoom(set_to_scale=new_scale)

        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(1, 1)  # set the ScrollRate to 1 in order for panning to work nicely
        self.Scroll(0, 0)
        self.zoomscale = new_scale
        self.clear_whole_window = False
        self.Refresh()

    def OnHandleSaveImageInclDoodles(self, event):
        """
        Draw the whole client area into a fresh new bitmap
        Dont use PrepareDC since scrolling not an issue in this 'in memory' rendering (re PrepareDC: If your image is on a scrolled window, then you have two coordinate systems -- the "virtual" one and the actual pixel coords of the window in its current position. PrepareDC() sets up the DC to deal with that, so you can draw in the virtual coordinate system.)
        """
        # Version 1 - doesn't work anymore - crashes in DoDrawing()? invalid dc
        # bmp, dc = self._CreateNewWhiteBmp(self.bmp.GetWidth(), self.bmp.GetHeight())
        # dc.SetUserScale(self.zoomscale, self.zoomscale)
        # self.DoDrawing(dc)
        # dc.SelectObject(wx.NullBitmap)

        # Version 2 - works (set the scale if you want WYSIWYG, but this will save slightly incorrectly, with scrollpos not taken into account)
        # https://stackoverflow.com/questions/2195792/saving-an-image-of-what-a-device-context-drew-wxpython
        bmp = wx.Bitmap(self.bmp.GetWidth(), self.bmp.GetHeight())
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        # dc.SetUserScale(self.zoomscale, self.zoomscale)
        self.DoDrawing(dc)
        dc.SelectObject(wx.NullBitmap)

        self.SaveImage(bmp, format="png")

    def OnViewPlantUmlMarkup(self, event, alt_down=False):
        # inherited from ImageViewer in common/gui_imageviewer.py, which shows the
        # generated markup together with the two copy-to-clipboard buttons
        ImageViewer.OnViewPlantUmlMarkup(self, event, alt_down)

    def SaveImage(self, bmp, format="png"):
        frame = self.GetTopLevelParent()

        thisdir = self.context.config.get("LastDirInsertImage", os.path.expanduser("~/"))

        dlg = wx.FileDialog(
            parent=frame,
            message="Save PlantUML image (.png)",
            defaultDir=thisdir,
            defaultFile="",
            wildcard="*.png",
            style=wx.FD_SAVE,
            pos=wx.DefaultPosition,
        )
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            bmp.SaveFile(filename, wx.BITMAP_TYPE_PNG)
            self.context.config["LastDirInsertImage"] = dlg.GetDirectory()  # remember dir path
            self.context.config.write()
        dlg.Destroy()


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
                newscrollx = oldscrollx / q
                newscrolly = oldscrolly / q
                # newvirtx = oldvirtx / q
                # newvirty = oldvirty / q
                # Aha - image size * step => virtual bounds
                newvirtx = self.maxWidth / newstep * self.zoomscale
                newvirty = self.maxHeight / newstep * self.zoomscale
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

    def OnWheelZoom(self, event):  # ANDY
        # dbg(f"OnWheelZoom {self.GetScrollPixelsPerUnit()}")
        # self.SetScrollRate(1, 1)
        delta = event.GetWheelDelta()
        rot = event.GetWheelRotation()
        if event.ControlDown():
            self.zoom(rot > 0)
        else:
            event.Skip()

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

    def mouse_pos_in_client_coords(self):
        """Converts screen mouse position into client coords that takes into account scroll and zoom"""
        mouse_client_x, mouse_client_y = self.ScreenToClient(wx.GetMousePosition())
        scroll_pos_x, scroll_pos_y = self.GetViewStart()
        x = (mouse_client_x + scroll_pos_x) / self.zoomscale
        y = (mouse_client_y + scroll_pos_y) / self.zoomscale
        return x, y

    def calc_pan_offsets(self, zoom_info):
        offsetx = 0
        offsety = 0
        zoom_point_x = zoom_point_y = None
        if zoom_info and zoom_info.delta != None:  # if have a zoom_info, then might have delta too
            scale_change = zoom_info.delta
            zoom_point_x, zoom_point_y = self.mouse_pos_in_client_coords()
            offsetx = (zoom_point_x * scale_change)
            offsety = (zoom_point_y * scale_change)
        return offsetx, offsety, zoom_point_x, zoom_point_y

    def prepare_zoom_info(self, delta=None):
        return ZoomInfo(scale=self.zoomscale, delta=delta)

    def zoom(self, out=True, reset=False, zoom_incr=ZOOM_INCR):

        self.SetScrollRateSmart(1)

        old_scalex = self.zoomscale

        if reset:
            self.zoomscale = 1.0
        else:
            amount = zoom_incr if out else -zoom_incr
            self.zoomscale = max(self.zoomscale + amount, 0.3)  # prevent zooming too far out
            self.zoomscale = min(self.zoomscale, 5.0)  # prevent zooming too far in
        if self.zoomscale == 0:
            self.zoomscale = 1.0

        deltax = self.zoomscale - old_scalex
        zoom_info = self.prepare_zoom_info(delta=deltax)

        bounds_width, bounds_height = self.maxWidth, self.maxHeight
        # virt_width, virt_height = self.GetVirtualSize()
        oldscrollx = self.GetScrollPos(wx.HORIZONTAL)
        oldscrolly = self.GetScrollPos(wx.VERTICAL)
        offsetx, offsety, zoom_point_x, zoom_point_y = self.calc_pan_offsets(zoom_info)

        DEBUG = False
        if DEBUG:
            if zoom_info:
                print(
                  f"BOUNDS ({int(bounds_width):4d},{int(bounds_height):4d}) * "
                  f"Scale {zoom_info.scale:3.1f} => "
                  f"{int(bounds_width * zoom_info.scale):4d},{int(bounds_height * zoom_info.scale):4d}  |  "
                  f"PAN ({oldscrollx:3d},{oldscrolly:3d})",
                  f"+ {int(offsetx):-3d},{int(offsety):-3d} ",
                  f"=> {int(oldscrollx + offsetx):-3d},{int(oldscrolly + offsety):-3d}",
                  end=" ")
                if zoom_info.delta:
                    print(f"  |  DELTA {zoom_info.delta:-5.2f} |  zoom_point {zoom_point_x},{zoom_point_y}")
                else:
                    print()
        bounds_width *= zoom_info.scale
        bounds_height *= zoom_info.scale

        if self.GetScrollPixelsPerUnit()[0] != 1:
            bounds_width *= 20
            bounds_height *= 20

        # _do_resize_virtual_canvas_tofit_bounds
        scroll_offsets: Tuple = (offsetx, offsety)

        oldscrollx = self.GetScrollPos(wx.HORIZONTAL)
        oldscrolly = self.GetScrollPos(wx.VERTICAL)

        if scroll_offsets:
            offsetx, offsety = scroll_offsets
            oldscrollx += offsetx
            oldscrolly += offsety

        # https://wxpython.org/Phoenix/docs/html/wx.Scrolled.html#wx.Scrolled.SetScrollbars
        self.SetScrollbars(
            1, 1,  # each scroll unit is 1 pixel, meaning scroll units match client coord units
            int(bounds_width), int(bounds_height),  # new virtual size
            int(oldscrollx), int(oldscrolly),  # new scroll positions
            noRefresh=True
        )


        # # Not sure this logic is any good - need to zoom towards mouse pointer properly
        # if out:
        #     jumptox, jumptoy = (
        #         self.GetViewStart()[0] * zoom_incr,
        #         self.GetViewStart()[1] * zoom_incr,
        #     )
        # else:
        #     jumptox, jumptoy = (
        #         self.GetViewStart()[0] / zoom_incr,
        #         self.GetViewStart()[1] / zoom_incr,
        #     )
        #
        # jumptox, jumptoy = 0, 0  # ANDY FUN
        # # jumptox, jumptoy = self.GetViewStart()[0] + amount, self.GetViewStart()[0] - amount  # ANDY FUN
        #
        # self.SetVirtualSize(self.CalcVirtSize())
        # self.SetScrollbars(
        #     1, 1, self.GetVirtualSize()[0], self.GetVirtualSize()[1], jumptox, jumptoy, True
        # )  # boolean is skip refresh or not, doesn't seem to matter

        # # If zoom out so much you need to clear the whole window to get rid of bigger image remnants
        # if self.NeedToClear():
        #     # ANDY - still need this?
        #     # self.clear_whole_window = True
        #     self.SetScrollbars(
        #         1, 1, self.GetVirtualSize()[0], self.GetVirtualSize()[1], 0, 0, True
        #     )  # workaround a bug where whole screen doesn't clear if you are scrolled to the right and y is non scrolled, and you zoom out - you see a screen fragment not erased
        # self.DebugSizez("zoom")

        self.Refresh()


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
