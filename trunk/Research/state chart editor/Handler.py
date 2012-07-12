# default event handler class
# always returns itself
# The real event handlers inherit from this class

class Handler:
    def __init__(self):
        pass

    def setGUI(self, GUI):
        self.GUI = GUI

    def setStatechart(self, statechart):
        self.statechart = statechart

    # FILE EVENTS
    def onNew(self):
	return self

    def onOpen(self):
        return self

    def onSave(self):
        return self

    def onSaveAs(self):
        return self

    def onExportToPostscript(self):
        return self

    def onExportToSVM(self):
        return self

    def onQuit(self):
        return self

    # CODE EDITION EVENTS
    def onDelete(self):
        return self

    def onEditInitCode(self):
        return self

    def onEditInteractCode(self):
        return self

    def onEditFinalCode(self):
        return self

    # STATECHART MODIFIED
    def onStatechartModified(self, modified):
        return self

    # STATE/TRANSITION EDITION EVENTS
    def onAddState(self):
        return self

    def onAddSeparator(self):
        return self

    def onAddTransition(self):
        return self
 
    def onAddTransitionTo(self):
        return self

    def onEditState(self):
        return self

    def onEditTransition(self):
        return self

    def onSetStateAsDefault(self):
        return self

    # CANVAS EVENTS
    def onCanvasEnter(self, event):
	return self

    def onCanvasLeave(self, event):
	return self

    def onCanvasButton(self, event):
        return self

    def onCanvasDoubleButton(self, event):
        return self

    def onCanvasMotion(self, event):
        return self

    def onCanvasShiftMotion(self, event):
        return self

    def onCanvasButtonMotion(self, event):
        return self

    def onCanvasShiftButtonMotion(self, event):
        return self

    def onCanvasButtonRelease(self, event):
        return self

    # STATE EVENTS
    def onStateButton1(self, state, event):
        return self
    
    def onStateButton3(self, state, event):
        return self
    
    def onStateDoubleButton1(self, state, event):
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
        return self
    
    def onStateBorderLeave(self, state, border, event):
        return self
    
    def onStateBorderButton1(self, state, border, event):
        return self
    
    def onStateBorderButtonMotion1(self, state, border, event):
        return self
        
    def onStateBorderButtonRelease1(self, state, border, event): 
        return self

    # SEPARATOR EVENTS
    def onSeparatorEnter(self, sep, state, event):
        return self

    def onSeparatorLeave(self, sep, state, event):
        return self
        
    def onSeparatorButton1(self, sep, state, event):
        return self

    def onSeparatorButton3(self, sep, state, event):
        return self

    def onSeparatorButtonMotion1(self, sep, state, event):
        return self

    def onSeparatorButtonMotion3(self, sep, state, event):
        return self

    def onSeparatorButtonRelease1(self, sep, state, event):
        return self

    def onSeparatorButtonRelease3(self, sep, state, event):
        return self


    # TRANSITION EVENTS
    def onTransitionArrowButton1(self, transition, event):
	return self

    def onTransitionSrcButton1(self, transition, event):
	return self

    def onTransitionDestButton1(self, transition, event):
	return self

    def onTransitionHandleButton1(self, transition, event):
	return self

    def onTransitionDoubleButton1(self, transition, event):
        return self
 
    def onTransitionButton3(self, transition, event):
	return self

    def onTransitionSrcButtonMotion1(self, transition, event):
	return self

    def onTransitionDestButtonMotion1(self, transition, event):
	return self

    def onTransitionHandleButtonMotion1(self, transition, event):
	return self

    def onTransitionButtonRelease1(self, transition, event):
	return self





