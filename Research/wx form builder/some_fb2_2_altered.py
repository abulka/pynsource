import wx
from some_fb2_gen_altered import MyFrame2

app = wx.App()
frame = MyFrame2(None)
frame.m_scintilla1.SetText(open(r"..\..\pynsource\printframework.py").read())
frame.m_scintilla1.EmptyUndoBuffer()
frame.Show()
app.MainLoop()
