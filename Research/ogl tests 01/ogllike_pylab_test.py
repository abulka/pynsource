import wx
from OGLlike_pylab import Diagram, Shape  # more needed...

"""
Experimental mucking around trying to use the "improved" OGLlike_pylab.py
but this file is UNFINISHED and does not even compile - abandoned for now
since the improvements in the pylab version may not be compelling enough?
Plus hard to disentangle from the pylab project https://code.google.com/archive/p/pylab-works/ 
"""


def menuMaker(frame, menus):
    menubar = wx.MenuBar()
    for m, n in list(menus.items()):
        menu = wx.Menu()
        menubar.Append(menu, m)
        for x in n:
            id = wx.NewId()
            menu.Append(id, x[0], x[1])
            wx.EVT_MENU(frame, id, x[2])
    frame.SetMenuBar(menubar)


class RectangleShape(Shape):
    def __init__(self, x=20, y=20, x2=90, y2=90):

        # ANDY
        if ANDYMAIN:
            topx, topy = (
                ANDYMAIN.canvas.GetViewStart()
            )  # The positions are in logical scroll units, not pixels, so to convert to pixels you will have to multiply by the number of pixels per scroll increment.
            print(topx, topy)
            px, py = ANDYMAIN.canvas.GetScrollPixelsPerUnit()
            print(topx, topy, px, py, topx * px, topy * py)
            topx, topy = ANDYMAIN.canvas.CalcUnscrolledPosition(topx * px, topy * py)
            print(topx, topy)
            Shape.__init__(self, [topx + x, topx + x2], [topy + y, topy + y2])
        else:
            Shape.__init__(self, [x, x2], [y, y2])
        ######

        # ANDY
        # Shape.__init__(self, [x,x2] ,  [y,y2])

    def draw(self, dc):
        Shape.draw(self, dc)
        dc.DrawRectangle(
            int(self.x[0]), int(self.y[0]), int(self.x[1] - self.x[0]), int(self.y[1] - self.y[0])
        )

    def HitTest(self, x, y):
        if x < self.x[0]:
            return False
        if x > self.x[1]:
            return False
        if y < self.y[0]:
            return False
        if y > self.y[1]:
            return False
        return True


# class Resizeable:
#     '''
#     Creates resize Nodes that can be drug around the canvas
#     to alter the shape or size of the Shape
#     '''
#
#     def __init__(self):
#         pass
#
#
# class Connectable:
#     '''
#     Creates connection nodes or ports
#     '''
#
#     def __init__(self):
#         self.input = 1
#         self.output = 3
#         self.connections = []  # this will be the list containing downstream connections
#
#     def getPort(self, type, num):
#         if type == 'input':
#             div = float(self.input + 1.0)
#             x = self.x[0]
#         elif type == 'output':
#             div = float(self.output + 1.0)
#             x = self.x[1]
#
#         dy = float(self.y[1] - self.y[0]) / div
#         y = self.y[0] + dy * (num + 1)
#         return (x, y)
#
#
# class Attributable:
#     '''
#     Allows AttributeEditor to edit specified properties
#     of the Shape
#     '''
#
#     def __init__(self):
#         self.attributes = []
#
#     def AddAttribute(self, name):
#         self.attributes.append(name)
#
#     def AddAttributes(self, atts):
#         self.attributes.extend(atts)
#
#     def RemoveAttribute(self, name):
#         self.attributes.remove(name)

