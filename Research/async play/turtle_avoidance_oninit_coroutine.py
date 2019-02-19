# shows how coroutine calls fails because of
# frame is created inside app OnInit architecture.
#
# update - but now works cos of fix in
# git+https://github.com/sirk390/wxasync.git@a2aa71eca525169f996be46a4515674028c8e6f5

import wx
import time
from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
import asyncio
from asyncio.events import get_event_loop
import wx.lib.newevent

SomeNewEvent, EVT_SOME_NEW_EVENT = wx.lib.newevent.NewEvent()

class MainApp(WxAsyncApp):

    def OnInit(self):
        self.frame = wx.Frame(None, -1, "test",)
        self.frame.CreateStatusBar()
        self.frame.Show(True)
        self.InitMenus()
        return True

    def InitMenus(self):
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()

        id = wx.NewIdRef()
        menu1.Append(id, "test - call StartCoroutine() \tCtrl-1")
        self.Bind(wx.EVT_MENU, self.func_calls_start_coroutine, id=id)

        # Finalise
        menuBar.Append(menu1, "&Experiments")
        self.frame.SetMenuBar(menuBar)

    def func_calls_start_coroutine(self, event):
        StartCoroutine(self.async_callback, self)

    async def async_callback(self):
        self.frame.SetStatusText("Button clicked")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Working")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Completed")

def main_async():
    # see https://github.com/sirk390/wxasync
    application = MainApp(0)
    loop = get_event_loop()
    loop.run_until_complete(application.MainLoop())

if __name__ == "__main__":
    main_async()
