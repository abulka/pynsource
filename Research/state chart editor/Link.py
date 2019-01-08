from Handler import Handler
from TransformHandlers import StateTranslater, SeparatorTranslater, StateScaler, TransitionTranslater
from Adders import StateAdder, SeparatorAdder, TransitionAdder

class Link(Handler):
    def __init__(self):
	self.stateAdder = StateAdder(self)
	self.stateTranslater = StateTranslater(self)
	self.stateScaler = StateScaler(self)
	self.separatorAdder = SeparatorAdder(self)
	self.separatorTranslater = SeparatorTranslater(self)
	self.transitionAdder = TransitionAdder(self)
        self.transitionTranslater = TransitionTranslater(self)

    def setGUI(self, GUI):
        self.GUI = GUI
	self.stateAdder.setGUI(GUI)
	self.stateTranslater.setGUI(GUI)
	self.stateScaler.setGUI(GUI)
	self.separatorAdder.setGUI(GUI)
        self.separatorTranslater.setGUI(GUI)
        self.transitionAdder.setGUI(GUI)
        self.transitionTranslater.setGUI(GUI)

    def setStatechart(self, statechart):
        self.statechart = statechart
	self.stateAdder.setStatechart(statechart)
	self.stateTranslater.setStatechart(statechart)
	self.stateScaler.setStatechart(statechart)
	self.separatorAdder.setStatechart(statechart)
	self.separatorTranslater.setStatechart(statechart)
        self.transitionAdder.setStatechart(statechart)
        self.transitionTranslater.setStatechart(statechart)


    #
    # STATE/TRANSITION EDITION EVENTS
    #
    def onAddState(self):
	return self.stateAdder.onAddState()

    def onAddSeparator(self):
	return self.separatorAdder.onAddSeparator()

    def onAddTransition(self):
        return self.transitionAdder.onAddTransition()

    def onAddTransitionTo(self):
        return self.transitionAdder.onAddTransitionTo()

    def onDelete(self):
        self.statechart.deleteSelected()
        return self

    def onEditState(self):
        states = self.statechart.getSelectedStates()
	self.GUI.editState(states[0], self.statechart)
        return self

    def onEditTransition(self):
        transitions = self.statechart.getSelectedTransitions()
	self.GUI.editTransition(transitions[0], self.statechart)
        return self

    def onSetStateAsDefault(self):
        states = self.statechart.getSelectedStates()
	self.statechart.setAsDefault(states[0])
        return self


    # CANVAS EVENTS
    def onCanvasEnter(self, event):
	return self

    def onCanvasLeave(self, event):
	return self

    def onCanvasButton(self, event):
	self.statechart.deselect()
	if event.num == 3: # right click
            if len(self.statechart.states) == 0:
                self.GUI.disable("addTransition")
                self.GUI.disable("addSeparator")
            self.GUI.showCanvasPopup(event.x_root, event.y_root)
            self.GUI.enable("addTransition")
            self.GUI.enable("addSeparator")
        return self

    def onCanvasDoubleButton(self, event):
        return self

    def onCanvasMotion(self, event):
        return self

    def onCanvasShiftMotion(self, event):
        print("onCanvasShiftMotion")
        return self

    def onCanvasButtonMotion(self, event):
        return self

    def onCanvasShiftButtonMotion(self, event):
        return self

    def onCanvasButtonRelease(self, event):
        return self

    # STATE EVENTS
    def onStateButton1(self, state, event):
	# if state is not selected yet
	if self.statechart.isSelectedState(state) == 0:
	    # deselect all
            self.statechart.deselect()
            # and select this state
            self.statechart.selectState(state)
	return self.stateTranslater.onStateButton1(state, event)

    def onStateButton3(self, state, event):
	self.statechart.deselect()
	self.statechart.selectState(state)
	if state.getDS():
            self.GUI.disable("setStateAsDefault")
            if state.parent != None:
                comp = state.parent.getComponentNumber(state)
                for s in state.parent.states:
                    if state.parent.getComponentNumber(s) == comp and s != state:
                        self.GUI.disable("delete")
            else:
                if len(self.statechart.states) > 1:
                    self.GUI.disable("delete")
	self.GUI.showStatePopup(event.x_root, event.y_root)
        self.GUI.enable("setStateAsDefault")
        self.GUI.enable("delete")
        return self

    def onStateDoubleButton1(self, state, event):
        # deselect all
        self.statechart.deselect()
        # and select this state
        self.statechart.selectState(state)
	self.GUI.editState(state, self.statechart)
        return self

    def onStateDoubleButton3(self, state, event):
        return self

    def onStateButtonMotion1(self, state, event):
        return self

    def onStateButtonMotion3(self, state, event):
        return self

    def onStateButtonRelease1(self, state, event):
        return self

    def onStateButtonRelease3(self, state, event):
        return self

    # STATE BORDER EVENTS
    def onStateBorderEnter(self, state, border, event):
	if border == "N" or border == "S":
		self.GUI.workspace.setCursorNS()
        elif border == "E" or border == "W":
		self.GUI.workspace.setCursorWE()
        elif border == "NE" or border == "SW":
		self.GUI.workspace.setCursorNE_SW()
        elif border == "NW" or border == "SE":
		self.GUI.workspace.setCursorNW_SE()
	return self
    
    def onStateBorderLeave(self, state, border, event):
	self.GUI.workspace.setCursorNormal()
        return self
    
    def onStateBorderButton1(self, state, border, event):
	self.statechart.deselect()
	self.statechart.selectState(state)
	return self.stateScaler.onStateBorderButton1(state, border, event)

    def onStateBorderButtonMotion1(self, state, border, event):
        return self
        
    def onStateBorderButtonRelease1(self, state, border, event):
        return self


    # SEPARATOR EVENTS
    def onSeparatorEnter(self, sep, state, event):
	self.GUI.workspace.setCursorNS()
        return self

    def onSeparatorLeave(self, sep, state, event):
	self.GUI.workspace.setCursorNormal()
        return self
        
    def onSeparatorButton1(self, sep, state, event):
        # deselect all
        self.statechart.deselect()
        # and select this separator
        self.statechart.selectSeparator(sep)
	return self.separatorTranslater.onSeparatorButton1(sep, state, event)

    def onSeparatorButton3(self, sep, state, event):
	self.statechart.deselect()
	self.statechart.selectSeparator(sep)
	self.GUI.showSeparatorPopup(event.x_root, event.y_root)
        return self



    # TRANSITION EVENTS
    def onTransitionArrowButton1(self, transition, event):
        # deselect all
        self.statechart.deselect()
        # and select this transition
        self.statechart.selectTransition(transition)
	return self

    def onTransitionSrcButton1(self, transition, event):
        return self.transitionTranslater.onTransitionSrcButton1(transition, event)

    def onTransitionDestButton1(self, transition, event):
        return self.transitionTranslater.onTransitionDestButton1(transition, event)

    def onTransitionHandleButton1(self, transition, event):
        return self.transitionTranslater.onTransitionHandleButton1(transition, event)

    def onTransitionDoubleButton1(self, transition, event):
        # deselect all
        self.statechart.deselect()
        # and select this transition
        self.statechart.selectTransition(transition)
	self.GUI.editTransition(transition, self.statechart)
        return self

    def onTransitionButton3(self, transition, event):
	self.statechart.deselect()
	self.statechart.selectTransition(transition)
	self.GUI.showTransitionPopup(event.x_root, event.y_root)
        return self















