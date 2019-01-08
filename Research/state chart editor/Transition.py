from tkinter import *
from Globals import *

class Transition:
    def __init__(self, src, dest, handler, event="e", time=-1,history=0):
        self.src = src
	self.dest = dest
	self.event = event
	self.time = time
        self.history = history
	self.code = ""
        self.canvas = None
	self.handler = handler
        self.selected = 0
        self._initCoords()

    def getSrc(self):
        return self.src

    def setSrc(self, state):
        self.src = state

    def getDest(self):
        return self.dest

    def setDest(self, state):
        self.dest = state

    def getTime(self):
        return self.time

    def setTime(self, time):
	self.time = time
	if self.canvas != None:
            self.canvas.itemconfig(self.label, text=self._getText())

    def getEvent(self):
        return self.event

    def setEvent(self, event):
	self.event = event
        self.canvas.itemconfig(self.label, text=self._getText())

    def getHistory(self):
        return self.history

    def setHistory(self, history):
        self.history = history
        self.canvas.itemconfig(self.label, text=self._getText())

    def getCode(self):
        return self.code

    def setCode(self, code):
        self.code = code

    def select(self):
	if self.selected == 1:
            return
	self.canvas.itemconfig(self.arrow, fill=SELECTED_COLOR)
	self.canvas.itemconfig(self.label, fill=SELECTED_COLOR)
        self._createDots()
	self._bindDots()
	self.selected = 1

    def deselect(self):
	if self.selected == 0:
            return
	self.canvas.itemconfig(self.arrow, fill="black")
	self.canvas.itemconfig(self.label, fill="black")
	self._deleteDots()
	self.selected = 0

    def translateSrcDot(self, dx, dy):
	self.srcX = self.srcX + dx
	self.srcY = self.srcY + dy
	self._updateItems()

    def translateDestDot(self, dx, dy):
	self.destX = self.destX + dx
	self.destY = self.destY + dy
	self._updateItems()

    def translateHandleDot(self, dx, dy):
	self.handleX = self.handleX + dx
	self.handleY = self.handleY + dy
	self._updateItems()

    def setCanvas(self, canvas):
        if self.canvas == None and canvas != None:
            self.canvas = canvas
            self._createItems()
            self._bindEvents()
        elif self.canvas != None and canvas == None:
            self._deleteItems()
            self.canvas = None

    def updateDisplay(self):
	self.srcX, self.srcY = self.src.getBorderPoint(self.handleX, self.handleY)
	self.destX, self.destY = self.dest.getBorderPoint(self.handleX, self.handleY)
	self._updateItems()

    def _updateItems(self):
        self.canvas.coords(self.arrow, self.srcX, self.srcY, self.handleX, self.handleY, self.destX, self.destY)
	self.canvas.coords(self.label, self.handleX, self.handleY - TRANSITION_LABEL_DY)
        if self.selected:
            td = TRANSITION_DOT
            self.canvas.coords(self.srcDot, self.srcX-td, self.srcY-td, self.srcX+td, self.srcY+td)
            self.canvas.coords(self.destDot, self.destX-td, self.destY-td, self.destX+td, self.destY+td)
            self.canvas.coords(self.handleDot, self.handleX-td, self.handleY-td, self.handleX+td, self.handleY+td)


    def lift(self):
        self.canvas.lift(self.arrow)
        self.canvas.lift(self.label)
	if self.selected:
            self.canvas.lift(self.srcDot)
            self.canvas.lift(self.destDot)
            self.canvas.lift(self.handleDot)

    # only to avoid having pickle to save the handler...
    def setHandler(self, handler):
        self.handler = handler

    def _initCoords(self):
	sx0,sy0,sx1,sy1,sr = self.src.getCoords()
	dx0,dy0,dx1,dy1,dr = self.dest.getCoords()
	self.srcX, self.srcY = self.src.getBorderPoint(dx0+(dx1-dx0)/2, dy0+(dy1-dy0)/2)
	self.destX, self.destY = self.dest.getBorderPoint(sx0+(sx1-sx0)/2, sy0+(sy1-sy0)/2)
	self.handleX = self.srcX + (self.destX-self.srcX)/2
	self.handleY =  self.srcY + (self.destY-self.srcY)/2

    def _createItems(self):
	if self.selected:
            color=SELECTED_COLOR
        else:
            color="black"
        self.arrow = self.canvas.create_line(self.srcX, self.srcY, self.handleX, self.handleY, self.destX, self.destY, arrow="last", width=TRANSITION_WIDTH,smooth=1,fill=color)
	self.label = self.canvas.create_text(self.handleX, self.handleY - TRANSITION_LABEL_DY,fill=color, text = self._getText())
        if self.selected:
            self._createDots()

    def _createDots(self):
	td = TRANSITION_DOT
        self.srcDot = self.canvas.create_rectangle(self.srcX-td, self.srcY-td, self.srcX+td, self.srcY+td, outline="white", fill=SELECTED_COLOR)
        self.destDot = self.canvas.create_rectangle(self.destX-td, self.destY-td, self.destX+td, self.destY+td, outline="white", fill=SELECTED_COLOR)
        self.handleDot = self.canvas.create_rectangle(self.handleX-td, self.handleY-td, self.handleX+td, self.handleY+td, outline="white", fill=SELECTED_COLOR)

    def _getText(self):
        if self.time >= 0:
            text = "after " + str(self.time)
        else:
            text = self.event
        if self.history == 1:
            text = text + " [H]"
        return text

    def _deleteItems(self):
        self.canvas.delete(self.arrow)
	self.canvas.delete(self.label)
	if self.selected:
	    self._deleteDots()

    def _deleteDots(self):
        self.canvas.delete(self.srcDot)
        self.canvas.delete(self.destDot)
        self.canvas.delete(self.handleDot)

    def _bindEvents(self):
        self.canvas.tag_bind(self.arrow, "<Button-1>", self.onArrowButton1)
        self.canvas.tag_bind(self.arrow, "<Button-3>", self.onButton3)
        self.canvas.tag_bind(self.arrow, "<Double-Button-1>", self.onDoubleButton1)
        self.canvas.tag_bind(self.arrow, "<ButtonRelease-1>", self.onButtonRelease1)
        self.canvas.tag_bind(self.label, "<Button-1>", self.onArrowButton1)
        self.canvas.tag_bind(self.label, "<Button-3>", self.onButton3)
        self.canvas.tag_bind(self.label, "<Double-Button-1>", self.onDoubleButton1)
        self.canvas.tag_bind(self.label, "<ButtonRelease-1>", self.onButtonRelease1)
	if self.selected:
            self._bindDots()
    
    def _bindDots(self):
        self.canvas.tag_bind(self.srcDot, "<Button-1>", self.onSrcButton1)
        self.canvas.tag_bind(self.destDot, "<Button-1>", self.onDestButton1)
        self.canvas.tag_bind(self.handleDot, "<Button-1>", self.onHandleButton1)
        self.canvas.tag_bind(self.srcDot, "<Double-Button-1>", self.onDoubleButton1)
        self.canvas.tag_bind(self.destDot, "<Double-Button-1>", self.onDoubleButton1)
        self.canvas.tag_bind(self.handleDot, "<Double-Button-1>", self.onDoubleButton1)
        self.canvas.tag_bind(self.srcDot, "<Button-3>", self.onButton3)
        self.canvas.tag_bind(self.destDot, "<Button-3>", self.onButton3)
        self.canvas.tag_bind(self.handleDot, "<Button-3>", self.onButton3)
        self.canvas.tag_bind(self.srcDot, "<B1-Motion>", self.onSrcButtonMotion1)
        self.canvas.tag_bind(self.destDot, "<B1-Motion>", self.onDestButtonMotion1)
        self.canvas.tag_bind(self.handleDot, "<B1-Motion>", self.onHandleButtonMotion1)
        self.canvas.tag_bind(self.srcDot, "<ButtonRelease-1>", self.onButtonRelease1)
        self.canvas.tag_bind(self.destDot, "<ButtonRelease-1>", self.onButtonRelease1)
        self.canvas.tag_bind(self.handleDot, "<ButtonRelease-1>", self.onButtonRelease1)

    def onArrowButton1(self, event):
        self.handler.onTransitionArrowButton1(self, event)

    def onSrcButton1(self, event):
        self.handler.onTransitionSrcButton1(self, event)

    def onDestButton1(self, event):
        self.handler.onTransitionDestButton1(self, event)

    def onHandleButton1(self, event):
        self.handler.onTransitionHandleButton1(self, event)

    def onDoubleButton1(self, event):
        self.handler.onTransitionDoubleButton1(self, event)

    def onButton3(self, event):
        self.handler.onTransitionButton3(self, event)

    def onSrcButtonMotion1(self, event):
        self.handler.onTransitionSrcButtonMotion1(self, event)

    def onDestButtonMotion1(self, event):
        self.handler.onTransitionDestButtonMotion1(self, event)

    def onHandleButtonMotion1(self, event):
        self.handler.onTransitionHandleButtonMotion1(self, event)

    def onButtonRelease1(self, event):
        self.handler.onTransitionButtonRelease1(self, event)









