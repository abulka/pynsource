from Tkinter import *
from Globals import *
from Handler import Handler
from Separator import Separator

class Adder(Handler):
    def __init__(self, parent):
	self.parent = parent

    def setGUI(self, GUI):
        self.GUI = GUI

    def setStatechart(self, statechart):
        self.statechart = statechart


    # FORWARD STATE/TRANSITION EDITION EVENTS TO PARENT
    def onAddState(self):
	self.interrupt()
        return self.parent.onAddState()

    def onAddSeparator(self):
	self.interrupt()
        return self.parent.onAddSeparator()

    def onAddTransition(self):
	self.interrupt()
        return self.parent.onAddTransition()
 
    def onAddTransitionTo(self):
	self.interrupt()
        return self.parent.onAddTransitionTo()

    def onDelete(self):
	self.interrupt()
        return self.parent.onDelete()

    def onEditState(self):
	self.interrupt()
        return self.parent.onEditState()

    def onEditTransition(self):
	self.interrupt()
        return self.parent.onEditTransition()

    def onSetStateAsDefault(self):
	self.interrupt()
        return self.parent.onSetStateAsDefault()

    # STATE EVENTS
    def onStateButton3(self, state, event):
        self.interrupt()
        return self.parent
    
    # OTHER METHODS
    def interrupt(self):
        pass    



class StateAdder(Adder):
    def __init__(self, parent):
        Adder.__init__(self, parent)
	self.stateShadow = StateShadow()

    def onAddState(self):
	self.statechart.deselect()
        self.GUI.workspace.setCursorNormal()
	if self.GUI.workspace.isCursorInCanvas():
            x,y = self.GUI.workspace.getEnterCanvasCoords()
	    self.stateShadow.setCanvas(self.GUI.getCanvas(), x, y)
	return self

    def _addState(self, x, y, parent):
	x0 = x - MIN_WIDTH/2
	y0 = y - MIN_HEIGHT/2
	state = self.statechart.addState(x0,y0,parent)
	if state == None:
	    return
        state.setCanvas(self.GUI.getCanvas())
	self.statechart.selectState(state)
        self.statechart.setModified(1)

    def interrupt(self):
        self.stateShadow.setCanvas(None, 0, 0)


    # CANVAS EVENTS
    def onCanvasEnter(self, event):
	self.stateShadow.setCanvas(self.GUI.getCanvas(), event.x, event.y)
	return self

    def onCanvasLeave(self, event):
	self.stateShadow.setCanvas(None, event.x, event.y)
	return self

    def onCanvasButton(self, event):
	self.stateShadow.setCanvas(None, event.x, event.y)
	if event.num == 1: # left click
	    self._addState(event.x, event.y, None)
        else:
            self.interrupt()
        return self.parent

    def onCanvasMotion(self, event):
	self.stateShadow.updateDisplay(event.x, event.y)
        return self

    # STATE EVENTS
    def onStateButton1(self, state, event):
	self.stateShadow.setCanvas(None, event.x, event.y)
        self._addState(event.x, event.y, state)
        return self.parent

    def onStateButton3(self, state, event):
        self.interrupt()
        return self.parent

    # STATE BORDER EVENTS
    def onStateBorderButton1(self, state, border, event):
        self.interrupt()
        return self.parent

    def onStateBorderButton3(self, state, border, event):
        self.interrupt()
        return self.parent

    # SEPARATOR EVENTS
    def onSeparatorButton1(self, sep, state, event):
        self.interrupt()
        return self.parent

    def onSeparatorButton3(self, sep, state, event):
        self.interrupt()
        return self.parent

    # TRANSITION EVENTS
    def onTransitionArrowButton1(self, transition, event):
	self.stateShadow.setCanvas(None, event.x, event.y)
        self._addState(event.x, event.y, None)
        return self.parent



