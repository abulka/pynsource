import wx
from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
import asyncio
from asyncio.events import get_event_loop
import time

class TestFrame(wx.Frame):
    def __init__(self, parent=None):
        super(TestFrame, self).__init__(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        button1 =  wx.Button(self, label="Submit")
        self.edit =  wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL|wx.ST_NO_AUTORESIZE)
        self.edit_timer =  wx.StaticText(self, style=wx.ALIGN_CENTRE_HORIZONTAL|wx.ST_NO_AUTORESIZE)
        vbox.Add(button1, 2, wx.EXPAND|wx.ALL)
        vbox.AddStretchSpacer(1)
        vbox.Add(self.edit, 1, wx.EXPAND|wx.ALL)
        vbox.Add(self.edit_timer, 1, wx.EXPAND|wx.ALL)
        self.SetSizer(vbox)
        self.Layout()
        AsyncBind(wx.EVT_BUTTON, self.async_callback, button1)
        StartCoroutine(self.update_clock, self)
        
    async def async_callback(self, event):
        self.edit.SetLabel("Button clicked")
        await asyncio.sleep(1)
        self.edit.SetLabel("Working")
        await asyncio.sleep(1)
        self.edit.SetLabel("Completed")

    async def update_clock(self):
        while True:
            self.edit_timer.SetLabel(time.strftime('%H:%M:%S'))
            await asyncio.sleep(0.5)
            
app = WxAsyncApp()
frame = TestFrame()
frame.Show()
app.SetTopWindow(frame)
loop = get_event_loop()
loop.run_until_complete(app.MainLoop())

