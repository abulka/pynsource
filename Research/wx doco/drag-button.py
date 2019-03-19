import wx

app = wx.App(False)
d = {}
properties = {}
AUTHOR_MODE = True
selected = None

class HypercardProperty:
    def __init__(self):
        self.code = ""
        self.props = {}

def wMouseDown(e):
    print("!!!", e.GetEventObject())

def MouseDown(e):
    global selected
    o           = e.GetEventObject()
    sx,sy       = panel.ScreenToClient(o.GetPosition())
    dx,dy       = panel.ScreenToClient(wx.GetMousePosition())
    o._x,o._y   = (sx-dx, sy-dy)
    d['d'] = o
    selected = o
    panel.Refresh()
    print(d)

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
    mode_switch()
    event.Skip()

def RunCode(event):
    print("running code")
    obj = event.GetEventObject()
    code = properties[obj].code
    eval(code)

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

def mode_switch():
    if AUTHOR_MODE:
        print("Author mode enabled")

        if button1:
            bind_all()
    else:
        print("Author mode disabled")
        if button1:
            unbind_all()

            # Bind to run code
            button1.Bind(wx.EVT_LEFT_UP, RunCode)
            button2.Bind(wx.EVT_LEFT_UP, RunCode)

    # panel.Refresh(eraseBackground=True)
    panel.Refresh(eraseBackground=False)

def bind_all():
    global button1, button2
    button1.Bind(wx.EVT_LEFT_DOWN, MouseDown)
    button2.Bind(wx.EVT_LEFT_DOWN, MouseDown)

    button1.Bind(wx.EVT_MOTION, MouseMove)
    button2.Bind(wx.EVT_MOTION, MouseMove)

    button1.Bind(wx.EVT_LEFT_UP, MouseUp)
    button2.Bind(wx.EVT_LEFT_UP, MouseUp)

def unbind_all():
    global button1, button2
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
    properties = {}
    panel.Refresh(eraseBackground=False)

frame = wx.Frame(None, -1, 'Pytoolbook')
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

button1 = wx.Button(panel, -1, "foo")
box.Add(button1, 0, wx.ALL, 10)
button2 = wx.Button(panel, -1, "bar")
box.Add(button2, 0, wx.ALL, 10)

properties[button1] = HypercardProperty()
properties[button2] = HypercardProperty()

properties[button1].code = "print('hi there')"
# properties[button2].code = r'wx.MessageBox(f"Hi from a button click {button.GetLabel()}")'
properties[button2].code = r'wx.MessageBox(f"Hi from a button click")'

panel.Bind(wx.EVT_PAINT, on_panel_paint)

mode_switch()

panel.Bind(wx.EVT_MOTION, MouseMove)
panel.Bind(wx.EVT_LEFT_UP, MouseUp)


def add_widgets(event):
    print("adding widgets")
    global button1, button2
    global box, properties, panel

    button1 = wx.Button(panel, -1, "foo")
    box.Add(button1, 0, wx.ALL, 10)
    button2 = wx.Button(panel, -1, "bar")
    box.Add(button2, 0, wx.ALL, 10)

    properties[button1] = HypercardProperty()
    properties[button2] = HypercardProperty()

    properties[button1].code = "print('hi there')"
    # properties[button2].code = r'wx.MessageBox(f"Hi from a button click {button.GetLabel()}")'
    properties[button2].code = r'wx.MessageBox(f"Hi from a button click")'
    panel.Layout()
    bind_all()

# Connect Events
m_checkBox1.Bind(wx.EVT_CHECKBOX, author_mode_click)
button_clear.Bind(wx.EVT_LEFT_DOWN, clear_page)
button_add_buttons.Bind(wx.EVT_LEFT_DOWN, add_widgets)

panel.SetSizer(box)
panel.Layout()
frame.Show()

app.MainLoop()

