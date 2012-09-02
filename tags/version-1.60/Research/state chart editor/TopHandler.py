from Handler import Handler
from Statechart import Statechart
from Link import Link
import pickle
class TopHandler(Handler):
    def __init__(self):
        self.link = Link()
	self.h = self.link

    def setGUI(self, GUI):
        self.GUI = GUI
	self.link.setGUI(GUI)

    def setStatechart(self, statechart):
        self.statechart = statechart
        self.link.setStatechart(statechart)

    # FILE EVENTS
    def onNew(self):
	if self.statechart.isValid == 0:
	    return # ignore event
        if self.canClose():
            self.statechart.setCanvas(None)
            self.setStatechart(Statechart(self.GUI.getStatechartHandler()))
            self.statechart.setModified(0)

    def onOpen(self):
	if self.statechart.isValid == 0:
	    return 0# ignore event
        filename = self.GUI.getStatechartFile()
        if filename != None:
            try:
                f = open(filename, "r")
            except:
                self.GUI.showError("Open","Cannot open " + filename)
                return 0
            try:
                statechart = pickle.load(f)
            except:
                self.GUI.showError("Open","Cannot open file:\nFormat not recognized")
                return 0
            if self.canClose():
                self.statechart.setCanvas(None)
                self.setStatechart(statechart)
                self.statechart.setHandler(self.GUI.workspace)
                self.statechart.setCanvas(self.GUI.getCanvas())
                self.statechart.setModified(0)
                return 1

    def canClose(self):
        if self.statechart.getModified() == 1:
            name = self._getShortStatechartName()
            answer = self.GUI.askYesNoCancel("Warning",name + " has been modified. Save?")
            if answer == "yes":
                return self.onSave()
            elif answer == "no":
                return 1
            else: #cancel
                return 0
        else:
            return 1

    def onSave(self):
	if self.statechart.isValid == 0:
	    return 0 # ignore event
	if (self.statechart.getFilename() != ""):
            self.save()
            return 1
        else:
            return self.onSaveAs()

    def onSaveAs(self):
	if self.statechart.isValid == 0:
	    return 0 # ignore event
	filename = self.GUI.getStatechartFilename()
        if filename == "":
	    return 0
        self.statechart.setFilename(filename)
        self.save()
        return 1

    def save(self):
        f = open(self.statechart.getFilename(),'w')
        self.statechart.deselect()
        self.statechart.setCanvas(None)
        self.statechart.setHandler(None)
        pickle.dump(self.statechart, f)
        f.close()
        self.statechart.setHandler(self.GUI.workspace)
        self.statechart.setCanvas(self.GUI.getCanvas())
        self.statechart.setModified(0)

    def onExportToPostscript(self):
	if self.statechart.isValid == 0:
	    return # ignore event
        filename = self.GUI.getPostscriptFilename()
        if filename != "":
            self.statechart.deselect()
            self.GUI.getCanvas().postscript(file=filename)

    def onExportToSVM(self):
	if self.statechart.isValid == 0:
	    return # ignore event
        filename = self.GUI.getSVMFilename()
        if filename != "":
            self.statechart.exportToSVM(filename)

    def onQuit(self):
	if self.statechart.isValid == 0:
	    return # ignore event
        if self.canClose():
            self.GUI.destroy()

    # STATECHART MODIFIED
    def onStatechartModified(self, modified):
        name = self._getShortStatechartName()
        if modified:
            self.GUI.setRootTitle(name + " [modified] - Statechart Editor")
            self.GUI.enable("save")
        else:
            self.GUI.setRootTitle(name + " - Statechart Editor")
            self.GUI.disable("save")

    def _getShortStatechartName(self):
        name = self.statechart.getFilename() # full name
        if name == "":
            return "Untitled"
        else:
            return name.split('/')[-1] # only filename

    # STATECHART EDITION EVENTS
    def onEditInitCode(self):
	self.GUI.editInitCode(self.statechart)

    def onEditInteractCode(self):
	self.GUI.editInteractCode(self.statechart)

    def onEditFinalCode(self):
	self.GUI.editFinalCode(self.statechart)


    # The other event are forwarded to
    # the current handler 'h'
    # STATE/TRANSITION EDITION EVENTS
    def onAddState(self):
        self.h = self.h.onAddState()

    def onAddSeparator(self):
        self.h = self.h.onAddSeparator()

    def onAddTransition(self):
        self.h = self.h.onAddTransition()

    def onAddTransitionTo(self):
        self.h = self.h.onAddTransitionTo()

    def onDelete(self):
        self.h = self.h.onDelete()

    def onEditState(self):
        self.h = self.h.onEditState()

    def onEditTransition(self):
        self.h = self.h.onEditTransition()

    def onSetStateAsDefault(self):
        self.h = self.h.onSetStateAsDefault()


    # CANVAS EVENTS
    def onCanvasEnter(self, event):
        self.h = self.h.onCanvasEnter(event)

    def onCanvasLeave(self, event):
        self.h = self.h.onCanvasLeave(event)

    def onCanvasButton(self, event):
	self.h = self.h.onCanvasButton(event)

    def onCanvasDoubleButton(self, event):
        self.h = self.h.onCanvasDoubleButton(event)

    def onCanvasMotion(self, event):
	self.h = self.h.onCanvasMotion(event)

    def onCanvasShiftMotion(self, event):
	self.h = self.h.onCanvasShiftMotion(event)

    def onCanvasButtonMotion(self, event):
	self.h = self.h.onCanvasButtonMotion(event)

    def onCanvasShiftButtonMotion(self, event):
	self.h = self.h.onCanvasShiftButtonMotion(event)

    def onCanvasButtonRelease(self, event):
        self.h = self.h.onCanvasButtonRelease(event)

    # STATE EVENTS
    def onStateButton1(self, state, event):
        self.h = self.h.onStateButton1(state, event)

    def onStateButton3(self, state, event):
        self.h = self.h.onStateButton3(state, event)
    
    def onStateDoubleButton1(self, state, event):
        self.h = self.h.onStateDoubleButton1(state, event)

    def onStateDoubleButton3(self, state, event):
        self.h = self.h.onStateDoubleButton3(state, event)
    
    def onStateButtonMotion1(self, state, event):
        self.h = self.h.onStateButtonMotion1(state, event)
    
    def onStateButtonMotion3(self, state, event):
        self.h = self.h.onStateButtonMotion3(state, event)
    
    def onStateButtonRelease1(self, state, event):
        self.h = self.h.onStateButtonRelease1(state, event)
    
    def onStateButtonRelease3(self, state, event):
        self.h = self.h.onStateButtonRelease3(state, event)

    # STATE BORDER EVENTS
    def onStateBorderEnter(self, state, border, event):
        self.h = self.h.onStateBorderEnter(state, border, event)
    
    def onStateBorderLeave(self, state, border, event):
        self.h = self.h.onStateBorderLeave(state, border, event)
    
    def onStateBorderButton1(self, state, border, event):
        self.h = self.h.onStateBorderButton1(state, border, event)
    
    def onStateBorderButtonMotion1(self, state, border, event):
        self.h = self.h.onStateBorderButtonMotion1(state, border, event)

    def onStateBorderButtonRelease1(self, state, border, event):
        self.h = self.h.onStateBorderButtonRelease1(state, border, event)

    # SEPARATOR EVENTS
    def onSeparatorEnter(self, sep, state, event):
        self.h = self.h.onSeparatorEnter(sep, state, event)

    def onSeparatorLeave(self, sep, state, event):
        self.h = self.h.onSeparatorLeave(sep, state, event)
        
    def onSeparatorButton1(self, sep, state, event):
        self.h = self.h.onSeparatorButton1(sep, state, event)

    def onSeparatorButton3(self, sep, state, event):
        self.h = self.h.onSeparatorButton3(sep, state, event)

    def onSeparatorButtonMotion1(self, sep, state, event):
        self.h = self.h.onSeparatorButtonMotion1(sep, state, event)

    def onSeparatorButtonMotion3(self, sep, state, event):
        self.h = self.h.onSeparatorButtonMotion3(sep, state, event)

    def onSeparatorButtonRelease1(self, sep, state, event):
        self.h = self.h.onSeparatorButtonRelease1(sep, state, event)

    def onSeparatorButtonRelease3(self, sep, state, event):
        self.h = self.h.onSeparatorButtonRelease3(sep, state, event)


    # TRANSITION EVENTS
    def onTransitionArrowButton1(self, transition, event):
        self.h = self.h.onTransitionArrowButton1(transition, event)

    def onTransitionSrcButton1(self, transition, event):
        self.h = self.h.onTransitionSrcButton1(transition, event)

    def onTransitionDestButton1(self, transition, event):
        self.h = self.h.onTransitionDestButton1(transition, event)

    def onTransitionHandleButton1(self, transition, event):
        self.h = self.h.onTransitionHandleButton1(transition, event)

    def onTransitionDoubleButton1(self, transition, event):
        self.h = self.h.onTransitionDoubleButton1(transition, event)

    def onTransitionButton3(self, transition, event):
        self.h = self.h.onTransitionButton3(transition, event)

    def onTransitionSrcButtonMotion1(self, transition, event):
        self.h = self.h.onTransitionSrcButtonMotion1(transition, event)

    def onTransitionDestButtonMotion1(self, transition, event):
        self.h = self.h.onTransitionDestButtonMotion1(transition, event)

    def onTransitionHandleButtonMotion1(self, transition, event):
        self.h = self.h.onTransitionHandleButtonMotion1(transition, event)

    def onTransitionButtonRelease1(self, transition, event):
        self.h = self.h.onTransitionButtonRelease1(transition, event)



























