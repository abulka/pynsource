import wx
from fbogl1_gen import MyFrame2
import wx.lib.ogl as ogl

app = wx.App()
ogl.OGLInitialize()
frame = MyFrame2(None)
frame.Show()
frame.SetSize((400, 400))

frame.canvas.SetBackgroundColour("LIGHT BLUE")
# Optional - add a shape
shape = ogl.RectangleShape(60, 60)
shape.SetX(50)
shape.SetY(50)
frame.canvas.AddShape(shape)
frame.canvas.GetDiagram().ShowAll(True)

app.MainLoop()
