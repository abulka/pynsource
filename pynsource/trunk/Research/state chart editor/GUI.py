# GUI.py
# user interface classes
from Tkinter import *
from Globals import *
import tkFileDialog 
import tkMessageBox
import os
import string # for EditTransitionDialog
from State import State

import random

class Workspace:
    def __init__(self, masterFrame, width, height, canvasWidth, canvasHeight, handler):
        #frame containing the canvas and the scrollbars
        self.frame = Frame(masterFrame)
        #width of the total workspace
        self.width = width
        #height of the total workspace
        self.height = height
        #current width of the canvas
        self.canvasWidth = canvasWidth
        #current height of the canvas
        self.canvasHeight = canvasHeight
        #event handler to send events to
        self.handler = handler
        #horizontal scrollbar
        self.xScrollbar = Scrollbar(self.frame, orient=HORIZONTAL)
        self.xScrollbar.pack(side=BOTTOM, fill=X)
        #vertical scrollbar
        self.yScrollbar = Scrollbar(self.frame, orient=VERTICAL)
        self.yScrollbar.pack(side=RIGHT, fill=Y)
        #canvas
        self.bd = 0 # borderwidth
        self.canvas = Canvas(self.frame, height=self.canvasHeight, width=self.canvasWidth, bg="white", borderwidth=self.bd, yscrollcommand=self.setYScrollbar, xscrollcommand=self.setXScrollbar, scrollregion=(0,0, width, height), highlightthickness=0)
        self._bindEvents()
        #make the canvas resizable
        self.canvas.pack(side=RIGHT, fill=BOTH, expand=1)
        self.canvas.focus_set() # focus on canvas
        self.yScrollbar.config(command=self.canvas.yview)
        self.xScrollbar.config(command=self.canvas.xview)
        self.x0 = 0
        self.y0 = 0
        #make the workspace resizable
        self.frame.pack(side=RIGHT, fill=BOTH, expand=1)
        # the following variable are used to eat canvas events 
        # when they are preceded by state events.
        self.skipMotion = 0
        self.skipShiftMotion = 0
        self.skipButton = 0
        self.skipDoubleButton = 0
        self.skipButtonMotion = 0
        self.skipShiftButtonMotion = 0
        self.skipButtonRelease = 0
        self.inCanvas = 0
        
        #bind canvas events
    def _bindEvents(self):
        self.canvas.bind("<Enter>",self.onEnter)
        self.canvas.bind("<Leave>",self.onLeave)
        self.canvas.bind("<Button-1>", self.onButton)
        self.canvas.bind("<Button-2>", self.onButton)
        self.canvas.bind("<Button-3>", self.onButton)
        self.canvas.bind("<Double-Button-1>", self.onDoubleButton)
        self.canvas.bind("<Double-Button-2>", self.onDoubleButton)
        self.canvas.bind("<Double-Button-3>", self.onDoubleButton)
        self.canvas.bind("<Motion>", self.onMotion)
        self.canvas.bind("<Shift-Motion>", self.onShiftMotion)
        self.canvas.bind("<B1-Motion>", self.onButtonMotion)
        self.canvas.bind("<B2-Motion>", self.onButtonMotion)
        self.canvas.bind("<B3-Motion>", self.onButtonMotion)
        self.canvas.bind("<Shift-B1-Motion>", self.onShiftButtonMotion)
        self.canvas.bind("<Shift-B2-Motion>", self.onShiftButtonMotion)
        self.canvas.bind("<Shift-B3-Motion>", self.onShiftButtonMotion)
        self.canvas.bind("<ButtonRelease-1>", self.onButtonRelease)
        self.canvas.bind("<ButtonRelease-2>", self.onButtonRelease)
        self.canvas.bind("<ButtonRelease-3>", self.onButtonRelease)
        
        # set the scrollbar and update y0 at the same time so that it doesn't need to
        # be updated each time an event occurs.
    def setXScrollbar(self, *args):
        apply(self.xScrollbar.set, args)
        low, hi = self.xScrollbar.get()
        #Because of the borderwidth, need to adjust the position to reflect the
        # real position of the cursor for both x0 and y0.
        self.x0 = low * self.width - self.bd - 1
        self.canvasWidth = (hi - low) * self.width
        
        # set the scrollbar and update y0
    def setYScrollbar(self, *args):
        apply(self.yScrollbar.set, args)
        low, hi = self.yScrollbar.get()
        self.y0 = low * self.height - self.bd - 1
        self.canvasHeight = (hi - low) * self.height
        
    def getCanvas(self):
        return self.canvas
        
    def isCursorInCanvas(self):
        return self.inCanvas
        
    def getEnterCanvasCoords(self):
        return (self.enterCanvasX, self.enterCanvasY)
        
    def getCanvasWidth(self):
        return self.canvasWidth
        
    def getCanvasHeight(self):
        return self.canvasHeight
        
    def setCursorNS(self):
        self.canvas.configure(cursor="sb_v_double_arrow")
        
    def setCursorWE(self):
        self.canvas.configure(cursor="sb_h_double_arrow")
        
    def setCursorNW_SE(self):
        if sys.platform == "win32":
            self.canvas.configure(cursor="size_nw_se")
        else:
            self.canvas.configure(cursor="bottom_right_corner")
            
    def setCursorNE_SW(self):
        if sys.platform == "win32":
            self.canvas.configure(cursor="size_ne_sw")
        else:
            self.canvas.configure(cursor="bottom_left_corner")
            
    def setCursorNormal(self):
        self.canvas.configure(cursor="")
        
        # canvas events
    def onEnter(self, event):
        self.inCanvas = 1
        event.x += self.x0
        event.y += self.y0
        self.enterCanvasX = event.x
        self.enterCanvasY = event.y
        self.handler.onCanvasEnter(event)
        
    def onLeave(self, event):
        self.inCanvas = 0
        self.handler.onCanvasLeave(event)
        
    def onButton(self, event):
        if self.skipButton == 1:
            self.skipButton = 0
            return
        event.x += self.x0
        event.y += self.y0
        self.handler.onCanvasButton(event)
        
    def onDoubleButton(self, event):
        if self.skipDoubleButton == 1:
            self.skipDoubleButton = 0
            return
        event.x += self.x0
        event.y += self.y0
        self.handler.onCanvasDoubleButton(event)
        
    def onMotion(self, event):
        if self.skipMotion == 1:
            self.skipMotion = 0
            return
        event.x += self.x0
        event.y += self.y0
        self.handler.onCanvasMotion(event)
        
    def onShiftMotion(self, event):
        if self.skipShiftMotion == 1:
            self.skipShiftMotion = 0
            return
        event.x += self.x0
        event.y += self.y0
        self.handler.onCanvasShiftMotion(event)
        
    def onButtonMotion(self, event):
        if self.skipButtonMotion == 1:
            self.skipButtonMotion = 0
            return
        event.x += self.x0
        event.y += self.y0
        self.handler.onCanvasButtonMotion(event)
        
    def onShiftButtonMotion(self, event):
        if self.skipShiftButtonMotion == 1:
            self.skipShiftButtonMotion = 0
            return
        event.x += self.x0
        event.y += self.y0
        self.handler.onCanvasShiftButtonMotion(event)
        
    def onButtonRelease(self, event):
        if self.skipButtonRelease == 1:
            self.skipButtonRelease = 0
            return
        event.x += self.x0
        event.y += self.y0
        self.handler.onCanvasButtonRelease(event)
        
        # state events
    def onStateButton1(self, state, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateButton1(state, event)
        
    def onStateButton3(self, state, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateButton3(state, event)
        
    def onStateDoubleButton1(self, state, event):
        self.skipDoubleButton = 1
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateDoubleButton1(state, event)
        
    def onStateDoubleButton3(self, state, event):
        self.skipDoubleButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateDoubleButton3(state, event)
        
    def onStateButtonMotion1(self, state, event):
        self.skipButtonMotion = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateButtonMotion1(state, event)
        
    def onStateButtonMotion3(self, state, event):
        self.skipButtonMotion = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateButtonMotion3(state, event)
        
    def onStateButtonRelease1(self, state, event):
        self.skipButtonRelease = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateButtonRelease1(state, event)
        
    def onStateButtonRelease3(self, state, event):
        self.skipButtonRelease = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateButtonRelease3(state, event)
        
        # state border events
    def onStateBorderEnter(self, state, border, event):
        self.handler.onStateBorderEnter(state, border, event)
        
    def onStateBorderLeave(self, state, border, event):
        self.handler.onStateBorderLeave(state, border, event)
        
    def onStateBorderButton1(self, state, border, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateBorderButton1(state, border, event)
        
    def onStateBorderButtonMotion1(self, state, border, event):
        self.skipButtonMotion = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateBorderButtonMotion1(state, border, event)
        
    def onStateBorderButtonRelease1(self, state, border, event):
        self.skipButtonRelease = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onStateBorderButtonRelease1(state, border, event)
        
        # separator events
    def onSeparatorEnter(self, sep, state, event):
        self.handler.onSeparatorEnter(sep, state, event)
        
    def onSeparatorLeave(self, sep, state, event):
        self.handler.onSeparatorLeave(sep, state, event)
        
    def onSeparatorButton1(self, sep, state, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onSeparatorButton1(sep, state, event)
        
    def onSeparatorButton3(self, sep, state, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onSeparatorButton3(sep, state, event)
        
    def onSeparatorButtonMotion1(self, sep, state, event):
        self.skipButtonMotion = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onSeparatorButtonMotion1(sep, state, event)
        
    def onSeparatorButtonMotion3(self, sep, state, event):
        self.skipButtonMotion = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onSeparatorButtonMotion3(sep, state, event)
        
    def onSeparatorButtonRelease1(self, sep, state, event):
        self.skipButtonRelease = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onSeparatorButtonRelease1(sep, state, event)
        
    def onSeparatorButtonRelease3(self, sep, state, event):
        self.skipButtonRelease = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onSeparatorButtonRelease3(sep, state, event)
        
        # TRANSITION EVENTS
    def onTransitionArrowButton1(self, transition, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionArrowButton1(transition, event)
        
    def onTransitionSrcButton1(self, transition, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionSrcButton1(transition, event)
        
    def onTransitionDestButton1(self, transition, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionDestButton1(transition, event)
        
    def onTransitionHandleButton1(self, transition, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionHandleButton1(transition, event)
        
    def onTransitionButton3(self, transition, event):
        self.skipButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionButton3(transition, event)
        
    def onTransitionDoubleButton1(self, transition, event):
        self.skipDoubleButton = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionDoubleButton1(transition, event)
        
    def onTransitionSrcButtonMotion1(self, transition, event):
        self.skipButtonMotion = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionSrcButtonMotion1(transition, event)
        
    def onTransitionDestButtonMotion1(self, transition, event):
        self.skipButtonMotion = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionDestButtonMotion1(transition, event)
        
    def onTransitionHandleButtonMotion1(self, transition, event):
        self.skipButtonMotion = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionHandleButtonMotion1(transition, event)
        
    def onTransitionButtonRelease1(self, transition, event):
        self.skipButtonRelease = 1
        event.x += self.x0
        event.y += self.y0
        self.handler.onTransitionButtonRelease1(transition, event)
        
        # statechart modified event
    def onStatechartModified(self, modified):
        self.handler.onStatechartModified(modified)
        
        # general Dialog class taken from "An Introduction to Tkinter"
        # www.pythonware.com/library/tkinter/introduction/dialog-windows.htm
class Dialog(Toplevel):
    def __init__(self, parent, title = None):
        Toplevel.__init__(self, parent)
        x = parent.winfo_rootx() + parent.winfo_width()/2
        y = parent.winfo_rooty() + parent.winfo_height()/2
        self.geometry("+%d+%d" % (x-150, y-150))
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        if sys.platform == "win32":
            self.iconbitmap("icon16win.ico")
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.initial_focus.focus_set()
        self.resizable(0,0)
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)
        
        # construction hooks
    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        pass
        
    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("&lt;Return>", self.ok)
        self.bind("&lt;Escape>", self.cancel)
        box.pack()
        
        # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()
        
    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
        
        # command hooks
    def validate(self):
        return 1 # override
        
    def apply(self):
        pass # override
        
class EditCodeDialog(Dialog):
    def __init__(self, root, statechart, codeTitle, previousCode):
        self.codeTitle = codeTitle
        self.previousCode = previousCode
        self.newCode = previousCode
        self.myStatechart = statechart
        Dialog.__init__(self, root, title=codeTitle)
        
    def body(self, frame):
        Label(frame, text=self.codeTitle+":").grid(column=0, row=0, sticky=W)
        self.codeText = Text(frame, height=20, width=60)
        self.codeText.insert(END, self.previousCode)
        self.codeText.grid(column=0, row=1, sticky=W)
        return self.codeText # initial focus to code
        
    def validate(self):
        return 1
        
    def apply(self):
        self.newCode = self.codeText.get(1.0, END)[:-1]
        
        
class EditStateDialog(Dialog):
    def __init__(self, root, state, statechart):
        self.myState = state
        self.myStatechart = statechart
        Dialog.__init__(self, root, title="State")
        
    def body(self, frame):
        nameFrame = Frame(frame)
        Label(nameFrame, text="Name:").pack(side=LEFT)
        self.name = Entry(nameFrame)
        self.name.insert(END, self.myState.getName())
        self.name.pack(side=LEFT)
        nameFrame.grid(column = 0, row = 0, sticky=W)
        # is default
        self.ds = IntVar()
        self.ds.set(self.myState.getDS())
        dsCheckbutton = Checkbutton(frame, text="Default State", variable=self.ds)
        dsCheckbutton.grid(column=0, row=1, sticky=W)
        # don't allow a component to be "defaultless"
        if self.ds.get() == 1:
            dsCheckbutton.config(state=DISABLED)
            
            # is final
        self.fs = IntVar()
        self.fs.set(self.myState.getFS())
        fsCheckbutton = Checkbutton(frame, text="Final State", variable=self.fs, command=self._setForFinal)
        fsCheckbutton.grid(column=0, row=2, sticky=W)
        
        # history support
        hsFrame = Frame(frame)
        self.hs = IntVar()
        self.hs.set(self.myState.getHS())
        self.hsLabel = Label(hsFrame, text="History support:")
        self.hsLabel.grid(column=0, row=0, sticky=W)
        self.no_hs = Radiobutton(hsFrame, text="None", variable=self.hs,value=NO_HS)
        self.no_hs.grid(column=0, row=1, sticky=W)
        self.one_hs = Radiobutton(hsFrame, text="One level", variable=self.hs,value=ONE_HS)
        self.one_hs.grid(column=0, row=2, sticky=W)
        self.deep_hs = Radiobutton(hsFrame, text="Deep", variable=self.hs,value=DEEP_HS)
        self.deep_hs.grid(column=0, row=3, sticky=W)
        hsFrame.grid(column=0, row=3, sticky=W)
        
        # entry code
        Label(frame, text="Entry Code:").grid(column=0, row=4, sticky=W)
        self.entryCode = Text(frame, height=5, width=40)
        self.entryCode.insert(END, self.myState.getEntryCode())
        self.entryCode.grid(column=0, row=5, sticky=W)
        # exit code
        self.exitCodeLabel = Label(frame, text="Exit Code:")
        self.exitCodeLabel.grid(column=0, row=6, sticky=W)
        self.exitCode = Text(frame, height=5, width=40)
        self.exitCode.insert(END, self.myState.getExitCode())
        self.exitCode.grid(column=0, row=7, sticky=W)
        
        # disable a few things if final
        self._setForFinal()
        
        return self.name # initial focus to name entry
        
    def _setForFinal(self):
        if self.fs.get() == 1:
            self.hsLabel.config(state=DISABLED)
            self.hs.set(NO_HS)
            self.no_hs.config(state=DISABLED)
            self.one_hs.config(state=DISABLED)
            self.deep_hs.config(state=DISABLED)
            self.exitCodeLabel.config(state=DISABLED)
            self.exitCode.delete(1.0,END)
            self.exitCode.config(state=DISABLED)
        else:
            self.hsLabel.config(state=NORMAL)
            self.no_hs.config(state=NORMAL)
            self.one_hs.config(state=NORMAL)
            self.deep_hs.config(state=NORMAL)
            self.exitCodeLabel.config(state=NORMAL)
            self.exitCode.config(state=NORMAL)
            
            
    def validate(self):
        if self.name.get() == "":
            tkMessageBox.showinfo("State", "A state must be given a name")
            return 0
        elif (self.myState.getName() != self.name.get()) and not self.myStatechart.isFreeName(self.myState.parent, self.name.get()):
            tkMessageBox.showinfo("State", "State name already chosen")
            return 0
        return 1
        
    def apply(self):
        self.myState.setName(self.name.get())
        self.myState.setDS(self.ds.get())
        self.myState.setFS(self.fs.get())
        self.myStatechart.updateTransitions()
        self.myState.setHS(self.hs.get())
        if self.myState.getHS() == NO_HS:
            self.myStatechart.disableTransitionHistory(self.myState)
        self.myState.setEntryCode(self.entryCode.get(1.0, END)[:-1])
        self.myState.setExitCode(self.exitCode.get(1.0, END)[:-1])
        self.myStatechart.setModified(1)
        
class EditTransitionDialog(Dialog):
    def __init__(self, root, transition, statechart):
        self.transition = transition
        self.statechart = statechart
        Dialog.__init__(self, root, title="Transition")
        
    def body(self, frame):
        # source state
        srcDestFrame = Frame(frame)
        Label(srcDestFrame, text="Source State:").grid(column=0,row=0,sticky=E)
        Label(srcDestFrame, text=self.transition.getSrc().getName()).grid(column=1,row=0,sticky=W)
        # dest state
        Label(srcDestFrame, text="Destination State:").grid(column=0,row=1,sticky=E)
        Label(srcDestFrame, text=self.transition.getDest().getName()).grid(column=1,row=1,sticky=W)
        srcDestFrame.grid(column = 0, row = 1, sticky=W)
        
        # time or event
        self.timeEventVar = IntVar()
        # event radiobutton
        eventFrame = Frame(frame)
        Radiobutton(eventFrame, text="fire on event", variable=self.timeEventVar,value=1, command=self.eventChosen).pack(side=LEFT)
        self.eventEntry = Entry(eventFrame, width=15)
        self.eventEntry.pack(side=LEFT)
        eventFrame.grid(column=0, row=2, sticky=W)
        # time radiobutton
        timeFrame = Frame(frame)
        Radiobutton(timeFrame, text="fire after", variable=self.timeEventVar,value=0, command=self.timeChosen).pack(side=LEFT)
        self.timeEntry = Entry(timeFrame, width=3)
        self.timeEntry.pack(side=LEFT)
        Label(timeFrame, text="seconds").pack(side=LEFT)
        timeFrame.grid(column=0, row=3, sticky=W)
        
        if self.transition.getTime() > 0: # if time chosen
            self.timeEventVar.set(0)
            self.timeEntry.insert(END, str(self.transition.getTime()))
            self.eventEntry.config(state=DISABLED)
        else: # else event chosen
            self.timeEventVar.set(1)
            self.eventEntry.insert(END, self.transition.getEvent())
            self.timeEntry.config(state=DISABLED)
            
            # history or not
        self.historyValue = IntVar()
        self.historyValue.set(self.transition.getHistory())
        historyCheckbutton = Checkbutton(frame, text="Go to the history of the destination state", variable=self.historyValue)
        if self.transition.getDest().getHS() == NO_HS:
            historyCheckbutton.config(state=DISABLED)
        historyCheckbutton.grid(column=0, row=4, sticky=W)
        
        # code
        Label(frame, text="Code:").grid(column=0, row=5, sticky=W)
        self.codeText = Text(frame, height=5, width=40)
        self.codeText.insert(END, self.transition.getCode())
        self.codeText.grid(column=0, row=6, sticky=W)
        return self.eventEntry # initial focus to event entry
        
    def timeChosen(self):
        self.timeEntry.config(state=NORMAL)
        #	self.timeEntry.insert(END, "1.0")
        self.timeEntry.focus_set()
        self.eventEntry.delete(0,END)
        self.eventEntry.config(state=DISABLED)
        
    def eventChosen(self):
        self.eventEntry.config(state=NORMAL)
        self.eventEntry.focus_set()
        self.timeEntry.delete(0,END)
        self.timeEntry.config(state=DISABLED)
        
    def validate(self):
        if self.timeEventVar.get() == 0: # chose time
            try:
                t = string.atof(self.timeEntry.get())
            except ValueError:
                tkMessageBox.showinfo("Transition", "Incorrect value for time")
                return 0
            if t <= 0:
                tkMessageBox.showinfo("Transition", "Time value must be positive")
                return 0
            return 1
        else: # chose event
            if self.eventEntry.get() == "":
                tkMessageBox.showinfo("Transition", "An event must be specified")
                return 0
            return 1
            
    def apply(self):
        if self.timeEventVar.get() == 0: # time
            t = string.atof(self.timeEntry.get())
            self.transition.setTime(t)
            self.transition.setEvent("")
        else:
            self.transition.setEvent(self.eventEntry.get())
            self.transition.setTime(-1)
        self.transition.setHistory(self.historyValue.get())
        self.transition.setCode(self.codeText.get(1.0, END)[:-1])
        self.statechart.setModified(1)
        
        
        
        # graphical user interface
class GUI:
    def __init__(self, handler):
        self.handler = handler
        self._createRootWindow()
        self._createMenuBar()
        self._createWorkspace()
        self._createCanvasPopup()
        self._createStatePopup()
        self._createSeparatorPopup()
        self._createTransitionPopup()
        
    def mainloop(self):
        self.root.mainloop()
        
    def destroy(self):
        self.root.destroy()
        
    def getStatechartHandler(self):
        return self.workspace
        
    def getCanvas(self):
        return self.workspace.getCanvas()
        
        # call with event.x_root, event.y_root
    def showCanvasPopup(self, x, y):
        self.canvasPopup.tk_popup(x, y)
        
    def showStatePopup(self, x, y):
        self.statePopup.tk_popup(x, y)
        
    def showSeparatorPopup(self, x, y):
        self.separatorPopup.tk_popup(x, y)
        
    def showTransitionPopup(self, x, y):
        self.transitionPopup.tk_popup(x, y)
        
    def showError(self, title, text):
        tkMessageBox.showerror(title, text)
        
    def askYesNoCancel(self, t,m):
        return tkMessageBox._show(title=t, message=m, type="yesnocancel", icon="warning")
        
    def getStatechartFilename(self):
        return tkFileDialog.asksaveasfilename(defaultextension="stt", filetypes=[("Statechart",".stt"), ("All files","*")],title="Save as")
        
    def getSVMFilename(self):
        return tkFileDialog.asksaveasfilename(defaultextension="des", filetypes=[("SVM Description",".des"), ("All files","*")],title="Export to SVM")
        
    def getPostscriptFilename(self):
        return tkFileDialog.asksaveasfilename(defaultextension="ps", filetypes=[("Postscript",".ps"), ("All files","*")],title="Export to Postscript")
        
    def getStatechartFile(self):
        return tkFileDialog.askopenfilename(defaultextension="stt", filetypes=[("Statechart",".stt"), ("All files","*")],title="Open")
        
    def editInitCode(self, statechart):
        title = "Initialization Code"
        code = statechart.getInitCode()
        codeDialog = EditCodeDialog(self.root, statechart, title,code)
        statechart.setInitCode(codeDialog.newCode)
        
    def editInteractCode(self, statechart):
        title = "Interaction Code"
        code = statechart.getInteractCode()
        codeDialog = EditCodeDialog(self.root, statechart, title,code)
        statechart.setInteractCode(codeDialog.newCode)
        
    def editFinalCode(self, statechart):
        title = "Finalization Code"
        code = statechart.getFinalCode()
        codeDialog = EditCodeDialog(self.root, statechart, title,code)
        statechart.setFinalCode(codeDialog.newCode)
        
    def editState(self, state, statechart):
        editStateDialog = EditStateDialog(self.root, state, statechart)
        
    def editTransition(self, transition, statechart):
        eTD = EditTransitionDialog(self.root, transition, statechart)
        
    def _createRootWindow(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.onQuit)
        self.root.title("Untitled - Statechart Editor")
        if sys.platform == "win32":
            self.root.iconbitmap("icon16win.ico")
        self.root.geometry("%dx%d%+d%+d" % (640, 480, 250, 50))
        self.root.bind("<Key>", self.onKey)
        self.root.bind("<Control-Key>", self.onControlKey)
        
    def setRootTitle(self, title):
        self.root.title(title)
        
    def onQuit(self):
        self.handler.onQuit()
        
    def onKey(self, event):
        if event.keysym == "Delete":
            self.handler.onDelete()
            
    def onControlKey(self, event):
        if event.keysym == 'n':
            if self.Ctrl_N_Enabled:
                self.handler.onNew()
        elif event.keysym == 'o':
            if self.Ctrl_O_Enabled:
                self.handler.onOpen()
        elif event.keysym == 's':
            if self.Ctrl_S_Enabled:
                self.handler.onSave()
        elif event.keysym == 'q':
            self.handler.onQuit()
            
    def _createMenuBar(self):
        self.menuBar = Menu(self.root)
        self.fileMenu = Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="New", accelerator="Ctrl+N", command=self.handler.onNew)
        self.Ctrl_N_Enabled = 1
        self.fileMenu.add_command(label="Open...", accelerator="Ctrl+O", command=self.handler.onOpen)
        self.Ctrl_O_Enabled = 1
        self.fileMenu.add_command(label="Save", accelerator="Ctrl+S", command=self.handler.onSave)
        self.Ctrl_S_Enabled = 1
        self.fileMenu.add_command(label="Save as...", command=self.handler.onSaveAs)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Postscript...", command=self.handler.onExportToPostscript)
        self.fileMenu.add_command(label="SVM description...", command=self.handler.onExportToSVM)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", accelerator="Atl+F4", command=self.handler.onQuit)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)
        
        self.editMenu = Menu(self.menuBar, tearoff=0)
        self.editMenu.add_command(label="Add State...", command=self.handler.onAddState)
        self.editMenu.add_command(label="Add Transition...", command=self.handler.onAddTransition)
        self.editMenu.add_command(label="Add Component Separator...", command=self.handler.onAddSeparator)
        self.editMenu.add_command(label="Delete", command=self.handler.onDelete, accelerator="Del")
        self.editMenu.add_separator()
        self.editMenu.add_command(label="Initialization Code...", command=self.handler.onEditInitCode)
        self.editMenu.add_command(label="Interaction Code...", command=self.handler.onEditInteractCode)
        self.editMenu.add_command(label="Finalization Code...", command=self.handler.onEditFinalCode)
        self.menuBar.add_cascade(label="Edit", menu=self.editMenu)
        
        self.umlMenu = Menu(self.menuBar, tearoff=0)
        self.umlMenu.add_command(label="Andy 01 Add State...", command=self.Andy01)
        self.umlMenu.add_command(label="Andy 02 Random add...", command=self.Andy02)
        self.menuBar.add_cascade(label="UML", menu=self.umlMenu)
        
        self.root.config(menu=self.menuBar)
        
    
    def Andy01(self):
        res = self.handler.link.stateAdder._addState(120, 120, parent=None)
        print res
        
    def Andy02(self):
        for i in range(1,20):
            self.handler.link.stateAdder._addState(random.randint(100,220), 100+random.randint(100,220), parent=None)
            print i
        
    def _createWorkspace(self):
        self.workspace = Workspace(self.root, 1200, 1200, 100, 100, self.handler)
        self.canvas = self.workspace.getCanvas()
        
    def _createCanvasPopup(self):
        self.canvasPopup = Menu(self.root, tearoff=0)
        self.canvasPopup.add_command(label="Add State...", command=self.handler.onAddState, state=NORMAL)
        self.canvasPopup.add_command(label="Add Transition...", command=self.handler.onAddTransition, state=NORMAL)
        self.canvasPopup.add_command(label="Add Component Separator...", command=self.handler.onAddSeparator, state=NORMAL)
        
        
    def _createStatePopup(self):
        self.statePopup = Menu(self.root, tearoff=0)
        self.statePopup.add_command(label="Add State...", command=self.handler.onAddState, state=NORMAL)
        self.statePopup.add_command(label="Add Transition to...", command=self.handler.onAddTransitionTo, state=NORMAL)
        self.statePopup.add_command(label="Add Component Separator...", command=self.handler.onAddSeparator, state=NORMAL)
        self.statePopup.add_separator()
        self.statePopup.add_command(label="Edit...", command=self.handler.onEditState, state=NORMAL)
        self.statePopup.add_command(label="Set as Default", command=self.handler.onSetStateAsDefault, state=NORMAL)
        self.statePopup.add_separator()
        # delete state
        self.statePopup.add_command(label="Delete", command=self.handler.onDelete, state=NORMAL)
        
    def _createSeparatorPopup(self):
        self.separatorPopup = Menu(self.root, tearoff=0)
        self.separatorPopup.add_command(label="Delete Component Separator", command=self.handler.onDelete, state=NORMAL)
        
    def _createTransitionPopup(self):
        self.transitionPopup = Menu(self.root, tearoff=0)
        self.transitionPopup.add_command(label="Edit...", command=self.handler.onEditTransition, state=NORMAL)
        self.transitionPopup.add_command(label="Delete", command=self.handler.onDelete, state=NORMAL)
        
    def enable(self, command):
        if command == "new":
            self.fileMenu.entryconfig(0, state=NORMAL)
            self.Ctrl_N_Enabled = 1
        elif command == "open":
            self.fileMenu.entryconfig(1, state=NORMAL)
            self.Ctrl_O_Enabled = 1
        elif command == "save":
            self.fileMenu.entryconfig(2, state=NORMAL)
            self.Ctrl_S_Enabled = 1
        elif command == "saveAs":
            self.fileMenu.entryconfig(3, state=NORMAL)
        elif command == "exportToPostscript":
            self.fileMenu.entryconfig(5, state=NORMAL)
        elif command == "exportToSVM":
            self.fileMenu.entryconfig(6, state=NORMAL)
        elif command == "quit":
            self.fileMenu.entryconfig(8, state=NORMAL)
        elif command == "setStateAsDefault":
            self.statePopup.entryconfig(5, state=NORMAL)
        elif command == "delete":
            self.editMenu.entryconfig(3, state=NORMAL)
            self.statePopup.entryconfig(7, state=NORMAL)
        elif command == "addState":
            self.canvasPopup.entryconfig(0, state=NORMAL)
            self.statePopup.entryconfig(0, state=NORMAL)
            self.editMenu.entryconfig(0, state=NORMAL)
        elif command == "addTransition":
            self.canvasPopup.entryconfig(1, state=NORMAL)
            self.statePopup.entryconfig(1, state=NORMAL)
            self.editMenu.entryconfig(1, state=NORMAL)
        elif command == "addSeparator":
            self.canvasPopup.entryconfig(2, state=NORMAL)
            self.statePopup.entryconfig(2, state=NORMAL)
            self.editMenu.entryconfig(2, state=NORMAL)
            
            
    def disable(self, command):
        if command == "new":
            self.fileMenu.entryconfig(0, state=DISABLED)
            self.Ctrl_N_Enabled = 0
        elif command == "open":
            self.fileMenu.entryconfig(1, state=DISABLED)
            self.Ctrl_O_Enabled = 0
        elif command == "save":
            self.fileMenu.entryconfig(2, state=DISABLED)
            self.Ctrl_S_Enabled = 0
        elif command == "saveAs":
            self.fileMenu.entryconfig(3, state=DISABLED)
        elif command == "exportToPostscript":
            self.fileMenu.entryconfig(5, state=DISABLED)
        elif command == "exportToSVM":
            self.fileMenu.entryconfig(6, state=DISABLED)
        elif command == "quit":
            self.fileMenu.entryconfig(8, state=DISABLED)
        elif command == "setStateAsDefault":
            self.statePopup.entryconfig(5, state=DISABLED)
        elif command == "delete":
            self.editMenu.entryconfig(3, state=DISABLED)
            self.statePopup.entryconfig(7, state=DISABLED)
        elif command == "addState":
            self.canvasPopup.entryconfig(0, state=DISABLED)
            self.statePopup.entryconfig(0, state=DISABLED)
            self.editMenu.entryconfig(0, state=DISABLED)
        elif command == "addTransition":
            self.canvasPopup.entryconfig(1, state=DISABLED)
            self.statePopup.entryconfig(1, state=DISABLED)
            self.editMenu.entryconfig(1, state=DISABLED)
        elif command == "addSeparator":
            self.canvasPopup.entryconfig(2, state=DISABLED)
            self.statePopup.entryconfig(2, state=DISABLED)
            self.editMenu.entryconfig(2, state=DISABLED)
            
            
            
            
            
            
            
            
            
            
            