# class LinesShape(Shape, Resizeable):
#     def __init__(self, points):
#         Shape.__init__(self)
#         self.x = []
#         self.y = []
#         for p in points:
#             self.x.append(p[0])
#             self.y.append(p[1])
#
#     def draw(self, dc):
#         Shape.draw(self, dc)
#         ind = 0
#         try:
#             while 1:
#                 dc.DrawLine(self.x[ind], self.y[ind], self.x[ind + 1], self.y[ind + 1])
#                 ind = ind + 1
#         except:
#             pass
#
#     def HitTest(self, x, y):
#
#         if x < min(self.x) - 3: return False
#         if x > max(self.x) + 3: return False
#         if y < min(self.y) - 3: return False
#         if y > max(self.y) + 3: return False
#
#         ind = 0
#         try:
#             while 1:
#                 x1 = self.x[ind]
#                 y1 = self.y[ind]
#                 x2 = self.x[ind + 1]
#                 y2 = self.y[ind + 1]
#
#                 top = (x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)
#                 distsqr = pow(x1 - x2, 2) + pow(y1 - y2, 2)
#                 u = float(top) / float(distsqr)
#
#                 newx = x1 + u * (x2 - x1)
#                 newy = y1 + u * (y2 - y1)
#
#                 dist = pow(pow(newx - x, 2) + pow(newy - y, 2), .5)
#
#                 if dist < 7:
#                     return True
#                 ind = ind + 1
#         except IndexError:
#             pass
#         return False
#


