import wx
from someStyledTextCtrl2 import runTest

# Good demo http://zamestnanci.fai.utb.cz/~bliznak/screencast/wxfbtut1/wxFBTut1.html


from some_fb2_gen import *
	
class MyFrame3A ( MyFrame3 ):
	def OnButton1( self, event ):
		print("button pushed")
	
	def OnHi( self, event ):
		print("hi")

	def OnSay( self, event ):
		print("say")

app = wx.App()

# DEMO 3
#frame = MyFrame3A(None)

# DEMO 2
frame = MyFrame2(None)
p = runTest(frame, frame, None)
frame.m_scintilla1 = p
#frame.m_scintilla1.SetText(demoText + open(r'..\..\pynsource\printframework.py').read())


frame.Show()
app.MainLoop()