import wx
# from typing import List, Set, Dict, Tuple, Optional

MENU_ID_SHAPE_PROPERTIES = wx.NewIdRef()
MENU_ID_BEGIN_LINE = wx.NewIdRef()
MENU_ID_CANCEL_LINE = wx.NewIdRef()

# # Central place to check whether menu is enabled.  Can be checked by handlers
# popup_menu_central : Dict[int, bool] = {
#     MENU_ID_SHAPE_PROPERTIES: True,
#     MENU_ID_BEGIN_LINE: True,
# }
#
# def is_item_enabled(id):
#     print(f"checking is item {id} is enabled")
#     return popup_menu_central[id]
#
# def set_item_state(id, state):
#     popup_menu_central[id] = state
#
# def accelerate(frame):
#     """ accelerator stuff
#     this is what is called when
#     """
#     accel_tbl = wx.AcceleratorTable([
#         (wx.ACCEL_CTRL, ord('Z'), MENU_ID_SHAPE_PROPERTIES),
#         (wx.ACCEL_NORMAL, ord('Q'), MENU_ID_BEGIN_LINE),
#     ])
#     frame.SetAcceleratorTable(accel_tbl)
#
#
#     frame.Bind(wx.EVT_MENU, OnNodeProperties, id=MENU_ID_SHAPE_PROPERTIES)
#     frame.Bind(wx.EVT_MENU, OnDrawBegin, id=MENU_ID_BEGIN_LINE)
#
# def focus_canvas(frame, canvas):
#     """ accelerator stuff
#     this is what is called when shape is deselected
#     the only acceleration should be to cancel the pending line drawing
#
#     """
#     accel_tbl = wx.AcceleratorTable([
#         (wx.ACCEL_NORMAL, ord('X'), MENU_ID_CANCEL_LINE),
#     ])
#     frame.SetAcceleratorTable(accel_tbl)
#
#     frame.Bind(wx.EVT_MENU, OnCancelLine, id=MENU_ID_SHAPE_PROPERTIES)
#     frame.Bind(wx.EVT_MENU, OnDrawBegin, id=MENU_ID_BEGIN_LINE)
#
# def OnNodeProperties(event):
#     print("global OnNodeProperties")
#
# def OnDrawBegin(event):
#     print("global OnDrawBegin")



# class PopupMenuItems:
#     """
#     Builds the MenuItems used in the r.click popup and stores them
#     which allows them to be accessed later, to check if they are enabled or not
#     by the handler.
#
#     The handler unfortunately, has to check if its associated menuitem is enabled
#     since the accelerator key for a menu item will trigger regardless.
#     """
#
#     def __init__(self, frame):
#         self.frame = frame
#         self.menu_items : List[wx.MenuItem] = []
#         self.sub_menu_items : List[wx.MenuItem] = []  # currently support one submenu for popup
#         self.accel_entries : List[wx.AcceleratorEntry] = []
#
#     def create(self, text, method, update_method=None, is_sub_menu=False, key_code=None, help=""):
#         """
#         Creates a menu item but does not add it to any menu - this will be done later
#
#         Re update_method - whenever a menu is about to be presented to the user, 'update_method'
#         is called, per item/binding. In the handler you can
#
#             - if the update handler is specific to each item, then you already know which item it caters to
#             - if the update handler is used by more than one menu item, check event.GetId()
#             - event.SetText(text) sets the text of the menuitem
#             - event.Enable(False) enables or disabled the menuitem
#
#         returns: menu item
#         """
#
#         item = wx.MenuItem(parentMenu=None,  # None cos item is going to be added to the menu later
#                            id=wx.ID_ANY,
#                            text=text,
#                            subMenu=None,
#                            helpString=help)
#
#         self.frame.Bind(wx.EVT_MENU, method, item)
#
#         if update_method:
#             self.frame.Bind(wx.EVT_UPDATE_UI, update_method, item)
#
#         if key_code:
#             # https://wxpython.org/Phoenix/docs/html/wx.AcceleratorEntryFlags.enumeration.html#wx-acceleratorentryflags
#             entry = wx.AcceleratorEntry()
#             entry.Set(wx.ACCEL_NORMAL, key_code, item.GetId())
#             self.accel_entries.append(entry)
#
#         if is_sub_menu:
#             self.sub_menu_items.append(item)
#         else:
#             self.menu_items.append(item)
#
#         return item
#
#     def finish(self):
#         accel_tbl = wx.AcceleratorTable(self.accel_entries)
#         # self.frame.SetAcceleratorTable(accel_tbl)
#
#     def find_by_text(self, text):
#         for item in self.menu_items + self.sub_menu_items:
#             if item.GetItemLabel() == text:
#                 return item
#         raise RuntimeError(f"Unknown menuitem with text '{text}' when searching through popup menuitems.")
#
#     def IsEnabled(self, id):
#         for item in self.menu_items + self.sub_menu_items:
#             if item.GetId() == id:
#                 return item.Enabled
#         raise RuntimeError(f"Unknown menuitem id {id} when searching through popup menuitems.")
#
#
# class ShapePopupMenuMgr(PopupMenuItems):
#
#     TXT_PROPERTIES = "Properties..."
#     TXT_BEGIN_LINE = "Begin Line\tZ"
#
#     def __init__(self, frame, uml_shape_handler):
#         super().__init__(frame)
#         self.popupmenu = wx.Menu()  # This is the popup menu to which we attach menu items
#         self.submenu = wx.Menu()  # This is the sub menu within the popupmenu
#         self.create_menu_items(uml_shape_handler)
#         self.finish()
#
#     def create_menu_items(self, uml_shape_handler):
#         """
#         Creates all menu items but does not assign them to menus.
#         All menu items trigger methods on the 'uml_shape_handler' object
#         """
#         self.create(
#             text=self.TXT_PROPERTIES,
#             method=uml_shape_handler.OnNodeProperties,
#             update_method=None,
#             is_sub_menu=False,
#             key_code=None,
#             help=""
#             )
#         self.create(
#             text=self.TXT_BEGIN_LINE,
#             method=uml_shape_handler.OnDrawBegin,
#             update_method=None,
#             is_sub_menu=True,
#             key_code=ord('Z'),
#             help=""
#             )
#
#
#     def clear(self):
#         self.popupmenu = wx.Menu()
#         self.submenu = wx.Menu()
#
#     # def finish(self):
#     #     super().finish()
#     #     # self.popupmenu.Append(wx.ID_ANY, "Subbbb", self.submenu, help="hacky line drawing stuff...")
#
#     # Add methods - call 'clear' then go for it to compose a menu
#
#     def add_separator(self):
#         self.popupmenu.AppendSeparator()
#
#     def add_properties(self):
#         self.popupmenu.Append(self.find_by_text(self.TXT_PROPERTIES))
#
#     def add_from(self):
#         self.submenu.Append(self.find_by_text(self.TXT_BEGIN_LINE))
