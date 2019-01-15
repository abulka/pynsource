# Event handler

import wx
import wx.lib.ogl as ogl
from .coord_utils import setpos, getpos
from common.architecture_support import *
from gui.uml_shapes import CommentShape
from view.display_model import GraphNode, UmlNode, CommentNode
from typing import List, Set, Dict, Tuple, Optional
from gui.shape_menuitems import *


class UmlShapeHandler(ogl.ShapeEvtHandler):
    def __init__(self, log, frame, shapecanvas):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.frame = frame  # these are arbitrary initialisations
        self.umlcanvas = shapecanvas  # these are arbitrary initialisations
        self.app = (
            None
        )  # assigned later by event sent to controller from uml canvas when creating new shapes

        self.popupmenu = None

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        x, y = getpos(shape)
        width, height = shape.GetBoundingBoxMax()

        msg = ""
        node = getattr(shape, "node", None)
        if node:
            colour_index = getattr(node, "colour_index", None)
            if colour_index != None:
                msg += "colour_index %d" % colour_index

        self.frame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d) %s" % (x, y, width, height, msg))

    def OnLeftClick(self, x, y, keys=0, attachment=0):
        self._SelectNodeNow(x, y, keys, attachment)

    def _SelectNodeNow(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        shape.GetCanvas().SelectNodeNow(shape)
        self.UpdateStatusBar(shape)
        self.focus_shape(shape)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        oldpos = getpos(shape)
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)  # super
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        newpos = getpos(shape)
        try:
            # print shape.node.id, "moved from", oldpos, "to", newpos
            # Adjust the GraphNode to match the shape x,y
            shape.node.left, shape.node.top = newpos
        except:
            print("no node model attached to this shape!")

        self.UpdateStatusBar(shape)

        shape.GetCanvas().canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=True)

        # Invoke overlap removal (unless hold down shift key)
        KEY_SHIFT = 1
        if keys & KEY_SHIFT:
            # shape.GetCanvas().mega_refresh()   # do we need this?  did quite well without it before
            pass
        else:
            canvas = shape.GetCanvas()
            if canvas.remove_overlaps():
                pass

        canvas.mega_refresh()

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        shape = self.GetShape()

        # super
        ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)

        width, height = shape.GetBoundingBoxMin()
        if hasattr(shape, "node"):
            # print shape.node, "resized to", width, height
            # print shape.node.id, shape.node.left, shape.node.top, "resized to", width, height

            # Adjust the GraphNode to match the shape x,y
            shape.node.width, shape.node.height = width, height
            shape.node.left, shape.node.top = getpos(shape)

        self.UpdateStatusBar(self.GetShape())

        shape.GetCanvas().canvas_resizer.resize_virtual_canvas_tofit_bounds(bounds_dirty=True)

        canvas = shape.GetCanvas()
        if canvas.remove_overlaps():
            pass

        canvas.mega_refresh()

    def OnEndSize(self, width, height):
        # print "OnEndSize", width, height
        pass

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)

        self.UpdateStatusBar(shape)

        if (
            "wxMac" in wx.PlatformInfo
        ):  # Definitely seem to need this on Mac to avoid ghost lines being left after a move
            shape.GetCanvas().Refresh(False)

    def BuildPopupMenuItems(self):
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

        self.popupmenu = wx.Menu()  # This is the popup menu to which we attach menu items
        self.submenu = wx.Menu()  # This is the sub menu within the popupmenu

        self.accel_entries : List[wx.AcceleratorEntry] = []

        def add_menuitem(text, method, id=None, submenu=False, key_code=None, keycode_only=False):

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
                # self.frame.Bind(wx.EVT_UPDATE_UI, self.TestUpdateUI, item)  # future update ?

            if key_code:
                entry = wx.AcceleratorEntry()
                entry.Set(wx.ACCEL_NORMAL, key_code, id)
                self.accel_entries.append(entry)
                # print("accel built", entry, key_code, id)

            return item

        def add_submenu_to_popup():
            self.popupmenu.Append(wx.ID_ANY, "Draw Line", self.submenu)

        def add_separator():
            self.popupmenu.AppendSeparator()

        def add_properties():
            add_menuitem("Properties...\ts",
                         self.OnNodeProperties,
                         id=MENU_ID_SHAPE_PROPERTIES,
                         key_code=ord('S'),
                         )

        def add_from(keycode_only=False):
            item : wx.MenuItem = add_menuitem(
                "Begin - Remember selected class as FROM node (for drawing lines)\tq",
                self.OnDrawBegin,
                id=MENU_ID_BEGIN_LINE,
                submenu=True,
                key_code=ord('Q'),
                keycode_only=keycode_only
            )
            # item.Enable(False)  # hmm, accelerator still fires :-(

        def add_from_cancel(keycode_only=False):
            add_menuitem(
                "Cancel Line Begin\tx",
                self.OnCancelDrawBegin,
                id=MENU_ID_CANCEL_LINE,
                submenu=True,
                key_code = ord('X'),
                keycode_only = keycode_only
            )

        def add_association_edge():
            add_menuitem(
                "End - Draw Line TO selected comment/class (association - dashed)\ta",
                self.OnDrawEnd3,
                submenu = True
            )

        def add_generalise_composition_edges():
            add_menuitem(
                "End - Draw Line TO selected class (composition)\tw",
                self.OnDrawEnd1,
                submenu=True
            )
            add_menuitem(
                "End - Draw Line TO selected class (generalisation)\te",
                self.OnDrawEnd2,
                submenu = True
            )

        def add_reset_image_size():
            add_menuitem("Reset Image Size", self.OnResetImageSize)

        def add_delete():
            add_menuitem("Delete\tDel", self.OnRightClickDeleteNode)

        def add_cancel():
            add_menuitem("Cancel", self.OnPopupMenuCancel)

        shape = self.GetShape()
        from_node : GraphNode = self.umlcanvas.new_edge_from
        is_bitmap = shape.__class__.__name__ == "BitmapShapeResizable"
        is_comment = isinstance(shape.node, CommentNode)
        is_umlclass = isinstance(shape.node, UmlNode)
        assert not is_umlclass == (is_comment or is_bitmap)
        started_connecting = from_node != None
        from_is_comment = isinstance(from_node, CommentNode)

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

        add_submenu_to_popup()

        add_separator()
        add_delete()
        add_separator()
        add_cancel()

        accel_tbl = wx.AcceleratorTable(self.accel_entries)
        self.frame.SetAcceleratorTable(accel_tbl)

        # wx.GetApp().Bind(wx.EVT_UPDATE_UI, self.TestUpdateUI, id=506)
        # self.frame.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        #
        # def doBind(item, handler, updateUI=None):
        #     self.Bind(wx.EVT_TOOL, handler, item)
        #     if updateUI is not None:
        #         self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        #
        # doBind(tbar.AddTool(-1, images._rt_bold.GetBitmap(), isToggle=True, shortHelpString="Bold"),
        #        self.OnBold,
        #        self.OnUpdateBold)

    def focus_shape(self, shape):
        """
        Called by both left and right click on a shape

        This is where we need to refresh the values in the central table

        This is where we need to bind accelerators to shape events just in case it was a
        left click and accelerator key pressed, thus no popup menu ever occurs.
        FUN FACT: Keyboard shortcuts in wxPython are actually menu events (i.e. wx.EVT_MENU), probably because the shortcuts are usually also a menu item.

        If it is a right click then we bind from the menu items again?  But how does that
        interact with the (non menu popup) first bindings?  Does the fact that menu items
        share ids nicely affect things?  Need to experiment a bit.

        what about unbinding when no shape is selected?  or when shape is deleted?
        well, we just cross our fingers the wxpython event handling does the right thing.

        """
        # Need to build accelerator table with only the entries that are relevant
        # and bind to the shape's handlers
        print("focus_shape")
        self.BuildPopupMenuItems()  # easy way, we simply don't popup the menu
        # accelerator table gets put in place - bonus
        # and the menu is ready to be displayed if we right click - bonus

    def OnRightClick(self, x, y, keys, attachment):
        """
        Popup menu when r.click on shape.

        Note: unlike proper toolbar menus, these shortcut keys don't work - you need to add
        onKeyChar() interceptions in umlcanvas.py
        Or we use a global accelerator table on the frame.  <-- 2019 current approach.

        Args:
            x:
            y:
            keys:
            attachment:

        Returns:

        """
        self._SelectNodeNow(x, y, keys, attachment)
        # self.log.WriteText("%s\n" % self.GetShape())

        # self.BuildPopupMenuItems()  should already be built cos of the focus_shape() call
        self.frame.PopupMenu(self.popupmenu, wx.Point(x, y))


        # # MGR attempt
        # pm = self.umlcanvas.shape_popup_menu_mgr
        # pmm.clear()
        # pmm.add_properties()
        # self.frame.PopupMenu(pmm.popupmenu, wx.Point(x, y))
        #
        # return


        # # EXPERIMENT
        #
        # self.accel_entries : List[wx.AcceleratorEntry] = []
        #
        # if self.popupmenu:  # already exists - don't build it again
        #     print("already exists")
        # else:
        #     print("creating popup")
        #     self.popupmenu = wx.Menu()  # This is the popup menu to which we attach menu items
        #     item : wx.MenuItem = self.popupmenu.Append(wx.ID_ANY, "Do Z")
        #     self.frame.Bind(wx.EVT_MENU, self.doZ, item)
        #
        #     item.Enable(False)  # hmm, accelerator still fires :-(
        #
        #     entry = wx.AcceleratorEntry()
        #     # entry.Set(wx.ACCEL_NORMAL, ord('Z'), item.GetId())
        #     entry.Set(wx.ACCEL_CTRL, ord('Z'), item.GetId())
        #     self.accel_entries.append(entry)
        #
        #     accel_tbl = wx.AcceleratorTable(self.accel_entries)
        #     self.frame.SetAcceleratorTable(accel_tbl)
        #     print("self.accel_entries", self.accel_entries)
        #
        # self.frame.PopupMenu(self.popupmenu, wx.Point(x, y))
        #
        #
        # return




    # def TestUpdateUI(self, evt):
    #     import time
    #     text = time.ctime()
    #     # How to get to the target of the event e.g. the specific menu item - AH you need to
    #     # bind a different handler to each menuitem,
    #     # Or you can check evt.GetId()
    #
    #     # evt.SetText(text)  # gosh this sets the text of the menuitem!
    #
    #     evt.Enable(False)  # Accelerator still fires !!??????
    #
    #     # print("TestUpdateUI", text, evt.EventObject)
    #
    # def doZ(self, event):
    #     print("doZ")

    # def _update_line_state(self):
    #     set_item_state(MENU_ID_BEGIN_LINE, self.GetShape().GetCanvas().new_edge_from == None)

    def OnRightClickDeleteNode(self, event):
        self.app.run.CmdNodeDelete(self.GetShape())

    def OnLeftDoubleClick(self, x, y, keys, attachment):
        node_edit_multi_purpose(self.GetShape(), self.app)

    def OnNodeProperties(self, event):
        node_edit_multi_purpose(self.GetShape(), self.app)

    def OnDrawBegin(self, event):
        print("OnDrawBegin")
        # if not is_item_enabled(event.GetId()):
        #     print("OnDrawBegin THWARTED")
        #     return
        self.GetShape().GetCanvas().NewEdgeMarkFrom()
        # self._update_line_state()
        self.focus_shape(self)  # rebuild the accelerator table and menus cos situation changed

    def OnCancelDrawBegin(self, event):
        self.GetShape().GetCanvas().OnCancelLine(event)  # delegate to canvas handler - event dodgy
        self.focus_shape(self)  # rebuild the accelerator table and menus cos situation changed

    def OnDrawEnd1(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type="composition")
        # self._update_line_state()

    def OnDrawEnd2(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type="generalisation")
        # self._update_line_state()

    def OnDrawEnd3(self, event):
        self.GetShape().GetCanvas().NewEdgeMarkTo(edge_type="association")
        # self._update_line_state()

    def OnResetImageSize(self, event):
        shape = self.GetShape()
        shape.ResetSize()
        # shape.GetCanvas().Refresh(False)   # don't seem to need since SelectNodeNow() might be doing it for us
        shape.GetCanvas().SelectNodeNow(shape)
        self.UpdateStatusBar(shape)

    def OnPopupMenuCancel(self, event):
        pass


def node_edit_multi_purpose(shape, app):
    """
    Edit a uml class node or a comment node

    Main menu calls this from pynsourcegui or
    Or uml shape handler (above) calls this when right click on a shape

    Args:
        shape:
        app:

    Returns: -

    """
    # node is a regular node, its the node.shape that is different for a comment
    from gui.uml_shapes import DividedShape

    if isinstance(shape, DividedShape):
        app.run.CmdEditUmlClass(shape)
    elif isinstance(shape, CommentShape):
        app.run.CmdEditComment(shape)
    else:
        print("Unknown Shape", shape)
