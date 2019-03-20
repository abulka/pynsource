import wx
from textwrap import dedent

app = wx.App(False)
d = {}
AUTHOR_MODE = True
selected = None
button1 = button2 = None
working = False  # for keys


class Meta:
    """
    Allows AttributeEditor to edit specified properties
    of the Shape
    """
    def __init__(self):
        self.attributes = []

    def AddAttribute(self, name):
        self.attributes.append(name)

    def AddAttributes(self, atts):
        self.attributes.extend(atts)

    def RemoveAttribute(self, name):
        self.attributes.remove(name)

# def wMouseDown(e):
#     print("!!!", e.GetEventObject())

def MouseDown(event):
    print("MouseDown")
    global selected
    o = event.GetEventObject()
    selected = o

    if selected and event and event.ShiftDown():
        f = AttributeEditor(None, -1, "props", selected)
        f.Show(True)
    else:
        sx, sy = panel.ScreenToClient(o.GetPosition())
        dx, dy = panel.ScreenToClient(wx.GetMousePosition())
        o._x, o._y = (sx - dx, sy - dy)
        d['d'] = o
        panel.Refresh()


def MouseMove(e):
    try:
        if 'd' in d:
            o = d['d']
            x, y = wx.GetMousePosition()
            o.SetPosition(wx.Point(x+o._x,y+o._y))

            panel.Refresh()
    except: pass

def MouseUp(event):
    global selected
    try:
        if 'd' in d: del d['d']
    except: pass
    print("MouseUp", d)

    o = event.GetEventObject()
    if o is panel:
        selected = None
        panel.Refresh()

def author_mode_click(event):
    # print("checkbox state is", event.GetEventObject(), event.GetEventObject().IsChecked())
    global AUTHOR_MODE
    AUTHOR_MODE = event.GetEventObject().IsChecked()
    check_mode_do_wiring()
    event.Skip()

def RunCode(event):
    print("running code")
    obj = event.GetEventObject()
    
    # eval(code)
    exec(str(obj.meta.code))


def on_panel_paint(event):
    # print(f"on panel paint, AUTHOR_MODE {AUTHOR_MODE}, selected={selected}")
    if AUTHOR_MODE:

        if button1:  # if haven't erased everything - fix

            if selected:
                dc = wx.PaintDC(panel)
                MARGIN = 5
                bounds1 = selected.GetRect()
                bounds1[0] -= MARGIN
                bounds1[1] -= MARGIN
                bounds1[2] += 2 * MARGIN
                bounds1[3] += 2 * MARGIN

                # dc.SetPen(wx.Pen('RED'))
                # dc.SetBrush(wx.Brush('BLUE'))
                dc.SetBrush(wx.Brush("grey", wx.TRANSPARENT))
                # dc.DrawRectangle(130, 15, 90, 60)
                dc.DrawRectangle(bounds1)

def check_mode_do_wiring():
    global button1, button2, box_tools
    if AUTHOR_MODE:
        print("Author mode enabled")

        if button1:
            bind_all()
        box_tools.ShowItems(show=True)
        # box_tools.Show()
    else:
        print("Author mode disabled")
        if button1:
            unbind_all()

            # Bind to run code
            button1.Bind(wx.EVT_LEFT_UP, RunCode)
            button2.Bind(wx.EVT_LEFT_UP, RunCode)
        box_tools.ShowItems(show=False)
        # box_tools.Hide()
        frame.SetStatusText("Run mode: Hit ESC to get back to Author mode")

    m_checkBox1.SetValue(AUTHOR_MODE)

    # panel.Refresh(eraseBackground=True)
    panel.Refresh(eraseBackground=False)
    print(f"button1={button1}, button2={button2}")

def onKeyPress(event):
    global AUTHOR_MODE, working, frame

    keycode = event.GetKeyCode()  # http://www.wxpython.org/docs/api/wx.KeyEvent-class.html
    print(keycode)

    if working:
        event.Skip()
        return
    working = True

    if keycode == wx.WXK_ESCAPE:
        frame.SetStatusText("ESC key detected: Back to Author mode")
        if not AUTHOR_MODE:
            AUTHOR_MODE = True
            check_mode_do_wiring()
    #
    # if keycode == wx.WXK_RIGHT:
    #     self.app.run.CmdLayoutExpand(remove_overlaps=not event.ShiftDown())
    #
    elif keycode == wx.WXK_F3:
        AUTHOR_MODE = not AUTHOR_MODE
        check_mode_do_wiring()

    working = False
    event.Skip()

