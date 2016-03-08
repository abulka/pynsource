# Statechart.py
# statechart class
import pickle
from Globals import *
from State import State
from Transition import Transition

class Statechart:
    def __init__(self, handler):
        self.canvas = None
	self.handler = handler
	self.states = []
	self.transitions = []
	self.initCode = ""
	self.interactCode = ""
        self.finalCode = ""
	self.selectedStates = []
	self.selectedSeparators = []
	self.selectedTransitions = []
	self.isValid = 1
	self.modified = 0
        self.filename = ""

    def getFilename(self):
        return self.filename

    def setFilename(self, filename):
        self.filename = filename

    def setCanvas(self, canvas):
        self.canvas = canvas
	for state in self.states:
            state.setCanvas(canvas)
        for transition in self.transitions:
            transition.setCanvas(canvas)

    def setHandler(self, handler):
        self.handler = handler
	for state in self.states:
            state.setHandler(handler)
        for transition in self.transitions:
            transition.setHandler(handler)

    def exportToSVM(self, filename):
        file = open(filename,"w")
        if self.initCode != "":
            file.write("INITIALIZER:\n")
            lines = self.initCode.split('\n')
            for line in lines:
                file.write("  " + line + "\n")
        if self.interactCode != "":
            file.write("INTERACTOR:\n")
            lines = self.interactCode.split('\n')
            for line in lines:
                file.write("  " + line + "\n")
        if self.finalCode != "":
            file.write("FINALIZER:\n")
            lines = self.finalCode.split('\n')
            for line in lines:
                file.write("  " + line + "\n")
        file.write("STATECHART:\n")
        for s in self.states:
            s.writeHierarchySVM(file,"  ")
        for s in self.states:
            s.writeEnterExitSVM(file)
        for t in self.transitions:
            file.write("TRANSITION:")
            if t.getHistory() == 1:
                file.write(" [HS]")
            file.write("\n")
            file.write("  S: " + t.getSrc().getFullName() + "\n")
            file.write("  N: " + t.getDest().getFullName() + "\n")
            time = t.getTime()
            if time >= 0:
                file.write("  T: " + str(time) + "\n")
            else:
                file.write("  E: " + t.getEvent() + "\n")
            code = t.getCode()
            if code != "":
                file.write("  O: " + t.getCode() + "\n")
        file.close()

    def getModified(self):
        return self.modified

    def setModified(self, mod):
        self.modified = mod
        self.handler.onStatechartModified(mod)

    def getInitCode(self):
        return self.initCode

    def setInitCode(self, code):
        self.initCode = code

    def getInteractCode(self):
        return self.interactCode

    def setInteractCode(self, code):
        self.interactCode = code

    def getFinalCode(self):
        return self.finalCode

    def setFinalCode(self, code):
        self.finalCode = code

    def getStateAtXY(self,x,y):
        for state in self.states:
            s = state.getStateAtXY(x,y)
            if s != None:
                return s
        return None

    def addState(self, x, y, parent):
	# if top level state
	if parent == None:
            for s in self.states:
                if s.intersectStateAt(x,y,x+MIN_WIDTH,y+MIN_HEIGHT):
                    return None
            if len(self.states) == 0:
                default = 1
            else:
                default = 0
            state = State(x,y,self._getFreeName(x,y),None,self.handler,[],[],ds=default)
            self.states.append(state)
            return state
	# else ask parent to add it
        else:
            state = parent.addStateAt(x,y)
            return state

    def selectState(self, state):
	if self.isSelectedState(state):
            return
        state.lift()
        for t in self.transitions:
            t.lift()
        self.selectedStates.append(state)
        state.setBorderColor(SELECTED_COLOR)

    def getSelectedStates(self):
        return self.selectedStates

    def isSelectedState(self, state):
        for s in self.selectedStates:
            if state == s:
                return 1
	return 0

    def hasLegalPosition(self,state):
        for s in self.states:
            if s != state and s.intersectStateAt(state.x0, state.y0,state.x1,state.y1):
                return 0
        return 1

    def addTransition(self, src, dest):
	if self._canAddTransition(src, dest):
            newTransition = Transition(src,dest,self.handler)
            self.transitions.append(newTransition)
            return newTransition
        else:
            return None

    def _canAddTransition(self, src, dest):
        return 1

    def selectTransition(self, transition):
	transition.lift()
        self.selectedTransitions.append(transition)
        transition.select()

    def getSelectedTransitions(self):
        return self.selectedTransitions

    def isSelectedTransition(self, transition):
        for t in self.selectedTransitions:
            if transition == t:
                return 1
	return 0

    def selectSeparator(self, separator):
        self.selectedSeparators.append(separator)
        separator.setColor(SELECTED_COLOR)
	separator.lift()
	
    def getSelectedSeparators(self):
        return self.selectedSeparators

    def deselect(self):
	for state in self.selectedStates:
	    state.setBorderColor("black")
	    self.selectedStates = []
	for transition in self.selectedTransitions:
	    transition.deselect()
	    self.selectedTransitions = []
	for separator in self.selectedSeparators:
	    separator.setColor("black")
            self.selectedSeparators = []

    def deleteSelected(self):
	for transition in self.selectedTransitions:
            self.transitions.remove(transition)
	    transition.setCanvas(None)
	for separator in self.selectedSeparators:
	    separator.state.removeSeparator(separator)
	for s in self.selectedStates:
	    trans = self.transitions[:]
            for t in trans:
                if s.belongsToThis(t.getSrc()) or s.belongsToThis(t.getDest()):
                    self.transitions.remove(t)
                    t.setCanvas(None)
	    if s.parent != None:
                s.parent.removeChild(s)
            else:
                self.states.remove(s)
	        s.setCanvas(None)
        self.selectedSeparators = []
        self.selectedStates = []
        self.selectedTransitions = []
        self.setModified(1)

    def translateTransitionHandles(self,state,dx,dy):
        for t in self.transitions:
            src = t.getSrc()
            dest = t.getDest()
            if state.isStateMine(src) and state.isStateMine(dest):
                t.translateHandleDot(dx, dy)

    def updateTransitions(self):
        for t in self.transitions:
            t.updateDisplay()

    def disableTransitionHistory(self, state):
        for t in self.transitions:
            if t.getDest() == state:
                t.setHistory(0)

    def _getFreeName(self,x,y):
	i = -1
	taken = 1
        while taken:
	    i = i + 1
	    taken = 0
            name = "s" + str(i)
	    for s in self.states:
	        if s.name.get() == name:
                    taken = 1
        return name

    def isFreeName(self, parentState,name):
        if parentState == None: # top state
            for s in self.states:
                if s.getName() == name:
                    return 0
            return 1
        else:
            for s in parentState.states:
                if s.getName() == name:
                    return 0
            return 1

    def setAsDefault(self, state):
	if state.parent == None:
            for s in self.states:
                s.setDS(0)
            state.setDS(1)
	    return
	else:
            state.parent.setChildAsDefault(state)
	    return
        self.setModified(1)