class StateShadow:
    WIDTH = 3
    def __init__(self):
	self.canvas = None

    def setCanvas(self, canvas, x, y):
	self.x = x
	self.y = y
        if self.canvas == None and canvas != None:
            self.canvas = canvas
            self._createItems(x, y)
        elif self.canvas != None and canvas == None:
            self._deleteItems()
            self.canvas = None

    def updateDisplay(self, x, y):
        if self.canvas == None:
            return
	x0 = x - MIN_WIDTH/2
	x1 = x + MIN_WIDTH/2
	y0 = y - MIN_HEIGHT/2
	y1 = y + MIN_HEIGHT/2
 	r = RADIUS
        self.canvas.coords(self.N, x0+r-1,y0,x1-r+1,y0)
        self.canvas.coords(self.W, x0, y0+r-1, x0, y1-r+1)
        self.canvas.coords(self.E, x1,y0+r-1,x1,y1-r+1)
        self.canvas.coords(self.S, x0+r-1,y1,x1-r+1,y1)
        xy = x0, y0, x0+r*2, y0+r*2
        self.canvas.coords(self.NW, xy)
        xy = x1-r*2, y0, x1, y0+r*2
        self.canvas.coords(self.NE, xy)
        xy = x0, y1-r*2, x0+r*2, y1
        self.canvas.coords(self.SW, xy)
        xy = x1-r*2, y1-r*2, x1, y1
        self.canvas.coords(self.SE, xy)

    def _createItems(self, x, y):
	x0 = x - MIN_WIDTH/2
	x1 = x + MIN_WIDTH/2
	y0 = y - MIN_HEIGHT/2
	y1 = y + MIN_HEIGHT/2
 	r = RADIUS
        self.N = self.canvas.create_line(x0+r-1,y0,x1-r+1,y0, width=StateShadow.WIDTH, fill=SHADOW_COLOR)
        self.W = self.canvas.create_line(x0, y0+r-1, x0, y1-r+1, width=StateShadow.WIDTH, fill=SHADOW_COLOR)
        self.E = self.canvas.create_line(x1,y0+r-1,x1,y1-r+1, width=StateShadow.WIDTH, fill=SHADOW_COLOR)
        self.S = self.canvas.create_line(x0+r-1,y1,x1-r+1,y1, width=StateShadow.WIDTH, fill=SHADOW_COLOR)
        xy = x0, y0, x0+r*2, y0+r*2
        self.NW = self.canvas.create_arc(xy, start=90, extent=90, style=ARC, width=StateShadow.WIDTH, outline=SHADOW_COLOR)
        xy = x1-r*2, y0, x1, y0+r*2
        self.NE = self.canvas.create_arc(xy, start=0, extent=90, style=ARC, width=StateShadow.WIDTH, outline=SHADOW_COLOR)
        xy = x0, y1-r*2, x0+r*2, y1
        self.SW = self.canvas.create_arc(xy, start=180, extent=90, style=ARC, width=StateShadow.WIDTH, outline=SHADOW_COLOR)
        xy = x1-r*2, y1-r*2, x1, y1
        self.SE = self.canvas.create_arc(xy, start=270, extent=90, style=ARC, width=StateShadow.WIDTH, outline=SHADOW_COLOR)
        self.items = [self.N, self.S, self.E, self.W, self.NW, self.NE, self.SW, self.SE]
        self.edges = [self.N, self.S, self.E, self.W]
        self.corners = [self.NW, self.NE, self.SW, self.SE]

    def _deleteItems(self):
        for item in self.items:
            self.canvas.delete(item)
        self.edges = None
        self.corners = None




############################SEPARATOR ADDER#################################

class SeparatorAdder(Adder):
    def __init__(self, parent):
        Adder.__init__(self, parent)
	self.separatorShadow = SeparatorShadow()

    def onAddSeparator(self):
	self.statechart.deselect()
        self.GUI.workspace.setCursorNormal()
	if self.GUI.workspace.isCursorInCanvas():
            x,y = self.GUI.workspace.getEnterCanvasCoords()
            state = self.statechart.getStateAtXY(x,y)
	    self.separatorShadow.setCanvas(self.GUI.getCanvas(), x, y, state)
	return self

    def _addSeparator(self, y, state):
        separator = state.addSeparator(y)
	if separator == None:
	    return
        separator.setCanvas(self.GUI.getCanvas())
	self.statechart.selectSeparator(separator)
        self.statechart.setModified(1)

    def interrupt(self):
        self.separatorShadow.setCanvas(None, 0, 0, None)


    # CANVAS EVENTS
    def onCanvasEnter(self, event):
	state = self.statechart.getStateAtXY(event.x,event.y)
	self.separatorShadow.setCanvas(self.GUI.getCanvas(), event.x, event.y, state)
	return self

    def onCanvasLeave(self, event):
	self.separatorShadow.setCanvas(None, event.x, event.y,None)
	return self

    def onCanvasButton(self, event):
	self.separatorShadow.setCanvas(None, event.x, event.y, None)
	if event.num == 3:
            return self.parent
	state = self.statechart.getStateAtXY(event.x,event.y)
	if state == None:
            return self.parent
        self._addSeparator(event.y, state)
        return self.parent

    def onCanvasMotion(self, event):
        state = self.statechart.getStateAtXY(event.x,event.y)
	self.separatorShadow.updateDisplay(event.x, event.y, state)
        return self




