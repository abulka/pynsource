import wx
from some_fb2_gen import MyFrame2

app = wx.App()
frame = MyFrame2(None)
frame.m_customControl1.SetText(open(r"..\..\pynsource\printframework.py").read())
frame.m_customControl1.EmptyUndoBuffer()
frame.Show()
app.MainLoop()
