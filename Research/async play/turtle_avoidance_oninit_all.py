# Demonstrates invoking async methods from inside regular methods using
# a call to StartCoroutine() and also by the technique of emitting a custom event
# which is bound using AsyncBind to an asynchronous method. All works!
# Uses architecture where frame is created inside app OnInit.

import wx
import time

# requires
# pip install git+https://github.com/sirk390/wxasync.git@7a7574126bbea3c1e151995bf6f03ed07e0b2fbf  <- note commit
# pip install git+https://github.com/sirk390/wxasync.git@a2aa71eca525169f996be46a4515674028c8e6f5  <- better

from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
import asyncio
from asyncio.events import get_event_loop
import wx.lib.newevent

SomeNewEvent, EVT_SOME_NEW_EVENT = wx.lib.newevent.NewEvent()
SomeNewEventAsync, EVT_SOME_NEW_EVENT_ASYNC = wx.lib.newevent.NewEvent()

class MainApp(WxAsyncApp):
    def OnInit(self):
        self.frame = wx.Frame(None, -1, "test",)
        self.frame.CreateStatusBar()
        self.frame.Show(True)
        self.clock_on = False
        self.InitMenus()
        return True

    def InitMenus(self):
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()

        id = wx.NewIdRef()
        menu1.Append(id, "AsyncBind (original wxasync example)\tCtrl-1")
        AsyncBind(wx.EVT_MENU, self.async_callback, menu1, id=id)

        id = wx.NewIdRef()
        menu1.Append(id, "Start/stop clock via StartCoroutine()\tCtrl-2")
        self.Bind(wx.EVT_MENU, self.regular_func_starts_coroutine, id=id)

        id = wx.NewIdRef()
        menu1.Append(id, "Emit Custom Event (sync)\tCtrl-3")
        self.Bind(wx.EVT_MENU, self.regular_func_raises_custom_event, id=id)
        self.Bind(EVT_SOME_NEW_EVENT, self.callback)  # bind custom event to synchronous handler - works OK

        id = wx.NewIdRef()
        menu1.Append(id, "Emit Custom Event (async)\tCtrl-4")
        self.Bind(wx.EVT_MENU, self.regular_func_raises_custom_async_event, id=id)
        AsyncBind(EVT_SOME_NEW_EVENT_ASYNC, self.async_callback, self.frame)  # don't specify id, and use self.frame not self

        # Finalise menu
        menuBar.Append(menu1, "&Experiments")
        self.frame.SetMenuBar(menuBar)

    def regular_func_raises_custom_event(self, event):
        print("trigger demo via custom event")
        # Create and post the event
        evt = SomeNewEvent(attr1="hello", attr2=654)
        wx.PostEvent(self, evt)

    def regular_func_raises_custom_async_event(self, event):
        print("trigger async demo via custom event")
        # Create and post the event
        evt = SomeNewEventAsync(attr1="hello", attr2=654)
        wx.PostEvent(self.frame, evt)  # send to frame not self to avoid EVT_WINDOW_DESTROY shutdown error

    def regular_func_starts_coroutine(self, event):
        self.clock_on = not self.clock_on
        if self.clock_on:
            print(f"triggering an async call via StartCoroutine()")
            StartCoroutine(self.update_clock, self)
        else:
            print("clock flag off, coroutine will stop looping, drop through and complete")

    # --------

    def callback(self, event):
        self.frame.SetStatusText("Menu item clicked (synchronous)")
        wx.SafeYield()
        time.sleep(1)
        self.frame.SetStatusText("Working (synchronous)")
        wx.SafeYield()
        time.sleep(1)
        self.frame.SetStatusText("Completed (synchronous)")
        wx.SafeYield()
        time.sleep(1)
        self.frame.SetStatusText("")

    async def async_callback(self, event):
        self.frame.SetStatusText("Menu item clicked")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Working")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Completed")
        await asyncio.sleep(1)
        self.frame.SetStatusText("")

    async def update_clock(self):
        while self.clock_on:
            self.frame.SetStatusText(time.strftime('%H:%M:%S'))
            await asyncio.sleep(0.5)
        self.frame.SetStatusText("")

def main():
    application = MainApp(0)
    application.MainLoop()

def main_async():
    # see https://github.com/sirk390/wxasync
    application = MainApp(0)
    loop = get_event_loop()
    loop.run_until_complete(application.MainLoop())

if __name__ == "__main__":
    # main()
    main_async()
