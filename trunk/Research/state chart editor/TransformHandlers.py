# default event handler class
# always returns itself
# The real event handlers inherit from this class
from Handler import Handler

class StateTranslater(Handler):
    def __init__(self, parent):
        self.parent = parent

    def setGUI(self, GUI):
        self.GUI = GUI

    def setStatechart(self, statechart):
        self.statechart = statechart

    # STATE EVENTS
    def onStateButton1(self, state, event):
	self.statechart.isValid = 0
        self.x = event.x
        self.y = event.y
        state.mark() # mark position, just in case
        return self

    def onStateButtonMotion1(self, state, event):
        dx = event.x - self.x
        dy = event.y - self.y
	selectedStates = self.statechart.getSelectedStates()
	for s in selectedStates:
            s.translate(dx, dy)
        self.statechart.translateTransitionHandles(state,dx,dy)
	self.statechart.updateTransitions()
        self.x = event.x
        self.y = event.y
        return self

    def onStateButtonRelease1(self, state, event):
	illegal = 0
        if state.parent != None:
            if not state.parent.hasLegalPosition(state):
		illegal = 1
        else: # top level state
            if not self.statechart.hasLegalPosition(state):
		illegal = 1
	if illegal:
            dx,dy = state.backToMark() # go back to initial position
            self.statechart.translateTransitionHandles(state,dx,dy)
            self.statechart.updateTransitions()
        else:
            self.statechart.setModified(1)
	self.statechart.isValid = 1
        # done
        return self.parent


class SeparatorTranslater(Handler):
    def __init__(self, parent):
        self.parent = parent

    def setGUI(self, GUI):
        self.GUI = GUI

    def setStatechart(self, statechart):
        self.statechart = statechart

    # SEPARATOR EVENTS
    def onSeparatorButton1(self, separator, state, event):
	self.statechart.isValid = 0
	self._setOffset(separator, event)
	separator.setMark()
        return self

    def onSeparatorButtonMotion1(self, sep, state, event):
	selectedSeparators = self.statechart.getSelectedSeparators()
        selectedSeparators[0].setY(event.y+self.offset)
        return self

    def onSeparatorButtonRelease1(self, sep, state, event):
        y = sep.getY()
        illegal = 0
        for s in sep.state.states:
            if y > s.y0 and y < s.y1:
                illegal = 1
        if illegal:
            sep.backToMark()
        else:
            self.statechart.setModified(1)
	self.statechart.isValid = 1
        # done
        return self.parent

    def _setOffset(self, sep, event):
        self.offset = sep.getY() - event.y


class StateScaler(Handler):
    def __init__(self, parent):
	self.parent = parent

    def setGUI(self, GUI):
        self.GUI = GUI

    def setStatechart(self, statechart):
        self.statechart = statechart

    # STATE BORDER EVENTS
    def onStateBorderButton1(self, state, border, event):
	self.statechart.isValid = 0
	self._setOffset(state, border, event.x, event.y)
	state.mark()
        return self

    def onStateBorderButtonMotion1(self, state, border, event):
        state.scale(border, event.x + self.x_offset, event.y + self.y_offset)
	self.statechart.updateTransitions()
        return self

    def onStateBorderButtonRelease1(self, state, border, event):
	illegal = 0
        if state.parent != None:
            if not state.parent.hasLegalPosition(state):
		illegal = 1
        else: # top level state
            if not self.statechart.hasLegalPosition(state):
		illegal = 1
	if illegal:
            state.backToMark() # go back to initial position
            self.statechart.updateTransitions()
        else:
            self.statechart.setModified(1)
	self.statechart.isValid = 1
        # done
        return self.parent

    def _setOffset(self, state, border, x, y):
	x0, y0, x1, y1, r = state.getCoords()
	if border == "NW":
            self.x_offset = x0 - x
	    self.y_offset = y0 - y
	elif border == "NE":
            self.x_offset = x1 - x
	    self.y_offset = y0 - y
	elif border == "SW":
            self.x_offset = x0 - x
	    self.y_offset = y1 - y
	elif border == "SE":
            self.x_offset = x1 - x
	    self.y_offset = y1 - y
	elif border == "N":
            self.x_offset = 0
	    self.y_offset = y0 - y
	elif border == "S":
            self.x_offset = 0
	    self.y_offset = y1 - y
	elif border == "E":
            self.x_offset = x1 - x
	    self.y_offset = 0
	elif border == "W":
            self.x_offset = x0 - x
	    self.y_offset = 0


class TransitionTranslater(Handler):
    def __init__(self, parent):
        self.parent = parent

    def setGUI(self, GUI):
        self.GUI = GUI

    def setStatechart(self, statechart):
        self.statechart = statechart

    def onTransitionSrcButton1(self, transition, event):
	self.what = "src"
	self.statechart.isValid = 0
        self.x = event.x
        self.y = event.y
        return self

    def onTransitionDestButton1(self, transition, event):
	self.what = "dest"
	self.statechart.isValid = 0
        self.x = event.x
        self.y = event.y
        return self

    def onTransitionHandleButton1(self, transition, event):
	self.what = "handle"
	self.statechart.isValid = 0
        self.x = event.x
        self.y = event.y
        return self

    def onTransitionSrcButtonMotion1(self, transition, event):
        dx = event.x - self.x
        dy = event.y - self.y
        transition.translateSrcDot(dx, dy)
        self.x = event.x
        self.y = event.y
        return self

    def onTransitionDestButtonMotion1(self, transition, event):
        dx = event.x - self.x
        dy = event.y - self.y
        transition.translateDestDot(dx, dy)
        self.x = event.x
        self.y = event.y
	return self

    def onTransitionHandleButtonMotion1(self, transition, event):
        dx = event.x - self.x
        dy = event.y - self.y
        transition.translateHandleDot(dx, dy)
        transition.updateDisplay()
        self.x = event.x
        self.y = event.y
	return self

    def onTransitionButtonRelease1(self, transition, event):
        self.statechart.setModified(1)
	if self.what == "src":
            newSrc = self.statechart.getStateAtXY(event.x, event.y)
            if newSrc != None:
                transition.setSrc(newSrc)
	elif self.what == "dest":
            newDest = self.statechart.getStateAtXY(event.x, event.y)
            if newDest != None:
                transition.setDest(newDest)
        transition.updateDisplay()
        self.statechart.isValid = 1
        # done
        return self.parent