def bind_all():
    global button1, button2
    print("bind_all", button1, button2)
    button1.Bind(wx.EVT_LEFT_DOWN, MouseDown)
    button2.Bind(wx.EVT_LEFT_DOWN, MouseDown)

    button1.Bind(wx.EVT_MOTION, MouseMove)
    button2.Bind(wx.EVT_MOTION, MouseMove)

    button1.Bind(wx.EVT_LEFT_UP, MouseUp)
    button2.Bind(wx.EVT_LEFT_UP, MouseUp)

def unbind_all():
    global button1, button2
    print("unbind_all", button1, button2)
    button1.Unbind(wx.EVT_LEFT_DOWN)
    button2.Unbind(wx.EVT_LEFT_DOWN)

    button1.Unbind(wx.EVT_MOTION)
    button2.Unbind(wx.EVT_MOTION)

    button1.Unbind(wx.EVT_LEFT_UP)
    button2.Unbind(wx.EVT_LEFT_UP)

def clear_page(event):
    print("clearing all")
    # for child in panel.GetChildren():
    #     child.Destroy()
    global button1, button2
    unbind_all()
    button1.Destroy()
    button2.Destroy()
    button1 = None
    button2 = None
    panel.Refresh(eraseBackground=False)


def add_widgets(event):
    global button1, button2
    if button1 == None and button2 == None:
        _add_widgets(None)
        bind_all()
    else:
        print("Already have buttons on page!!")

def _add_widgets(event):
    global button1, button2
    global box, properties, panel

    button1 = wx.Button(panel, -1, "foo")
    box.Add(button1, 0, wx.ALL, 10)
    button2 = wx.Button(panel, -1, "bar")
    box.Add(button2, 0, wx.ALL, 10)

    m = button1.meta = Meta()
    m.AddAttributes(["label", "pen", "fill"])
    m.AddAttribute("code")
    m.code = dedent("""
        # Hi there this is some code
        # in Python Toolbook!
        x = 11
        y = 2
        print(x + y)
        for i in range(100):
            print(i, end=" ")
        print("done!")

        # A gui message
        #wx.MessageBox(f"Hi from a button click")
    """).strip()
    m.label = "Code"
    m.pen = ["BLACK", 2]
    m.fill = ["GREEN"]

    m = button2.meta = Meta()
    m.AddAttributes(["label", "pen", "fill"])
    m.AddAttribute("code")
    m.code = dedent("""
        # Hi there this is some code
        # in Python Toolbook!
        x = 1
        y = 2
        print(x + y)
        for i in range(100):
            print(i, end=" ")
        print("done!")
        
        # A gui message
        wx.MessageBox(f"Hi from a button click")
    """).strip()
    m.label = "Code ha ha"
    m.pen = ["RED", 5]
    m.fill = ["GREEN"]

    panel.Layout()


######


frame = wx.Frame(None, -1, 'Pytoolbook')
frame.CreateStatusBar()
panel = wx.Panel(frame)
box = wx.BoxSizer(wx.VERTICAL)
box_tools = wx.BoxSizer(wx.HORIZONTAL)

m_checkBox1 = wx.CheckBox( panel, wx.ID_ANY, "Author Mode", wx.DefaultPosition, wx.DefaultSize, 0 )
m_checkBox1.SetValue(AUTHOR_MODE)
box_tools.Add( m_checkBox1, 0, wx.ALL, 5 )

button_clear = wx.Button(panel, -1, "Clear All")
box_tools.Add(button_clear, 0, wx.ALL)

button_add_buttons = wx.Button(panel, -1, "Add Widgets")
box_tools.Add(button_add_buttons, 0, wx.ALL)

box.Add(box_tools, 0, wx.ALL)



_add_widgets(event=None)



panel.Bind(wx.EVT_PAINT, on_panel_paint)