class ShapeCanvas(wx.ScrolledWindow):
    def __init__(self, parent, id=-1, pos=(-1, -1), size=(-1, -1), style=0, name=""):
        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)
        self.diagram = None
        self.nodes = []
        self.currentPoint = [0, 0]  # x and y of last mouse click
        self.selectedShapes = []
        self.scalex = 1.0
        self.scaley = 1.0

        # Window Events
        EVT_PAINT(self, self.onPaintEvent)
        # Mouse Events
        EVT_LEFT_DOWN(self, self.OnLeftDown)
        EVT_LEFT_UP(self, self.OnLeftUp)
        EVT_LEFT_DCLICK(self, self.OnLeftDClick)

        EVT_RIGHT_DOWN(self, self.OnRightDown)
        EVT_RIGHT_UP(self, self.OnRightUp)
        EVT_RIGHT_DCLICK(self, self.OnRightDClick)

        EVT_MOTION(self, self.OnMotion)
        # Key Events
        EVT_KEY_DOWN(self, self.keyPress)

    def AddShape(self, shape, after=None):
        self.diagram.AddShape(shape, after)

    def AppendShape(self, shape):
        self.diagram.AppendShape(shape)

    def InsertShape(self, shape, index=0):
        self.diagram.InsertShape(shape, index)

    def DeleteShape(self, shape):
        self.diagram.DeleteShape(shape)

    def RemoveShape(self, shape):
        self.diagram.DeleteShape(shape)

    def keyPress(self, event):
        key = event.GetKeyCode()
        if key == 127:  # DELETE
            # self.diagram.shapes = [n for n in self.diagram.shapes if not n in self.select()]
            for s in self.select():
                self.diagram.DeleteShape(s)
            self.deselect()  # remove nodes
        elif key == 67 and event.ControlDown():  # COPY
            del clipboard[:]
            for i in self.select():
                clipboard.append(i)
        elif key == 86 and event.ControlDown():  # PASTE
            for i in clipboard:
                self.AddShape(i.Copy())
        elif key == 9:  # TAB
            if len(self.diagram.shapes) == 0:
                return
            shape = self.select()
            if shape:
                ind = self.diagram.shapes.index(shape[0])
                self.deselect()
                try:
                    self.select(self.diagram.shapes[ind + 1])
                except:
                    self.select(self.diagram.shapes[0])
            else:
                self.select(self.diagram.shapes[0])
        self.Refresh()

    def onPaintEvent(self, event):
        dc = PaintDC(self)
        self.PrepareDC(dc)
        dc.SetUserScale(self.scalex, self.scaley)
        # dc.BeginDrawing()
        for item in self.diagram.shapes + self.nodes:
            item.draw(dc)
        # dc.EndDrawing()

    def OnRightDown(self, event):
        # ANDY
        # self.getCurrentShape(event).OnRightDown(event)

        # ANDY
        if self.getCurrentShape(event):
            self.getCurrentShape(event).OnRightDown(event)

    def OnRightUp(self, event):
        # ANDY
        # self.getCurrentShape(event).OnRightUp(event)

        # ANDY
        if self.getCurrentShape(event):
            self.getCurrentShape(event).OnRightUp(event)
        else:
            #
            self.popupmenu = Menu()
            item = self.popupmenu.Append(2021, "Properties...")
            self.Bind(EVT_MENU, self.OnPopupItemSelected, item)
            item = self.popupmenu.Append(2022, "Cancel")
            self.Bind(EVT_MENU, self.OnPopupItemSelected, item)

            pos = event.GetPosition()
            pos = self.ScreenToClient(pos)
            self.PopupMenu(self.popupmenu, pos)
        ########

    # ANDY
    def OnPopupItemSelected(self, event):
        item = self.popupmenu.FindItemById(event.GetId())
        text = item.GetText()
        MessageBox("You selected item '%s'" % text)

    ################

    def OnRightDClick(self, event):
        self.getCurrentShape(event).OnRightDClick(event)

    def OnLeftDClick(self, event):
        self.getCurrentShape(event).OnLeftDClick(event)

    def OnLeftDown(self, event):
        item = self.getCurrentShape(event)

        if item is None:  # clicked on empty space deselect all
            self.deselect()
            return

        item.OnLeftDown(event)  # send leftdown event to current shape

        if isinstance(item, Selectable):
            if not event.ShiftDown():
                self.deselect()

        self.select(item)
        self.Refresh()

    def OnLeftUp(self, event):
        try:
            shape = self.getCurrentShape(event)
            shape.OnLeftUp(event)
            shape.leftUp(self.select())
        except:
            pass
        self.Refresh()

    def OnMotion(self, event):
        if event.Dragging():
            point = self.getEventCoordinates(event)
            x = point[0] - self.currentPoint[0]
            y = point[1] - self.currentPoint[1]
            for i in self.getSelectedShapes():
                i.move(x, y)
            self.currentPoint = point
            self.Refresh()

    def SetDiagram(self, diagram):
        self.diagram = diagram

    def getCurrentShape(self, event):
        # get coordinate of click in our coordinate system
        point = self.getEventCoordinates(event)
        self.currentPoint = point
        # Look to see if an item is selected
        for item in self.nodes + self.diagram.shapes:
            if item.HitTest(point[0], point[1]):
                return item
        return None

    def getEventCoordinates(self, event):
        originX, originY = self.GetViewStart()
        unitX, unitY = self.GetScrollPixelsPerUnit()
        return [
            (event.GetX() + (originX * unitX)) / self.scalex,
            (event.GetY() + (originY * unitY)) / self.scaley,
        ]

    def getSelectedShapes(self):
        return self.selectedShapes

    def deselect(self, item=None):
        if item is None:
            for s in self.selectedShapes:
                s.OnDeselect(None)
            del self.selectedShapes[:]
            del self.nodes[:]
        else:
            self.nodes = [n for n in self.nodes if n.item != item]
            self.selectedShapes = [n for n in self.selectedShapes if n != item]
            item.OnDeselect(None)

    def select(self, item=None):
        if item is None:
            return self.selectedShapes

        if isinstance(item, Node):
            del self.selectedShapes[:]
            self.selectedShapes.append(item)  # items here is a single node
            return

        if not item in self.selectedShapes:
            self.selectedShapes.append(item)
            item.OnSelect(None)
            if isinstance(item, Connectable):
                self.nodes.extend([INode(item, n, self) for n in range(item.input)])
                self.nodes.extend([ONode(item, n, self) for n in range(item.output)])
            if isinstance(item, Resizeable):
                self.nodes.extend([ResizeableNode(item, n, self) for n in range(len(item.x))])

    def showOutputs(self, item=None):
        if item:
            self.nodes.extend([ONode(item, n, self) for n in range(item.output)])
        elif item is None:
            for i in self.diagram.shapes:
                if isinstance(i, Connectable):
                    self.nodes.extend([ONode(i, n, self) for n in range(i.output)])

    def showInputs(self, item=None):
        if isinstance(item, Block):
            self.nodes.extend([INode(item, n, self) for n in range(item.input)])
        else:
            for i in self.diagram.shapes:
                if isinstance(i, Connectable):
                    self.nodes.extend([INode(i, n, self) for n in range(i.input)])


