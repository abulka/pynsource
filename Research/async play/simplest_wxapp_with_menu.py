import wx
import time

# requires
# pip install git+https://github.com/sirk390/wxasync.git@7a7574126bbea3c1e151995bf6f03ed07e0b2fbf  <- note commit
from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
import asyncio
from asyncio.events import get_event_loop

class MainApp(WxAsyncApp):
# class MainApp(wx.App):

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
        menu1.Append(id, "test - async call\tCtrl-1")

        # self.Bind(wx.EVT_MENU, self.callback, id=id)
        # AsyncBind(wx.EVT_MENU, self.async_callback, id)
        AsyncBind(wx.EVT_MENU, self.async_callback, menu1, id=id)

        menuBar.Append(menu1, "&Experiments")
        self.frame.SetMenuBar(menuBar)

    def callback(self, event):
        self.frame.SetStatusText("Menu item clicked")
        wx.SafeYield()
        time.sleep(2)
        self.frame.SetStatusText("Working")
        wx.SafeYield()
        time.sleep(2)
        self.frame.SetStatusText("Completed")

    async def async_callback(self, event):
        self.frame.SetStatusText("Button clicked")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Working")
        await asyncio.sleep(1)
        self.frame.SetStatusText("Completed")

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
