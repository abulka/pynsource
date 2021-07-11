import wx
from typing import List, Set, Dict, Tuple, Optional
from view.display_model import GraphNode, UmlNode, UmlModuleNode, CommentNode
from gui.node_edit_multi_purpose import node_edit_multi_purpose
from gui.settings import PRO_EDITION

unregistered = not PRO_EDITION

# not all are defined, as the rest of the ids are auto allocated, just nice not to waste id's :-)
MENU_ID_SHAPE_PROPERTIES = wx.NewIdRef()
MENU_ID_BEGIN_LINE = wx.NewIdRef()
MENU_ID_CANCEL_LINE = wx.NewIdRef()


class ShapeMenuMgr:
    """
    Builds the MenuItems used in the r.click popup and also builds the accelerator table.
    Returns: -

    Fun Facts
    ---------
    Keyboard shortcuts in wxPython are actually menu events
    (i.e. wx.EVT_MENU), probably because the shortcuts are usually also a menu item.
    Id's seems to be 'broadcast' and any handler bound to that id gets called
    wx.EVT_MENU is an object, not an id.  All menu events and presumably
    key events emit this event, and the 'id' is needed to distinguish between the events.

    Accelerator tables work using keycodes and menu/key 'event' int ids - they do not involve
    menuitem objects or any other object, only ids.  There is only one global accelerator table
    per frame.
    https://wxpython.org/Phoenix/docs/html/wx.AcceleratorEntryFlags.enumeration.html#wx-acceleratorentryflags

    Note: unlike proper toolbar menus, these shortcut keys don't work - you need to add
    onKeyChar() interceptions in umlcanvas.py
    Or we use a global accelerator table on the frame.  <-- 2019 current approach.

    Where are the accelerator tables?
        - one is on the help frame so that CMD-W works
        - we otherwise don't use them anywhere else, except here, where we dynamically build
            one and attach it to main frame, then do this process again each time focus changes
            to a shape
        - when focus changes to the canvas (no shape selected) then we build a different
            accelerator table, which only has a single shortcut see focus_canvas()
        - other umlcanvas shortcuts are done via old fashioned keychar interception.

    On Binding
    ----------
    https://wxpython.org/Phoenix/docs/html/wx.EvtHandler.html#wx.EvtHandler.Bind

    third parameter is 'source'   <--- this is not an id, but an object e.g. a frame, a menuitem
    Sometimes the event originates from a different window than self, but you still want
    to catch it in self

    fourth parameter is 'id' – Used to specify the event source by ID instead of instance.

    ** Initially this didn't make sense.  if the event source is a 'window', which means a
    canvas or control etc. a frame, a menuitem etc. then how can you alternatively
    refer to that 'window' by id?
    do windows have id's?  I thought id's were the pseudo 'events' that get broadcast
    and bound to.
    ** ANSWER: Source is not an id - its an object e.g. a frame, a menuitem

    and the window/control.Bind() construct suggests that the id is expected to come
    from that window (AHA which makes sense re the definition above of 'source')

    OBJ.Bind(event_type, handler, source)
    but why bother with source - you always specify where events come from by the OBJ
    and you can bind to any destination with the handler method.  what does it mean to
    specify both source and OBJ, as the destination is always 'handler' !
    Why not just always have OBJ as your source?
    Perhaps menuitem.Bind() wouldn't work? as the events are coming from frame?  e.g.
    accelerator key id's come from the frame.  main menu event come from the frame.
    Menuitem event would surely come from the menuitem?

    OBJ.Bind(event_type, handler, source)
    OBJ.Bind(event_type, handler, id=integer_id)
    I thus think OBJ and source are both places where events 'come from'.  Specifying
    both means you can get them from either e.g. a frame or from a menuitem, if you had
    specified a menuitem as source.
    Presumably one doesn't override the other?  In other words you can get events from
    both places, not just 'source'.?
    Perhaps menuitems don't have a Bind() method, so you have to do it this way, and source
    does indeed override.  CONFIRMED
        AttributeError: 'MenuItem' object has no attribute 'Bind'
    I wonder what 'propagation', if any, happens

    OBJ.Bind(event_type, handler, integer_id)
    only seems to work with pre-allocated ids or wx.NewIdRef() but not wx.ID_ANY which is
    -1 which is strange since the passing of wx.ID_ANY into .Append() works?
    Perhaps the adding to the menu and the binding need different thinking.
    YES
    The creation of a menuitem via .Append(wx.ID_ANY, text) will give that menu item
    an id of -1 which means how do we get to it?  Well the Bind() with the menu item as the
    third parameter which is the 'source' allows the Bind to work and "receive" from the
    menuitem even though the id is generically wx.ID_ANY -1
    But if we don't specify the 'source' then we must rely on a general broadcast of the id
    and thus we need a specific id to distinguish on.  Its kind of making sense now.

    If you want both a menu item and an accelerator then you need to use a unique id
    binding technique, not 'source' based, because you can't have accelerator tables
    broadcasting wx.ID_ANY -1 everywhere, nobody would be able to tell them apart.
    How I learned this:
    At one stage I thought I would be tricky
        if not id:
            id = wx.NewIdRef() if keycode_only else wx.ID_ANY
    then the following:
        if keycode_only:
            # Need a unique id in Bind() because id broadcast from frame
            self.frame.Bind(wx.EVT_MENU, method, id=id)
        else:
            # Can use a generic wx.ID_ANY -1 id because binding directly to menuitem thus don't need id
            to_menu = self.submenu if submenu else self.popupmenu
            item = to_menu.Append(id, text)
            self.frame.Bind(wx.EVT_MENU, method, source=item)
        if key_code:
            entry = wx.AcceleratorEntry()
            entry.Set(wx.ACCEL_NORMAL, key_code, id)
            self.accel_entries.append(entry)
    BUT the wx.ID_ANY -1 in the accelerator table didn't trigger anything!

    Perhaps 'source=menuitem' binding to menu items is the only correct way cos
        to_menu = self.submenu if submenu else self.popupmenu
        item = to_menu.Append(id, text)
     1. self.frame.Bind(wx.EVT_MENU, method, source=item)   <- WORKS
     2. self.frame.Bind(wx.EVT_MENU, method, id=id)    <- DOESN'T TRIGGER THE HANDLER
    AH BUT it WORKS when the ids are unique it does, but they must be freshly allocated
    each time the menu it built, for some reason?  Otherwise the handlers don't get called?
    Possibly the 'shape' isn't in the broadcast zone of the frame - but it is, when using
    freshly allocated ids.
    Even when using a unique, pre-allocated id, the (2.) technique doesn't work?
    Even when the menuitem in question is getting a freshly allocated id, if the surrounding
    menuitems are reusing ids, no accelerator shortcuts work and I even see that CMD Q
    of the main menu stops working - something seriously screwy here.

    Here is an example illustrating the above comment.
        if not id or id == wx.ID_ANY:
            # Accelerator tables need unique ids, whereas direct menuitem binding
            # with Bind(....source=menuitem)
            # don't care about ids and can thus use wx.ID_ANY (which is always -1)
            id = wx.NewIdRef() if key_code or keycode_only else wx.ID_ANY

        # id = wx.NewIdRef()  <--- need to uncomment this to make the (2) binding technique work
        if key_code:
            assert id != wx.ID_ANY
        if keycode_only:
            assert id != wx.ID_ANY
        print(f"id={id} used for {text}")

        if keycode_only:
            self.frame.Bind(wx.EVT_MENU, method, id=id)
        else:
            to_menu = self.submenu if submenu else self.popupmenu
            item = to_menu.Append(id, text)
            # self.frame.Bind(wx.EVT_MENU, method, source=item) # (1)
            self.frame.Bind(wx.EVT_MENU, method, id=id)  # (2) doesn't work unless all ids fresh

            # self.frame.Bind(wx.EVT_UPDATE_UI, self.TestUpdateUI, item)  # future update ?

        if key_code:
            entry = wx.AcceleratorEntry()
            entry.Set(wx.ACCEL_NORMAL, key_code, id)
            self.accel_entries.append(entry)

    Summary
    -------
    Thus when creating a menu item to_menu.Append(id, text) you can specify wx.ID_ANY -1
    as the id, but this means you MUST do a Bind() with the third parameter
    which is the 'source' set to the menuitem that was just created.
    A kind of 'hard wiring / direct broadcast' which doesn't rely on unique ids.
        item = to_menu.Append(wx.ID_ANY, text)
        self.frame.Bind(wx.EVT_MENU, method, source=item)

    When creating a menu item with unique ids
    (pre-allocated ids or wx.NewIdRef() but not wx.ID_ANY) you have the option in the Bind
    to not specify the 'source' and just to specify the id.
    Warning, the third parameter is 'source', if you want to specify id, that's the
    fourth parameter, so you are typically going to need to use a keyword arg id= approach.
        id = wx.NewIdRef()               <-- this could be a pre-allocated constant
        item = to_menu.Append(id, text)              <--- id specified
        self.frame.Bind(wx.EVT_MENU, method, id=id)  <--- same id specified

    """

    def __init__(self, frame, shapehandler):
        self.frame = frame
        self.shapehandler = shapehandler  # UmlShapeHandler

        self.popupmenu = wx.Menu()  # This is the popup menu to which we attach menu items
        self.submenu = wx.Menu()  # This is the sub menu within the popupmenu
        self.accel_entries: List[wx.AcceleratorEntry] = []

    def BuildPopupMenuItems(self):
        self.popupmenu = wx.Menu()  # This is the popup menu to which we attach menu items
        self.submenu = wx.Menu()  # This is the sub menu within the popupmenu
        self.accel_entries: List[wx.AcceleratorEntry] = []

        def add_menuitem(text, method, id=None, submenu=False, key_code=None, keycode_only=False, image=None):
            def check_id(id):
                """
                Accelerator tables need unique ids, whereas direct menuitem binding with Bind(...source=menuitem)
                doesn't care about ids and can thus use wx.ID_ANY (which is always -1)
                """
                if not id or id == wx.ID_ANY:
                    id = wx.NewIdRef() if key_code or keycode_only else wx.ID_ANY
                return id

            item: wx.MenuItem = None
            id = check_id(id)

            if keycode_only:
                self.frame.Bind(wx.EVT_MENU, method, id=id)
            else:
                to_menu = self.submenu if submenu else self.popupmenu
                item = to_menu.Append(id, text)
                self.frame.Bind(wx.EVT_MENU, method, source=item)

            if key_code:
                entry = wx.AcceleratorEntry()
                entry.Set(wx.ACCEL_NORMAL, key_code, id)
                self.accel_entries.append(entry)

            if image:
                item.SetBitmap(image)

            return item

        # Utility functions to add specific things to the menu - nicer way for algorithm to refer to

        def add_submenu_to_popup():
            # self.popupmenu.Append(wx.ID_ANY, "Draw Line", self.submenu)
            self.popupmenu.AppendSubMenu(self.submenu, "Draw Line", "Line drawing operations")

        def add_separator():
            self.popupmenu.AppendSeparator()

        def add_submenu_separator():
            self.submenu.AppendSeparator()

        def add_properties():
            add_menuitem(
                "Properties...\ts",
                self.OnNodeProperties,
                id=MENU_ID_SHAPE_PROPERTIES,
                key_code=ord("S"),
            )

        def add_pro_advert():
            from media import images

            msg = "Edition lets you drag drop to connect!  Learn More..."
            if "wxGTK" in wx.PlatformInfo or "wxMSW" in wx.PlatformInfo:  # ubuntu gtk all menus and windows popup menus have images disallowed, so add text
                msg = '(Pro) ' + msg
            item: wx.MenuItem = add_menuitem(
                msg,
                self.OnProDragDrop,
                submenu=True,
                image=images.pro.GetBitmap()
            )

        def add_from(keycode_only=False):
            item: wx.MenuItem = add_menuitem(
                "Begin - Remember selected class as FROM node (for drawing lines)\tq",
                self.OnDrawBegin,
                id=MENU_ID_BEGIN_LINE,
                submenu=True,
                key_code=ord("Q"),
                keycode_only=keycode_only,
            )
            # item.Enable(False)  # hmm, accelerator still fires :-(

        def add_from_cancel(keycode_only=False):
            add_menuitem(
                "Cancel Line Begin\tx",
                self.OnCancelDrawBegin,
                id=MENU_ID_CANCEL_LINE,
                submenu=True,
                key_code=ord("X"),
                keycode_only=keycode_only,
            )

        def add_association_edge():
            add_menuitem(
                "End - Draw Line TO selected comment/class (association - dashed)\ta",
                self.OnDrawEnd3,
                key_code=ord("A"),
                submenu=True,
            )

        def add_generalise_composition_edges():
            add_menuitem(
                "End - Draw Line TO selected class (composition)\tw",
                self.OnDrawEnd1,
                submenu=True,
                key_code=ord("W"),
            )
            add_menuitem(
                "End - Draw Line TO selected class (generalisation)\te",
                self.OnDrawEnd2,
                submenu=True,
                key_code=ord("E"),
            )

        def add_reset_image_size():
            add_menuitem("Reset Image Size", self.OnResetImageSize)

        def add_delete():
            add_menuitem("Delete\tDel", self.OnRightClickDeleteNode)

        def add_cancel():
            add_menuitem("Cancel", self.OnPopupMenuCancel)

        def add_line_deletions():
            """Add delete line entries to the submenu which allows the deletion of lines"""
            displaymodel = self.shapehandler.umlcanvas.displaymodel
            edges = displaymodel.graph.find_edges_for(shape.node)
            for edge in edges:
                # The lambda returns a function to call which locks in an extra param, the edge
                add_menuitem(
                    f"Delete Line "
                    f"\"{edge['source'].id}\" "
                    f"{displaymodel.edgetype_symbol(edge['uml_edge_type'])} "
                    f"\"{edge['target'].id}\" "
                    f"({edge['uml_edge_type']})",
                    lambda evt, extra_info=edge: self.OnDeleteLine(evt, extra_info),
                    submenu=True,
                )

        # Line popup menu item helpers

        def add_edge_types():
            add_menuitem("Generalisation --|>\tE", self.OnLineConvertToGeneralisation, key_code=ord("E"))
            add_menuitem("Composition    <>--\tW", self.OnLineConvertToComposition, key_code=ord("W"))
            add_menuitem("Association    ----\tA", self.OnLineConvertToAssociation, key_code=ord("A"))
            add_separator()
            add_menuitem("Reverse Link\tR", self.OnLineConvertToReverse, key_code=ord("R"))
            add_separator()
            add_menuitem("Delete\tDel", self.OnRightClickDeleteNode)
            add_separator()


        # Main Logic - First look around...

        shape = self.shapehandler.GetShape()
        if "Line" in shape.__class__.__name__:  # no popup menu for lines
            add_edge_types()
            add_cancel()
        else:
            if not hasattr(shape, "node"):
                return
            from_node: GraphNode = self.shapehandler.umlcanvas.new_edge_from
            is_bitmap = shape.__class__.__name__ == "BitmapShapeResizable"
            if is_bitmap:
                is_comment = is_umlclass = False
            else:
                is_comment = isinstance(shape.node, CommentNode)
                is_umlclass = isinstance(shape.node, UmlNode) or isinstance(shape.node, UmlModuleNode)
            assert not is_umlclass == (is_comment or is_bitmap)
            started_connecting = from_node != None
            from_is_comment = isinstance(from_node, CommentNode)

            # The algorithm that builds the menu

            if unregistered:
                add_pro_advert()
                add_submenu_separator()

            if is_umlclass or is_comment:
                add_properties()
                add_separator()
                if not from_node:
                    add_from()
                else:
                    add_from(keycode_only=True)  # always allow begin line draw as shortcut

            if is_umlclass:
                if started_connecting:
                    add_association_edge()
                    if not from_is_comment:
                        add_generalise_composition_edges()
                else:
                    pass  # don't offer 'to' menu choices cos haven't started connecting yet
            elif is_comment:
                if started_connecting:
                    add_association_edge()
                else:
                    pass  # don't offer 'to' menu choices cos haven't started connecting yet
            elif is_bitmap:
                add_reset_image_size()
            else:
                raise RuntimeError("Right click on unknown shape")

            if is_umlclass or is_comment:
                if from_node:
                    add_from_cancel()
                else:
                    add_from_cancel(keycode_only=True)  # always allow begin line cancel as shortcut

            if not is_bitmap:
                add_submenu_to_popup()

            add_separator()
            add_delete()
            add_separator()
            add_cancel()

            if is_umlclass or is_comment:
                add_submenu_separator()
                add_line_deletions()

        accel_tbl = wx.AcceleratorTable(self.accel_entries)
        self.frame.SetAcceleratorTable(accel_tbl)

    def OnDeleteLine(self, event, extra_info):
        edge: Dict = extra_info
        self.shapehandler.umlcanvas.displaymodel.graph.delete_edge(edge)
        edge["shape"].Delete()
        self.shapehandler.umlcanvas.mega_refresh()

    # Handy Redirections

    def GetShape(self):
        return self.shapehandler.GetShape()

    def focus_shape(self):
        self.shapehandler.focus_shape()

    # Handlers

    def OnNodeProperties(self, event):
        node_edit_multi_purpose(self.GetShape(), self.shapehandler.umlcanvas.app)

    def OnDrawBegin(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkFrom()
        self.focus_shape()  # rebuild the accelerator table and menus cos situation changed

    def OnCancelDrawBegin(self, event):
        self.GetShape().GetCanvas().OnCancelLine(event)  # delegate to canvas handler - event dodgy
        self.focus_shape()  # rebuild the accelerator table and menus cos situation changed

    def OnDrawEnd1(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type="composition")
        self.focus_shape()

    def OnDrawEnd2(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type="generalisation")
        self.focus_shape()

    def OnDrawEnd3(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type="association")
        self.focus_shape()

    def OnResetImageSize(self, event):
        shape = self.GetShape()
        shape.ResetSize()
        # shape.GetCanvas().Refresh(False)   # don't seem to need since SelectNodeNow() might be doing it for us
        shape.GetCanvas().SelectNodeNow(shape)
        self.shapehandler.UpdateStatusBar(shape)

    def OnRightClickDeleteNode(self, event):
        self.shapehandler.umlcanvas.app.run.CmdNodeDelete(self.GetShape())

    def OnProDragDrop(self, event):
        # self.shapehandler.umlcanvas.app.context.wxapp.MessageBox("asd")  # quick popup

        from common.messages import PRO_DRAG_DROP_CONNECT_HELP, PRO_INFO_URL
        import webbrowser
        retCode = wx.MessageBox(PRO_DRAG_DROP_CONNECT_HELP.strip(), "Pro Edition Information", wx.YES_NO | wx.ICON_QUESTION)
        if retCode == wx.YES:
            webbrowser.open(PRO_INFO_URL)

    def OnPopupMenuCancel(self, event):
        pass

    # Line handlers

    def OnLineConvertToGeneralisation(self, event):
        self.shapehandler.umlcanvas.app.run.CmdLineChangeToEdgeType(self.GetShape(), "generalisation")
    def OnLineConvertToComposition(self, event):
        self.shapehandler.umlcanvas.app.run.CmdLineChangeToEdgeType(self.GetShape(), "composition")
    def OnLineConvertToAssociation(self, event):
        self.shapehandler.umlcanvas.app.run.CmdLineChangeToEdgeType(self.GetShape(), "association")
    def OnLineConvertToReverse(self, event):
        self.shapehandler.umlcanvas.app.run.CmdLineChangeToReverse(self.GetShape())