class Block(RectangleShape, Connectable, Resizeable, Selectable, Attributable):
    def __init__(self):
        RectangleShape.__init__(self)
        Resizeable.__init__(self)
        Connectable.__init__(self)
        Attributable.__init__(self)
        self.AddAttributes(["label", "pen", "fill", "input", "output"])
        self.label = "Block"

    def draw(self, dc):
        RectangleShape.draw(self, dc)
        w, h = dc.GetTextExtent(self.label)
        mx = int((self.x[0] + self.x[1]) / 2.0) - int(w / 2.0)
        my = int((self.y[0] + self.y[1]) / 2.0) - int(h / 2.0)
        dc.DrawText(self.label, mx, my)

    def OnLeftDown(self, event):
        if isinstance(self, Block) and event.ControlDown():
            d = TextEntryDialog(None, "Block Label", defaultValue=self.label, style=OK)
            d.ShowModal()
            self.label = d.GetValue()

    # ANDY
    # def OnRightDown(self,event):
    #    f = AttributeEditor(NULL, -1, "props",self)
    #    f.Show(True)

    # ANDY
    def OnRightDown(self, event):
        self.popupmenu = Menu()
        item = self.popupmenu.Append(2011, "Properties...")
        ANDYMAIN.canvas.Bind(EVT_MENU, self.OnPopupItemSelected, item)
        item = self.popupmenu.Append(2012, "Delete Node")
        ANDYMAIN.canvas.Bind(EVT_MENU, self.OnPopupItemSelected, item)
        item = self.popupmenu.Append(2013, "Cancel")
        ANDYMAIN.canvas.Bind(EVT_MENU, self.OnPopupItemSelected, item)
        #
        pos = event.GetPosition()
        pos = ANDYMAIN.canvas.ScreenToClient(pos)
        ANDYMAIN.canvas.PopupMenu(self.popupmenu, pos)

    ##########

    # ANDY
    def OnPopupItemSelected(self, event):
        item = self.popupmenu.FindItemById(event.GetId())
        text = item.GetText()
        # wx.MessageBox("You selected item '%s'" % text)
        if text == "Properties...":
            f = AttributeEditor(None, -1, "props", self)
            f.Show(True)

    ################


#
# class CodeBlock(Block):
#
#   def __init__(self):
#     Block.__init__(self)
#     self.AddAttribute('code')
#     self.code = ''
#     self.label = 'Code'
#
#   def OnLeftDClick(self, event):
#     exec str(self.code)
#
#
class ContainerBlock(Block, Diagram):
    def __init__(self):
        Block.__init__(self)
        Diagram.__init__(self)

        self.label = "Container"
        self.pen = ["BLACK", 2]
        self.fill = ["GREEN"]

    def OnLeftDClick(self, event):
        f = CodeFrame(self)
        f.SetTitle(self.label)
        f.Show(True)


# class AttributeEditor(Frame):
#     def __init__(self, parent, ID, title, item):
#         Frame.__init__(self, parent, ID, title,
#                        DefaultPosition, Size(200, 450))
#         self.item = item
#         # Create a box sizer for self
#         box = BoxSizer(VERTICAL)
#         self.SetSizer(box)
#
#         tID = NewId()
#         self.list = ListCtrl(self, tID, DefaultPosition, DefaultSize, LC_REPORT)
#         self.SetSize(self.GetSize())
#
#         self.list.InsertColumn(0, "Attribute")
#         self.list.InsertColumn(1, "Value")
#
#         accept = Button(self, NewId(), "Accept", size=(40, 20))
#
#         for c in range(len(item.attributes)):
#             self.list.InsertStringItem(c, "")
#             self.list.SetStringItem(c, 0, str(item.attributes[c]))
#             temp = str(eval("item." + str(item.attributes[c])))
#             self.list.SetStringItem(c, 1, temp)
#
#         self.text = TextCtrl(self, NewId(), "", style=TE_MULTILINE)
#
#         box.Add(self.list, 1, EXPAND)
#         box.Add(accept, 0, EXPAND)
#         box.Add(self.text, 1, EXPAND)
#
#         EVT_LIST_ITEM_SELECTED(self.list, tID, self.selectProp)
#         EVT_BUTTON(accept, accept.GetId(), self.acceptProp)
#
#     def selectProp(self, event):
#         idx = self.list.GetFocusedItem()
#         prop = self.list.GetItem(idx, 0).GetText()
#         val = self.list.GetItem(idx, 1).GetText()
#         self.text.Clear()
#         self.text.WriteText(val)
#
#     def acceptProp(self, event):
#         idx = self.list.GetFocusedItem()
#         prop = self.list.GetItem(idx, 0).GetText()
#         lines = self.text.GetNumberOfLines()
#         if lines == 1:
#             exec 'self.item.' + prop + '=' + self.text.GetValue()
#         else:
#             p = setattr(self.item, prop, self.text.GetValue())
#
#         self.list.SetStringItem(idx, 1, str(getattr(self.item, prop)))


