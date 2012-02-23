# Andy's demo code showing wxpython and bottle running together at the same time.

import wx
from bottle import route, run
import thread

HOST='localhost'
PORT="8081"
LOCALURL = u"http://"+HOST+":"+PORT

class MyForm(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self,parent,id=3)
        self.inputFieldTxt = wx.TextCtrl(self, -1, size=(200,-1), pos=(5, 10), style=wx.TE_PROCESS_ENTER)
        wx.StaticText(self, -1, "enter text and hit ENTER", size=(170,-1), pos=(5, 35))
        wx.HyperlinkCtrl(self, wx.ID_ANY, u"view", LOCALURL, pos=(5, 60) )

class AppFrame(wx.Frame):
    myForm = None
    currentData = ""

    def __init__(self):
        wx.Frame.__init__(self,parent=None, id=-1, title="Wx plus Bottle by Andy",size=(300,150))
        self.myForm = MyForm(self)

        self.myForm.Bind(wx.EVT_TEXT_ENTER, self.onGuiHitEnter, self.myForm.inputFieldTxt)

    def onGuiHitEnter(self, evt):
        self.currentData = self.myForm.inputFieldTxt.GetValue().upper()
        print "wx gui got", self.currentData
        
    def StartServer(self):
        thread.start_new_thread(self._Serve, ())
        
    def _Serve(self):
        print "starting server thread..."
        
        @route('/')
        def index():
            return '<b>app data is</b> %s' % self.currentData

        run(host=HOST, port=PORT)
        # nothing runs after this point


class WxApp(wx.App):
    appFrame = None

    def OnInit(self):
        self.appFrame = AppFrame()
        self.appFrame.Show()
        return True

if __name__ == '__main__':
    wxApp = WxApp(redirect=False)
    wx.CallAfter(wxApp.appFrame.StartServer)    
    wxApp.MainLoop()
    