import wx.lib.newevent

ASYNC = True

RefreshPlantUmlEvent, EVT_REFRESH_PLANTUML_EVENT = wx.lib.newevent.NewEvent()
CancelRefreshPlantUmlEvent, EVT_CANCEL_REFRESH_PLANTUML_EVENT = wx.lib.newevent.NewEvent()
