#!/usr/bin/env pythonw

import wx
import wx.adv
import wx.lib.embeddedimage

WXPdemo = wx.lib.embeddedimage.PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAWlJ"
    "REFUWIW1V1sSwjAIBMebeBU9db2KZ8EPmxbCI4TUnXGskWaXDQktwhjErjERP4XRhER08iPi"
    "5SKiyQR5JyI7xxB3j7wn5GI6V2hFxM0gJtjYANFBiIjQu7L/1lYlwR0QxLDZhE0II1+CtwRC"
    "RI8riBva7DL7CC9VAwDbbxwKtdDXwBi7K+1zCP99T1vDFedd8FBwYd6BCAUXuACEF7QsbET/"
    "FaHs+gDQw4vOLNHkMojAnTw8nlNipIiwmR0DCXJbjCXkFCAL23BnpQgRWt1EMbyujCK9AZzZ"
    "f+b3sX0oSqJQ6EorFeT4NiL6Wtj0+LXnQAzThYoAAsN6ehqR3sHExmcEqGeFApQLcTvm5Kt9"
    "wkHGgb+RZwSkyc1dwOcpCtCoNKSz6FRCUQ3o7Nn+5Y+Lg+y5CIXlcyAk99ziiQS32+svz/UY"
    "vClJoLpIC8gi+VwwfDecEiEtT/WZTJDf94uk1Ru8vbz0cvoF7S2DnpeVL9UAAAAASUVORK5C"
    "YII=")

class DemoTaskBarIcon(wx.adv.TaskBarIcon):
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE   = wx.NewId()
    TBMENU_CHANGE  = wx.NewId()
    TBMENU_REMOVE  = wx.NewId()

    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame

        # Set the image
        icon = self.MakeIcon(WXPdemo.GetImage())
        self.SetIcon(icon, "wxPython Demo")
        self.imgidx = 1

        # bind some events
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarActivate)
        self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)


    def CreatePopupMenu(self):
        """
        This method is called by the base class when it needs to popup
        the menu for the default EVT_RIGHT_DOWN event.  Just create
        the menu how you want it and return it from this function,
        the base class takes care of the rest.
        """
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "Restore wxPython Demo")
        menu.Append(self.TBMENU_CLOSE,   "Close wxPython Demo")
        return menu


    def MakeIcon(self, img):
        """
        The various platforms have different requirements for the
        icon size...
        """
        if "wxMSW" in wx.PlatformInfo:
            img = img.Scale(16, 16)
        elif "wxGTK" in wx.PlatformInfo:
            img = img.Scale(22, 22)
        # wxMac can be any size upto 128x128, so leave the source img alone....
        icon = wx.Icon(img.ConvertToBitmap() )
        return icon


    def OnTaskBarActivate(self, evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()


    def OnTaskBarClose(self, evt):
        wx.CallAfter(self.frame.Close)



class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Hello World")
        self.tbicon = DemoTaskBarIcon(self)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def OnCloseWindow(self, evt):
        self.tbicon.Destroy()
        evt.Skip()


app = wx.App(redirect=False)
frame = MainFrame(None)
frame.Show(True)
app.MainLoop()