class CodeFrame(wx.Frame):
    def __init__(self, diagram):
        wx.Frame.__init__(self, None, -1, "Untitled", size=(500, 300))

        self.file = None
        menus = {}

        menus["&Add"] = [
            ("Code", "Block that holds code", self.newCodeBlock),
            ("Container", "Block that holds blocks", self.newContBlock),
            ("Point", "Playing with points", self.newPointShape),
            ("Lines", "Plotting", self.newLinesShape),
        ]

        menus["&Zoom"] = [
            ("Zoom In\tCtrl+o", "zoom in", self.zoomin),
            ("Zoom Out\tCtrl+p", "zoom out", self.zoomout),
        ]

        menuMaker(self, menus)

        # Canvas Stuff
        self.canvas = ShapeCanvas(self, -1)
        self.canvas.SetDiagram(diagram)
        self.canvas.SetBackgroundColour(WHITE)

        # ANDY
        global ANDYMAIN
        ANDYMAIN = self
        #
        self.canvas.SetScrollbars(1, 1, 600, 400)
        self.canvas.SetVirtualSize((600, 400))
        ################

        self.Show(True)

    # ANDY
    # def OnPopupItemSelected(self, event):
    #    OnPopupItemSelected(self, event):
    #
    #    item = self.popupmenu.FindItemById(event.GetId())
    #    text = item.GetText()
    #    wx.MessageBox("You selected item '%s'" % text)
    #    if text == "Properties...":
    #        f = AttributeEditor(NULL, -1, "props",self)
    #        f.Show(True)
    ################

    def zoomin(self, event):
        self.canvas.scalex = max(self.canvas.scalex + 0.05, 0.3)
        self.canvas.scaley = max(self.canvas.scaley + 0.05, 0.3)

        # ANDY
        self.canvas.SetVirtualSize((1900, 1600))

        self.canvas.Refresh()

    def zoomout(self, event):
        self.canvas.scalex = self.canvas.scalex - 0.05
        self.canvas.scaley = self.canvas.scaley - 0.05
        self.canvas.Refresh()

    def newCodeBlock(self, event):
        i = CodeBlock()
        self.canvas.AddShape(i)
        self.canvas.deselect()
        self.canvas.Refresh()

    def newContBlock(self, event):
        i = ContainerBlock()
        self.canvas.AddShape(i)
        self.canvas.deselect()
        self.canvas.Refresh()

    def newPointShape(self, event):
        i = PointShape(50, 50)
        self.canvas.AddShape(i)
        self.canvas.deselect()
        self.canvas.Refresh()

    def newLinesShape(self, event):
        points = [
            (5, 30),
            (10, 20),
            (20, 25),
            (30, 50),
            (40, 70),
            (50, 30),
            (60, 20),
            (70, 25),
            (80, 50),
            (90, 70),
            (100, 30),
            (110, 20),
            (115, 25),
            (120, 50),
            (125, 70),
            (130, 30),
            (135, 20),
            (140, 25),
            (150, 50),
            (160, 70),
            (165, 30),
            (170, 20),
            (175, 25),
            (180, 50),
            (200, 70),
        ]
        i = LinesShape(points)
        self.canvas.AddShape(i)
        self.canvas.deselect()
        self.canvas.Refresh()


class MyApp(wx.App):
    def OnInit(self):
        frame = CodeFrame(ContainerBlock())
        return True


##########################################

app = MyApp(0)
app.MainLoop()
