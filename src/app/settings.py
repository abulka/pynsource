import wx.lib.newevent

ASYNC = True

RefreshPlantUmlEvent, EVT_REFRESH_PLANTUML_EVENT = wx.lib.newevent.NewEvent()
CancelRefreshPlantUmlEvent, EVT_CANCEL_REFRESH_PLANTUML_EVENT = wx.lib.newevent.NewEvent()

LOG_FILENAME = "/tmp/pynsource_debug.log"
LOG_TO_CONSOLE = False
