"""
From http://wiki.wxpython.org/PopupMenuOnRightClick

Note that there are better ways to do this, like binding to
the exact method that you want e.g.

self.frame.Bind(wx.EVT_MENU, method, item)

see my
  uml_shape_handler.py
  pyNsourceGui.py
  
for examples.

"""

from wxPython.wx import *



menu_titles = [ "Open",
                "Properties",
                "Rename",
                "Delete" ]

menu_title_by_id = {}
for title in menu_titles:
    menu_title_by_id[ wxNewId() ] = title



list_title = "files"
list_items = [ "binding.py",
               "clipboard.py",
               "config.py",
               "debug.py",
               "dialog.py",
               "dispatch.py",
               "error.py", ]



class App( wxPySimpleApp ):
    def OnInit( self ):
        # build frame
        frame = wxFrame(NULL, -1, "Hello from wxPython")
        self.frame = frame # we'll use in RightClickCb

        # build list
        list  = wxListCtrl( frame, -1, style=wxLC_REPORT )
        list.InsertColumn( 0, list_title )
        for x in list_items: list.InsertStringItem(0,x)

        ### 1. Register source's EVT_s to invoke launcher. ###
        EVT_LIST_ITEM_RIGHT_CLICK( list, -1, self.RightClickCb )

        # clear variables
        self.list_item_clicked = None

        # show &amp; run
        frame.Show(1)
        return 1

    def RightClickCb( self, event ):
        # record what was clicked
        self.list_item_clicked = right_click_context = event.GetText()

        ### 2. Launcher creates wxMenu. ###
        menu = wxMenu()
        for (id,title) in list(menu_title_by_id.items()):
            ### 3. Launcher packs menu with Append. ###
            menu.Append( id, title )
            ### 4. Launcher registers menu handlers with EVT_MENU, on the menu. ###
            EVT_MENU( menu, id, self.MenuSelectionCb )

        ### 5. Launcher displays menu with call to PopupMenu, invoked on the source component, passing event's GetPoint. ###
        self.frame.PopupMenu( menu, event.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak

    def MenuSelectionCb( self, event ):
        # do something
        operation = menu_title_by_id[ event.GetId() ]
        target    = self.list_item_clicked
        print('Perform "%(operation)s" on "%(target)s."' % vars())

app = App()
app.MainLoop()