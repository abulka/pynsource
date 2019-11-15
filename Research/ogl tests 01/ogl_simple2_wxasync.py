"""
UNFINISHED attempt to make wxasync bug appear re event slowdown

failed to repro cos 

1. main app is not from WxAsyncApp - which is critical - 
    need to refactor to be the same design as pynsourceGui app/frame bootup
2. the bug ended up to be caused by 
    wx.SafeYield()  # this causes slowdown of eventing over time - dangerous!
    in layout
"""

import wx
import wx.lib.ogl as ogl
import random

# sys.path.append("../../src/gui")
from gui.repair_ogl import repairOGL
repairOGL()

ASYNC = True

if ASYNC:
    from appdirs import AppDirs  # pip install appdirs
    from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
    import asyncio
    import aiohttp
    from asyncio.events import get_event_loop

def setpos(shape, x, y):
    width, height = shape.GetBoundingBoxMax()
    shape.SetX(x + width / 2)
    shape.SetY(y + height / 2)

def getpos(shape):
    width, height = shape.GetBoundingBoxMax()
    x = shape.GetX()
    y = shape.GetY()
    return (x - width / 2, y - height / 2)

class AppFrame(wx.Frame):
# class MainApp(WxAsyncApp):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Demo", size=(700, 700), style=wx.DEFAULT_FRAME_STYLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # put stuff into sizer

        canvas = ogl.ShapeCanvas(self)
        sizer.Add(canvas, 1, wx.GROW)

        canvas.SetBackgroundColour("LIGHT BLUE")  #

        diagram = ogl.Diagram()
        canvas.SetDiagram(diagram)
        diagram.SetCanvas(canvas)

        # shape = ogl.RectangleShape(60, 60)
        # shape.SetX(30)
        # shape.SetY(30)
        # print(shape.GetBoundingBoxMax())
        # canvas.AddShape(shape)

        # shape = ogl.RectangleShape(60, 60)
        # shape.SetX(90)
        # shape.SetY(30)
        # canvas.AddShape(shape)

        # shape = ogl.RectangleShape(160, 160)
        # shape.SetX(250)
        # shape.SetY(130)
        # canvas.AddShape(shape)

        # diagram.ShowAll(1)

        # apply sizer
        # self.SetSizer(sizer)
        # self.SetAutoLayout(1)
        # self.Show(1)

    # def BootStrap(self):
        y = 0
        
        # for x in range(0, 1200, 70):
        for x in range(0, 600, 70):
            shape = ogl.RectangleShape(60, 60)
            shape.AddText("%d,%d" % (x, y))
            setpos(shape, x, y)
            diagram.AddShape(shape)

            y += 70

        diagram.ShowAll(1)
        self.Show(1)
        
        canvas.Bind(wx.EVT_LEFT_DCLICK, self.OnXXX)
        
        self.diagram = diagram  # remember
        self.canvas = canvas  # remember

        if ASYNC:
            StartCoroutine(self.YYY, self)

    async def YYY(self):
        # await asyncio.sleep(15)
        # print("hanging back even longer from doing a version check...")
        await asyncio.sleep(3)
        print("YYY did some async")
        # url = WEB_VERSION_CHECK_URL_TRACKED_DEVEL if self._running_andy_development_mode() else WEB_VERSION_CHECK_URL_TRACKED
        # status_code = 0
        # try:
        #     data, status_code = await url_to_data(url)
        #     response_text = data.decode('utf-8')
        #     # info = json.loads(response_text)
        #     info = eval(response_text)
        # # except (ConnectionError, requests.exceptions.RequestException) as e:
        # #     # log.exception("Trying to render using plantuml server %s str(e)" % plant_uml_server)
        # #     log.error(
        # #         f"Error trying to fetch initial html from plantuml server {plant_uml_server} {str(e)}")
        # #     return None
        # except asyncio.TimeoutError as e:  # there is no string repr of this exception
        #     print("time out getting latest version info")
        # except aiohttp.client_exceptions.ClientConnectorError as e:
        #     print("connection error (no internet?) getting latest version info")
        # else:
        #     print(f"checked url for updates: {url}")

        # if status_code == 200:
        #     self._update_alert(info, alert_even_if_running_latest=False)


    def OnXXX(self, event):
        for shape in self.diagram.GetShapeList():
            x = random.randint(0,500)
            y = random.randint(0,500)
            setpos(shape, x, y)
        self.canvas.Draw()
        self.canvas.Refresh()

def main():
    # application = MainApp(0)
    # # application = MainApp(redirect=True, filename='/tmp/pynsource.log')  # to view what's going on
    # application.MainLoop()

    app = wx.PySimpleApp()
    ogl.OGLInitialize()
    frame = AppFrame()
    app.MainLoop()
    app.Destroy()

def main_async():
    # see https://github.com/sirk390/wxasync
    # application = MainApp(0)
    # loop = get_event_loop()
    # loop.run_until_complete(application.MainLoop())

    app = wx.PySimpleApp()
    ogl.OGLInitialize()
    frame = AppFrame()
    loop = get_event_loop()
    loop.run_until_complete(app.MainLoop())

    # Let's also cancel all running tasks:
    # https://stackoverflow.com/questions/37278647/fire-and-forget-python-async-await
    pending = asyncio.Task.all_tasks()
    for task in pending:
        # print("Cancelling leftover task...", task._coro.cr_code.co_name, task._state)
        task.cancel()
        # Now we should await task to execute it's cancellation.
        # Cancelled task raises asyncio.CancelledError that we can suppress:
        with suppress(asyncio.CancelledError):
            loop.run_until_complete(task)


if __name__ == "__main__":
    if ASYNC:
        main_async()
    else:
        main()