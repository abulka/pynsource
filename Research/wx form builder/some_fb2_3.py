import wx

# Good demo http://zamestnanci.fai.utb.cz/~bliznak/screencast/wxfbtut1/wxFBTut1.html


from some_fb2_gen import *
	
class MyFrame3A ( MyFrame3 ):
	def OnButton1( self, event ):
		print "button pushed"
	
	def OnHi( self, event ):
		print "hi"

	def OnSay( self, event ):
		print "say"

app = wx.App()

# DEMO 3
frame = MyFrame3A(None)

frame.Show()
app.MainLoop()