# shows how coroutine calls fails because of
# frame is created inside app OnInit architecture.
#
# update - but now works cos of fix in
# git+https://github.com/sirk390/wxasync.git@a2aa71eca525169f996be46a4515674028c8e6f5
# 
# but now is broken again as of 0.42
# reported https://github.com/sirk390/wxasync/issues/12 
# 
import wx
import time
# from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
from wxasync041 import AsyncBind, WxAsyncApp, StartCoroutine  # OK
# from wxasync042 import AsyncBind, WxAsyncApp, StartCoroutine  # FAILS
import asyncio
from asyncio.events import get_event_loop
import wx.lib.newevent

SomeNewEvent, EVT_SOME_NEW_EVENT = wx.lib.newevent.NewEvent()

class MainApp(WxAsyncApp):

    def OnInit(self):
        self.frame = wx.Frame(None, -1, "test",)
        self.frame.CreateStatusBar()
        self.frame.Show(True)
        StartCoroutine(self.async_callback, self)
        return True

    async def async_callback(self):
        self.frame.SetStatusText("Button clicked")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Working")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Completed")

def main_async():
    application = MainApp(0)
    loop = get_event_loop()
    loop.run_until_complete(application.MainLoop())

if __name__ == "__main__":
    main_async()
