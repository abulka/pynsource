import wx
import wx.lib.mixins.inspection as wit

"""
Seems to be a keycode focus issue when triggering
inspector.  

only when focus is in a text control does CMD ALT I launching work

official example is broken
# https://wxpython.org/Phoenix/docs/html/wx.lib.mixins.inspection.html

latest official examples work, but they don't use normal
frames and instead cheat' and all use
wx.lib.sized_controls as sc
frame = sc.SizedFrame(None, -1, "WIT InspectableApp")

"""

class MyApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init()  # initialize the inspection tool
        # frame = MyForm()
        frame = wx.Frame(None, -1, "WIT InspectionMixin")
        pane = wx.Panel(frame, wx.ID_ANY)
        b1 = wx.Button(pane, wx.ID_ANY)

        # AHHH only when focus is in this control does CMD ALT I launching work
        t1 = wx.TextCtrl(pane, -1)

        frame.Show()
        self.SetTopWindow(frame)
        return True

# Run the program
if __name__ == "__main__":
    # app = wx.App(False)
    app = MyApp()
    app.MainLoop()




# WORKS

# import wx
# import wx.lib.sized_controls as sc
# import wx.lib.mixins.inspection as wit
#
# app = wit.InspectableApp()
#
# frame = sc.SizedFrame(None, -1, "WIT InspectableApp")
#
# pane = frame.GetContentsPane()
# pane.SetSizerType("horizontal")
#
# b1 = wx.Button(pane, wx.ID_ANY)
# t1 = wx.TextCtrl(pane, -1)
# t1.SetSizerProps(expand=True)
#
# frame.Show()
#
# app.MainLoop()


# WORKS
#
# import wx
# import wx.lib.sized_controls as sc
# import wx.lib.mixins.inspection as wit
#
# class MyApp(wx.App, wit.InspectionMixin):
#     def OnInit(self):
#         self.Init()  # initialize the inspection tool
#         return True
# app = MyApp()
#
# # frame = sc.SizedFrame(None, -1, "WIT InspectionMixin")
# # pane = frame.GetContentsPane()
# # pane.SetSizerType("horizontal")
# # b1 = wx.Button(pane, wx.ID_ANY)
# # t1 = wx.TextCtrl(pane, -1)
# # t1.SetSizerProps(expand=True)
#
# # ANDY variant
# frame = wx.Frame(None, -1, "WIT InspectionMixin")
# pane = wx.Panel(frame, wx.ID_ANY)
# b1 = wx.Button(pane, wx.ID_ANY)
# t1 = wx.TextCtrl(pane, -1)
# # t1.SetSizerProps(expand=True)
#
#
# frame.Show()
#
# app.MainLoop()




# DOESN'T WORK - EVEN THOUGH IT IS AN OFFICIAL WXPYTHON DOCO PAGE
# https://wxpython.org/Phoenix/docs/html/wx.lib.mixins.inspection.html
#
# import wx
# import wx.lib.mixins.inspection
#
#
# class MyFrame(wx.Frame):
#     pass
#
#
# class MyApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
#     def OnInit(self):
#         self.Init()  # initialize the inspection tool
#         frame = MyFrame(None, title="This is a test")
#         frame.Show()
#         self.SetTopWindow(frame)
#         return True
#
#
# app = MyApp()
# app.MainLoop()

