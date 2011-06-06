import wx
from hexmvcgui_gen import HexMvcGuiFrame1
import thread, time

class MyFrame(HexMvcGuiFrame1):
    def __init__( self, parent ):
        HexMvcGuiFrame1.__init__( self, parent )
        self.need_abort = False
        
    def SetApp(self, app):
        self.app = app
        print "app has been set"

    def DumpModel( self, event ):
        self._DumpModel()

    def DumpClear( self, event ):
        self.m_textCtrl1.Clear()

    def AddJunkText( self, event ):
        self._AddJunkText()
        
    def MiscMessageBox( self, event ):
        wx.MessageBox("hi there")

    def FileLoad( self, event ):        
        self.app.Load()
        self._DumpModel()

    def FileNew( self, event ):        
        self.app.New()
        self._DumpModel()
        
    def _AddJunkText(self):
        self.m_textCtrl1.AppendText("asdasdasd ")

    def _IncrGuage(self):
        self.m_gauge1.Value += 1

    def _DumpModel(self):
        self.m_textCtrl1.AppendText(str(self.app.model))
        for thing in self.app.model.things:
            self.m_listBox1.Append(str(thing), thing)

    def BackgroundTask1( self, event ):
        self.need_abort = False
        self.m_gauge1.Range = 5
        self.m_gauge1.Value = 0
        thread.start_new_thread(self._DoSomeLongTask, ())

    def StopBackgroundTask1( self, event ):
        self.need_abort = True

    def _DoSomeLongTask(self):
        print "Background Task started"
        for i in range(0,5):
            if self.need_abort:
                print "aborted."
                return
            wx.CallAfter(self._AddJunkText)
            wx.CallAfter(self._IncrGuage)
            print '*',
            time.sleep(1)   # lets events through to the main wx thread and paints/messages get through ok
        print "Done Background Task."
        self.m_gauge1.Value = 0

    def StartServer( self, event ):
        self.app.StartServer()


class MyWxApp(wx.App):
    def OnInit(self):
        frame = MyFrame(parent=None)
        frame.Show()
        self.myframe = frame
        return True
    