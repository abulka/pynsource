import wx
from dialogs.FramePyYuml import *
from common.messages import *

class PyYumlGuiFrame ( MyFrame1 ):
    def OnButton1( self, event ):
        pass
    
    def AndyBoot(self):
       self.SetStatusText("Import python code and have it rendered by yUml web service")
       self.yuml = self.m_customControl1

    def OnOpen( self, event ):
        self.yuml.FileLoad(event)
        #FILE = """F:\Documents\\AndyTabletXp2\\Documents and Settings\\Andy\\My Documents\\Software Development\\aa python\\pyNsource\\outyuml.png"""
        #self.yuml.ViewImage(FILE)
    
    def OnSaveAs( self, event ):
        self.yuml.SaveImage(self.yuml.bmp, format="png")
    
    def OnExit( self, event ):
        self.Close(True)
    
    def OnAbout( self, event ):
        #wx.MessageBox("(c) Andy Bulka, 2012")
        
        from wx.lib.wordwrap import wordwrap
        info = wx.AboutDialogInfo()
        #info.SetIcon(wx.Icon('Images\\img_uml01.png', wx.BITMAP_TYPE_PNG))
        info.SetName(PY_YUML_ABOUT_APPNAME)
        info.SetVersion(str(PY_YUML_APP_VERSION))
        #info.SetDescription(ABOUT_MSG)
        info.Description = wordwrap(PY_YUML_ABOUT_MSG, 350, wx.ClientDC(self))
        info.SetCopyright(ABOUT_AUTHOR)
        #info.SetWebSite(WEB_PYNSOURCE_HOME_URL)
        info.WebSite = (WEB_PYNSOURCE_HOME_URL, "Home Page")
        info.WebSite = (PY_YUML_HOME_URL, "Yuml Home Page")
        info.SetLicence(ABOUT_LICENSE)
        #info.AddDeveloper(ABOUT_AUTHOR)
        #info.AddDocWriter(ABOUT_FEATURES)
        #info.AddArtist('Blah')
        #info.AddTranslator('Blah')

        wx.AboutBox(info)
        
    def OnImport( self, event ):
        from generate_code.gen_yuml import PySourceAsYuml
        import urllib
        
        dlg = wx.FileDialog(parent=self, message="choose", defaultDir='.',
            defaultFile="", wildcard="*.py", style=wx.OPEN|wx.MULTIPLE, pos=wx.DefaultPosition)
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
            print 'Importing...'
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
            print filenames
            
            files=filenames
            p = PySourceAsYuml()
            p.optionModuleAsClass = 0
            p.verbose = 0
            if files:
                for f in files:
                    p.Parse(f)
            p.CalcYumls()
            print p

            #yuml_txt = "[Customer]+1->*[Order],[Order]++1-items >*[LineItem],[Order]-0..1>[PaymentMethod]"
            yuml_txt = ','.join(str(p).split())
            baseUrl = 'http://yuml.me/diagram/dir:lr;scruffy/class/'
            url = baseUrl + urllib.quote(yuml_txt)
            self.yuml.ViewImage(url=url)

            wx.EndBusyCursor()
            print 'Import - Done.'
            
            
APP_SIZE = (600,600)
BOOTSTRAP_TECHNIQUE = "B"  # "B"

if BOOTSTRAP_TECHNIQUE == "A":
    app = wx.App()                       # 1. create app
    frame = PyYumlGuiFrame(None)         # 2. create and show frame
    frame.Show()
    frame.Centre()
    frame.SetSize(APP_SIZE)
    frame.AndyBoot()
    app.MainLoop()                       # 3. app.MainLoop()
else:
    class App(wx.App):
        def OnInit(self):
            frame = PyYumlGuiFrame(None) # 2. create and show frame
            frame.Show(True)
            frame.Centre()
            frame.SetSize(APP_SIZE)
            frame.AndyBoot()
            return True
    app = App(0)                         # 1. create app
    app.MainLoop()                       # 3. app.MainLoop()