check_mode_do_wiring()

panel.Bind(wx.EVT_MOTION, MouseMove)
panel.Bind(wx.EVT_LEFT_UP, MouseUp)
panel.Bind(wx.EVT_KEY_DOWN, onKeyPress)

#####

from ast import literal_eval


def get_type(input_data):
    """
    Guess type of input string

    print(get_type("1"))        # <class 'int'>
    print(get_type("1.2354"))   # <class 'float'>
    print(get_type("True"))     # <class 'bool'>
    print(get_type("abcd"))     # <class 'str'>

    See https://stackoverflow.com/questions/22199741/identifying-the-data-type-of-an-input

    Args:
        input_data: str

    Returns: type class
    """
    try:
        return type(literal_eval(input_data))
    except (ValueError, SyntaxError):
        # A string, so return str
        return str

class AttributeEditor(wx.Frame):
    def __init__(self, parent, ID, title, item):
        print(f"attribute editor invoked on {item}, has attribute obj {item.meta}")

        """Edits properties of 'item' as defined by the list of properties in item.attributes"""
        wx.Frame.__init__(self, parent, ID, title, wx.DefaultPosition, wx.Size(800, 550))
        self.item = item  # type wx.Button, not Block

        # Create a box sizer for self
        box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(box)

        tID = wx.NewIdRef()  # was wx.NewId()
        self.list = wx.ListCtrl(self, tID, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT)
        self.SetSize(self.GetSize())

        self.list.InsertColumn(0, "Attribute")
        self.list.InsertColumn(1, "Value")

        self.accept = wx.Button(self, wx.ID_ANY, "Apply", size=(40, 20))

        for c in range(len(item.meta.attributes)):
            self.list.InsertItem(c, "")  # insert the list control item
            self.list.SetItem(c, 0, str(item.meta.attributes[c]))  # set the list control item's 0 col

            # set the list control item's 1 col to actual value of the attribute, converted into
            # a string for display purposes
            temp = str(eval("item.meta." + str(item.meta.attributes[c])))
            self.list.SetItem(c, 1, temp)

        # This is the area we edit in - first select the attribute and then edit in here
        self.text = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.text.SetBackgroundColour((255, 255, 230))  # set text back color

        # Close button
        button = wx.Button(self, label="Close")

        # The layout
        box.Add(self.list, 1, wx.EXPAND)
        box.Add(self.text, 1, wx.EXPAND)
        box.Add(self.accept, 0, wx.EXPAND)
        box.Add(button, 0, wx.EXPAND)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selectProp, self.list, tID)
        self.Bind(wx.EVT_BUTTON, self.acceptProp, self.accept, self.accept.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, button)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.accept.Disable()

        # CMD-W to close Frame by attaching the key bind event to accellerator table
        randomId = wx.NewIdRef()  # was wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=randomId)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("W"), randomId)])
        self.SetAcceleratorTable(accel_tbl)

    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()

    def selectProp(self, event):
        """When you click on an item in the list control, populate the edit text area with its content"""
        idx = self.list.GetFocusedItem()
        prop = self.list.GetItem(idx, 0).GetText()
        val = self.list.GetItem(idx, 1).GetText()
        self.text.Clear()
        self.text.WriteText(val)

        self.accept.Enable()

    def acceptProp(self, event):
        """Write the edited value back into the property"""
        idx = self.list.GetFocusedItem()
        print(idx)
        prop = self.list.GetItem(idx, 0).GetText()  # calc property name

        if get_type(self.text.GetValue()) == str or self.text.GetNumberOfLines() > 1:
            val = self.text.GetValue()  # string
        else:
            val = eval(self.text.GetValue())  # convert string back into Python data e.g int or list
        setattr(self.item.meta, prop, val)

        self.list.SetItem(idx, 1, str(getattr(self.item.meta, prop)))




# Connect Events
m_checkBox1.Bind(wx.EVT_CHECKBOX, author_mode_click)
button_clear.Bind(wx.EVT_LEFT_UP, clear_page)
button_add_buttons.Bind(wx.EVT_LEFT_UP, add_widgets)

panel.SetSizer(box)
panel.Layout()
frame.Show()

app.MainLoop()