class SeparatorShadow:
    def __init__(self):
	self.canvas = None

    def setCanvas(self, canvas, x, y, state):
	self.x = x
	self.y = y
        if self.canvas == None and canvas != None:
            self.canvas = canvas
            self._createItems(x, y, state)
        elif self.canvas != None and canvas == None:
            self._deleteItems()
            self.canvas = None

    def updateDisplay(self, x, y, state):
        if self.canvas == None:
            return
	x0,x1 = self._getX0X1(x,y,state)
        self.canvas.coords(self.line,x0,y,x1,y)

    def _createItems(self, x, y, state):
	x0,x1 = self._getX0X1(x,y,state)
        self.line = self.canvas.create_line(x0,y,x1,y, fill=SHADOW_COLOR,stipple=SEPARATOR_BITMAP, width=SEPARATOR_WIDTH)
        self.items = [self.line]

    def _deleteItems(self):
        for item in self.items:
            self.canvas.delete(item)

    def _getX0X1(self,x,y,state):
        if state != None:
            sx0,sy0,sx1,sy1,sr = state.getCoords()
            if y > sy0 + SEPARATOR_PAD and y < sy1 - SEPARATOR_PAD:
                return sx0, sx1
        return x - MIN_WIDTH/2, x + MIN_WIDTH/2




##########################TRANSITION ADDER#################################

class TransitionAdder(Adder):
    def __init__(self, parent):
        Adder.__init__(self, parent)
	self.transitionShadow = TransitionShadow()

    def onAddTransition(self):
	self.src = None
	self.statechart.deselect()
        self.GUI.workspace.setCursorNormal()
	if self.GUI.workspace.isCursorInCanvas():
            x,y = self.GUI.workspace.getEnterCanvasCoords()
	    self.transitionShadow.setCanvas(self.GUI.getCanvas(), x, y, self.src)
	return self

    def onAddTransitionTo(self):
	states = self.statechart.getSelectedStates()
	self.src = states[0]
	self.statechart.deselect()
        self.GUI.workspace.setCursorNormal()
	if self.GUI.workspace.isCursorInCanvas():
            x,y = self.GUI.workspace.getEnterCanvasCoords()
	    self.transitionShadow.setCanvas(self.GUI.getCanvas(), x, y, self.src)
	return self

    def _addTransition(self, src, dest):
        transition = self.statechart.addTransition(src,dest)
        if transition == None:
	    return
        transition.setCanvas(self.GUI.getCanvas())
	self.statechart.selectTransition(transition)
        self.statechart.setModified(1)

    def interrupt(self):
        self.transitionShadow.setCanvas(None, 0, 0, None)


    # CANVAS EVENTS
    def onCanvasEnter(self, event):
	self.transitionShadow.setCanvas(self.GUI.getCanvas(), event.x, event.y, self.src)
	return self

    def onCanvasLeave(self, event):
	self.transitionShadow.setCanvas(None, event.x, event.y, None)
	return self

    def onCanvasButton(self, event):
	# button 3
	if event.num == 3:
            self.interrupt()
            return self.parent
        # button 1
	if self.src == None: # getting src state
            self.src = self.statechart.getStateAtXY(event.x,event.y)
	    if self.src == None:
	        self.interrupt()
                return self.parent
            self.transitionShadow.updateDisplay(event.x,event.y,self.src)
            return self
        else: # getting dest
            dest = self.statechart.getStateAtXY(event.x,event.y)
            self.interrupt()
	    if dest == None:
                return self.parent
            self._addTransition(self.src,dest)
	    return self.parent

    def onCanvasMotion(self, event):
	self.transitionShadow.updateDisplay(event.x, event.y, self.src)
        return self




class TransitionShadow:
    def __init__(self):
	self.canvas = None

    def setCanvas(self, canvas, x, y, src):
        if self.canvas == None and canvas != None:
            self.canvas = canvas
            self._createItems(x, y, src)
        elif self.canvas != None and canvas == None:
            self._deleteItems()
            self.canvas = None

    def updateDisplay(self, x, y, src):
	x0,y0,x1,y1 = self._getCoords(x,y,src)
        self.canvas.coords(self.arrow,x0,y0,x1,y1)
	td = TRANSITION_DOT
        self.canvas.coords(self.srcDot, x0-td, y0-td, x0+td, y0+td)
        self.canvas.coords(self.destDot, x1-td, y1-td, x1+td,y1+td)

    def _createItems(self, x, y, src):
	x0,y0,x1,y1 = self._getCoords(x,y,src)
        self.arrow = self.canvas.create_line(x0,y0,x1,y1,arrow="last", width=TRANSITION_WIDTH,fill=SHADOW_COLOR)
	td = TRANSITION_DOT
        self.srcDot = self.canvas.create_rectangle(x0-td, y0-td, x0+td, y0+td, outline=SHADOW_COLOR, fill=SHADOW_COLOR)
        self.destDot = self.canvas.create_rectangle(x1-td, y1-td, x1+td,y1+td, outline=SHADOW_COLOR, fill=SHADOW_COLOR)
        self.items = [self.arrow, self.srcDot, self.destDot]

    def _deleteItems(self):
        for item in self.items:
            self.canvas.delete(item)

    def _getCoords(self,x,y,src):
        if src != None:
            x0,y0 = src.getBorderPoint(x,y)
	    x1,y1 = x,y
	else:
            x0,y0 = x-5,y+5
	    x1,y1 = x+5,y-5
	return x0,y0,x1,y1









































































