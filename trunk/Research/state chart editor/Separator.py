from Tkinter import *
from Globals import *

class Separator:
    def __init__(self, state, y, handler):
        self.y = y
        self.state = state # parent state
        self.canvas = None
	self.handler = handler
        self.color = "black"

    def setColor(self, color):
        self.color = color        
        self.updateDisplay()
 
    def getColor(self):
        if self.state.borderColor != "black":
            return self.state.borderColor
        else:
            return self.color

    def getY(self):
        return self.y

    # used by SeparatorTranslater.
    def setY(self, y):
	if y < self.state.y0 + SEPARATOR_PAD:
            y = self.state.y0 + SEPARATOR_PAD
	if y > self.state.y1 - SEPARATOR_PAD:
            y = self.state.y1 - SEPARATOR_PAD
        self.y = y
	self.updateDisplay()

    def setMark(self): # remember current position
        self.mark = self.y

    def backToMark(self): # go back to last mark
        self.y = self.mark
        self.updateDisplay()

    # used by state. Note that display is not updated
    def translate(self, dy):
	self.y = self.y + dy
        
    def setCanvas(self, canvas):
        if self.canvas == None and canvas != None:
            self.canvas = canvas
            self._createItems()
            self._bindEvents()
        elif self.canvas != None and canvas == None:
            self._deleteItems()
            self.canvas = None

    def updateDisplay(self):
        if self.canvas == None:
            return
        s = self.state
        self.canvas.itemconfig(self.line, fill=self.getColor())
        self.canvas.coords(self.line, s.x0,self.y, s.x1, self.y)

    def lift(self):
	if self.canvas == None:
	    return
        self.canvas.lift(self.line)

    # only to avoid having pickle to save the handler...
    def setHandler(self, handler):
        self.handler = handler

    def _createItems(self):
        s = self.state
        self.line = self.canvas.create_line(s.x0,self.y,s.x1,self.y, fill=self.getColor(), stipple=SEPARATOR_BITMAP, width=SEPARATOR_WIDTH)

    def _deleteItems(self):
        self.canvas.delete(self.line)

    def _bindEvents(self):
        i = self.line
        self.canvas.tag_bind(i, "<Enter>", self.onEnter)
        self.canvas.tag_bind(i, "<Leave>", self.onLeave)
        self.canvas.tag_bind(i, "<Button-1>", self.onButton1)
        self.canvas.tag_bind(i, "<Button-3>", self.onButton3)
        self.canvas.tag_bind(i, "<B1-Motion>", self.onButtonMotion1)
        self.canvas.tag_bind(i, "<B3-Motion>", self.onButtonMotion3)
        self.canvas.tag_bind(i, "<ButtonRelease-1>", self.onButtonRelease1)
        self.canvas.tag_bind(i, "<ButtonRelease-3>", self.onButtonRelease3)
 
    def onEnter(self, event):
        self.handler.onSeparatorEnter(self, self.state, event)

    def onLeave(self, event):
        self.handler.onSeparatorLeave(self, self.state, event)
        
    def onButton1(self, event):
        self.handler.onSeparatorButton1(self, self.state, event)

    def onButton3(self, event):
        self.handler.onSeparatorButton3(self, self.state, event)

    def onButtonMotion1(self, event):
        self.handler.onSeparatorButtonMotion1(self, self.state, event)

    def onButtonMotion3(self, event):
        self.handler.onSeparatorButtonMotion3(self, self.state, event)

    def onButtonRelease1(self, event):
        self.handler.onSeparatorButtonRelease1(self, self.state, event)

    def onButtonRelease3(self, event):
        self.handler.onSeparatorButtonRelease3(self, self.state, event)







