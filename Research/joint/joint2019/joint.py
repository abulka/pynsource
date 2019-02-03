import wx
# import wx.lib.ogl as ogl
import wx.html2 as webview

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Demo", size=(1300, 1200), style=wx.DEFAULT_FRAME_STYLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # put stuff into sizer

        # canvas = ogl.ShapeCanvas(self)
        # sizer.Add(canvas, 1, wx.GROW)
        self.wv = webview.WebView.New(self)
        sizer.Add(self.wv, 1, wx.GROW)

        # canvas.SetBackgroundColour("LIGHT BLUE")  #

        # diagram = ogl.Diagram()
        # canvas.SetDiagram(diagram)
        # diagram.SetCanvas(canvas)

        # shape = ogl.CircleShape(20.0)  #
        # shape.SetX(25.0)  #
        # shape.SetY(25.0)  #
        # canvas.AddShape(shape)  #
        # diagram.ShowAll(1)  #

        # apply sizer
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Show(1)

        # test TextEntryDialog
        # dlg = wx.TextEntryDialog(
        #     self, "What is your favorite programming language?", "Eh??", "Python"
        # )
        # dlg.SetValue("Python is the best!")
        # if dlg.ShowModal() == wx.ID_OK:
        #     print(("You entered: %s\n" % dlg.GetValue()))
# 
        # dlg.Destroy()

        # self.wv.LoadURL("http://google.com")
        # self.wv.LoadURL("file://joint_uml_big1.html")
        self.wv.LoadURL("file:///Users/Andy/Devel/pynsource/Research/joint/joint2019/joint_uml_big1.html")


app = wx.PySimpleApp()
# ogl.OGLInitialize()
frame = AppFrame()
app.MainLoop()
app.Destroy()
