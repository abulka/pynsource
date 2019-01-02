import wx
from test1_gen import *


class MyFrame1A(MyFrame1):
# class MyFrame1A(MyFrame2):
    """test"""

    def __init__(self, parent):
        super(MyFrame1A, self).__init__(parent) #, title="hi", size=(350, 300))

        menuBar = MyMenuBar1()
        self.SetMenuBar(menuBar)

        # Instantiating a toolbar class doesn't work??????
        # tb = MyToolBar1(parent=self)
        # self.SetToolBar(tb)
        # tb.Show()

        # Instantiating a toolbar class doesn't work?????? - vers 2
        # # client = wx.Panel(self)  # creating a new one
        # client = self.m_panel1  # use an existing one
        # client.SetBackgroundColour(wx.RED)
        # tb = MyToolBar1(self)
        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(tb, 0, wx.EXPAND)
        # client.SetSizer(sizer)


        # Attempt manually built toolbar - works OK
        self.toolbar = self.CreateToolBar()
        self.toolbar.AddTool(1, '', wx.Bitmap('toucan.png'))
        self.toolbar.AddTool(2, '', wx.Bitmap('toucan.png'))
        self.toolbar.Realize()




        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('Ready')


        # self.SetSize((450, 350))
        # self.SetTitle('Check menu item')
        # self.Centre()


    def do_popup(self, event):
        f = MyFrame2(parent=self)  # or can use parent of None
        f.Show()

	# def OnButton1(self, event):
    #     print "button pushed"
	#
    # def OnHtml2(self, event):
    #     url = "http://www.wxpython.org/docs/api/wx.html.HtmlWindow-class.html"
    #     wx.CallAfter(frame.m_htmlWin1.LoadPage, url)
	#
    # def OnLoadHtml1(self, event):
    #     url = "http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm"
    #     wx.CallAfter(frame.m_htmlWin1.LoadPage, url)
	# frame.m_htmlWin1.LoadPage(url)


app = wx.App()
frame = MyFrame1A(None)
frame.Show()
frame.SetSize((400, 400))

app.MainLoop()

