class Torture1:
    def PrepTests(self):
        self.a = UmlCanvas(panel, Log(), self.frame)
        self.b.append(UmlCanvas(panel, Log(), self.frame))

    # def Tricky(self):
    #    self.log = Log()
    #    from self.frame = wx.Frame    ? should pick up more?
    #    self.notebook = wx.Notebook
    #    self.umlcanvas = UmlCanvas(panel, Log(), self.frame)
    #    self.umlcanvas = UmlCanvas(self.notebook, Log(), self.frame)
    #    self.umlcanvas = UmlCanvas(self.frame, Log(), self.frame)
    #    self.multiText = wx.TextCtrl
    #    self.app = App(context)
    #    self.user_config_file = os.path.join(config_dir, PYNSOURCE_CONFIG_FILE)
    #    self.config = ConfigObj(self.user_config_file) # doco at
    #    self.popupmenu = wx.Menu()     # Create a menu
    #    self.next_menu_id = wx.NewId() ---- yike how to tell if LIBRARY call is class or function !!
    #    self.printData = wx.PrintData()
    #    self.printData = wx.PrintData()
    #    self.box = wx.BoxSizer(wx.VERTICAL)
    #    self.canvas = self.umlcanvas.GetDiagram().GetCanvas()


a = Torture1()
