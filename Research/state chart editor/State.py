from tkinter import *
import sys
import math
from Globals import *
from Separator import Separator
# State background/border need workspace for events

class State:
    def __init__(self, x0, y0, name, parent, handler, states,separators, width=MIN_WIDTH, height=MIN_HEIGHT, ds=0, fs=0,hs=NO_HS, entryCode="",exitCode=""):
	self.parent = parent
	self.states = states
	self.separators = separators
	self.canvas = None
	self.handler = handler
	self.x0 = x0
	self.y0 = y0
        if width < MIN_WIDTH:
            width = MIN_WIDTH
        if height < MIN_HEIGHT:
            height = MIN_HEIGHT
        self.x1 = x0 + width
        self.y1 = y0 + height
	self.borderColor = "black"
	self._setRadius()
        # The different parts of a state
        # Each part takes care of its graphical
        # representation
	self.fs = FS(self, fs, handler)
        self.background = Background(self, handler)
        self.border = Border(self, handler)
        self.name = Name(self, name, handler)
        self.ds = DS(self, ds, handler)
        self.hs = HS(self, hs, handler)
	# entry and exit code strings
	self.entryCode = entryCode
	self.exitCode = exitCode
        self.parts = [self.background, self.border, self.name, self.ds, self.hs, self.fs]

    def setCanvas(self, canvas):
	self.canvas = canvas
        for part in self.parts:
            part.setCanvas(canvas)
        for sep in self.separators:
            sep.setCanvas(canvas)
        for state in self.states:
            state.setCanvas(canvas)

    def getCoords(self):
	return (self.x0, self.y0, self.x1, self.y1, self.r)

    def getName(self):
	return self.name.get()

    def getFullName(self):
        name = self.getName()
        s = self
        p = self.parent
        while p != None:
            name = p.getName() + ".c" + str(p.getComponentNumber(s)) + "." + name
            s = p
            p = p.parent
        return name

    def writeHierarchySVM(self,file,tabulation):
        file.write(tabulation + self.getName())
        if self.getDS() == 1:
            file.write(" [DS]")
        if self.getFS() == 1:
            file.write(" [FS]")
        if self.getHS() == ONE_HS:
            file.write(" [HS]")
        elif self.getHS() == DEEP_HS:
            file.write(" [HS*]")
        file.write("\n")
        numComponents = len(self.separators) + 1
        if len(self.states) == 0:
            return
        for c in range(numComponents):
            file.write(tabulation + "  c" + str(c) + " [CS] [DS]\n")
            for s in self.states:
                if self.getComponentNumber(s) == c:
                    s.writeHierarchySVM(file, tabulation + "    ")

    def writeEnterExitSVM(self,file):
        if self.entryCode != "":
            file.write("ENTER:\n")
            file.write("  N: " + self.getFullName() + "\n")
            lines = self.getEntryCode().split('\n')
            file.write("  O: " + lines[0] + "\n")
            lines = lines[1:]
            for line in lines:
                file.write("     " + line + "\n")
        if self.exitCode != "":
            file.write("EXIT:\n")
            file.write("  S: " + self.getFullName() + "\n")
            lines = self.getExitCode().split('\n')
            file.write("  O: " + lines[0] + "\n")
            lines = lines[1:]
            for line in lines:
                file.write("     " + line + "\n")
        for s in self.states:
            s.writeEnterExitSVM(file)

    def getComponentNumber(self, state):
        cn = 0
        for sep in self.separators:
            if sep.getY() < state.y0:
                cn = cn + 1
        return cn

    def setName(self, name):
	self.name.set(name)
	self.updateDisplay()

    def getDS(self):
	return self.ds.get()

    def setDS(self, ds):
        self.ds.set(ds)
	self.updateDisplay()

    def getFS(self):
	return self.fs.get()

    def setFS(self, fs):
        self.fs.set(fs)
	self.updateDisplay()

    def getHS(self):
        return self.hs.get()

    def setHS(self, hs):
        self.hs.set(hs)
	self.updateDisplay()

    def getEntryCode(self):
        return self.entryCode

    def setEntryCode(self, entryCode):
        self.entryCode = entryCode

    def getExitCode(self):
        return self.exitCode

    def setExitCode(self, exitCode):
        self.exitCode = exitCode

    def setBackgroundColor(self, color):
	self.background.setColor(color)

    def setBorderColor(self, color):
	self.borderColor = color
	self.updateDisplay()

    def lift(self):
        for part in self.parts:
            part.lift()
        for sep in self.separators:
            sep.lift()
        for state in self.states:
            state.lift()

    # mark and backToMark can be used to bring the
    # state back to a previous position/size
    def mark(self):
        self.old_x0 = self.x0
        self.old_y0 = self.y0
        self.old_x1 = self.x1
        self.old_y1 = self.y1

    def backToMark(self):
        dx = self.old_x0 - self.x0
        dy = self.old_y0 - self.y0
        for sep in self.separators:
	    sep.translate(dy)
        for state in self.states:
            state.translate(dx,dy)
        self.x0 = self.old_x0
        self.y0 = self.old_y0
        self.x1 = self.old_x1
        self.y1 = self.old_y1
        self.updateDisplay()
        return dx,dy

    def setHandler(self, handler):
	self.handler = handler
        for part in self.parts:
            part.setHandler(handler)
        for sep in self.separators:
            sep.setHandler(handler)
        for state in self.states:
            state.setHandler(handler)

    def translate(self, dx, dy):
        self.x0 = self.x0 + dx
        self.x1 = self.x1 + dx
        self.y0 = self.y0 + dy
        self.y1 = self.y1 + dy
        for sep in self.separators:
	    sep.translate(dy)
        for state in self.states:
            state.translate(dx,dy)
        self.updateDisplay()

    def scale(self, border, x, y):
	minSep = self._getMinSep()
        maxSep = self._getMaxSep()
	scalingMethods = {"N":self._scaleN,"S":self._scaleS,"E":self._scaleE,"W":self._scaleW,"NW":self._scaleNW,"NE":self._scaleNE,"SW":self._scaleSW,"SE":self._scaleSE}
	scalingMethods[border](*[x, y, minSep, maxSep])
	self._setRadius()
        self.updateDisplay()

    def _getMinSep(self):
        y = self.y1
        for s in self.separators:
            sy = s.getY()
            if sy < y:
                y = sy
        return y

    def _getMaxSep(self):
        y = self.y0
        for s in self.separators:
            sy = s.getY()
            if sy > y:
                y = sy
        return y

    def _setRadius(self):
	self.r = RADIUS # constant
#        self.r = min(self.x1 - self.x0, self.y1 - self.y0)/10 + 5

    def _minChildY(self):
        min = 1000000
        for s in self.states:
            if s.y0 < min:
                min = s.y0
        return min

    def _maxChildY(self):
        max = -1000000
        for s in self.states:
            if s.y1 > max:
                max = s.y1
        return max

    def _minChildX(self):
        min = 1000000
        for s in self.states:
            if s.x0 < min:
                min = s.x0
        return min

    def _maxChildX(self):
        max = -1000000
        for s in self.states:
            if s.x1 > max:
                max = s.x1
        return max

    def _scaleN(self, x, y, minSep, maxSep):
        if self.y1 - y < MIN_HEIGHT:
            y = self.y1 - MIN_HEIGHT
        if y > minSep - SEPARATOR_PAD:
            y = minSep - SEPARATOR_PAD
        minY = self._minChildY()
        if y > minY:
            y = minY
        self.y0 = y

    def _scaleS(self, x, y, minSep, maxSep):
        if y - self.y0 < MIN_HEIGHT:
            y = self.y0 + MIN_HEIGHT
        if y < maxSep + SEPARATOR_PAD:
            y = maxSep + SEPARATOR_PAD
        maxY = self._maxChildY()
        if y < maxY:
            y = maxY
        self.y1 = y

    def _scaleE(self, x, y, minSep, maxSep):
        if x - self.x0 < MIN_WIDTH:
            x = self.x0 + MIN_WIDTH
        maxX = self._maxChildX()
        if x < maxX:
            x = maxX
        self.x1 = x

    def _scaleW(self, x, y, minSep, maxSep):
        if self.x1 - x < MIN_WIDTH:
            x = self.x1 - MIN_WIDTH
        minX = self._minChildX()
        if x > minX:
            x = minX
        self.x0 = x

    def _scaleNW(self, x, y, minSep, maxSep):
        if self.y1 - y < MIN_HEIGHT:
            y = self.y1 - MIN_HEIGHT
        if y > minSep - SEPARATOR_PAD:
            y = minSep - SEPARATOR_PAD
        minY = self._minChildY()
        if y > minY:
            y = minY
        self.y0 = y
        if self.x1 - x < MIN_WIDTH:
            x = self.x1 - MIN_WIDTH
        minX = self._minChildX()
        if x > minX:
            x = minX
        self.x0 = x

    def _scaleNE(self, x, y, minSep, maxSep):
        if self.y1 - y < MIN_HEIGHT:
            y = self.y1 - MIN_HEIGHT
        if y > minSep - SEPARATOR_PAD:
            y = minSep - SEPARATOR_PAD
        minY = self._minChildY()
        if y > minY:
            y = minY
        self.y0 = y
        if x - self.x0 < MIN_WIDTH:
            x = self.x0 + MIN_WIDTH
        maxX = self._maxChildX()
        if x < maxX:
            x = maxX
        self.x1 = x

    def _scaleSW(self, x, y, minSep, maxSep):
        if y - self.y0 < MIN_HEIGHT:
            y = self.y0 + MIN_HEIGHT
        if y < maxSep + SEPARATOR_PAD:
            y = maxSep + SEPARATOR_PAD
        maxY = self._maxChildY()
        if y < maxY:
            y = maxY
        self.y1 = y
        if self.x1 - x < MIN_WIDTH:
            x = self.x1 - MIN_WIDTH
        minX = self._minChildX()
        if x > minX:
            x = minX
        self.x0 = x

    def _scaleSE(self, x, y, minSep, maxSep):
        if y - self.y0 < MIN_HEIGHT:
            y = self.y0 + MIN_HEIGHT
        if y < maxSep + SEPARATOR_PAD:
            y = maxSep + SEPARATOR_PAD
        maxY = self._maxChildY()
        if y < maxY:
            y = maxY
        self.y1 = y
        if x - self.x0 < MIN_WIDTH:
            x = self.x0 + MIN_WIDTH
        maxX = self._maxChildX()
        if x < maxX:
            x = maxX
        self.x1 = x

    def updateDisplay(self):
        for part in self.parts:
            part.updateDisplay()
        for sep in self.separators:
            sep.updateDisplay()
        for state in self.states:
            state.updateDisplay()

    def isPointInside(self,x,y):
        # check box
        if x < self.x0:
            return 0
        if x > self.x1:
            return 0
        if y < self.y0:
            return 0
        if y > self.y1:
            return 0
        # check four corners
        if x < self.x0 + RADIUS and y < self.y0 + RADIUS:
            dx = self.x0 + RADIUS - x
            dy = self.y0 - y
            if dx*dx+dy*dy > RADIUS*RADIUS:
                return 0
        if x > self.x1 - RADIUS and y < self.y0 + RADIUS:
            dx = self.x1 - RADIUS - x
            dy = self.y0 + RADIUS - y
            if dx*dx+dy*dy > RADIUS*RADIUS:
                return 0
        if x < self.x0 + RADIUS and y > self.y1 - RADIUS:
            dx = self.x0 + RADIUS - x
            dy = self.y1 - RADIUS - y
            if dx*dx+dy*dy > RADIUS*RADIUS:
                return 0
        if x > self.x1 - RADIUS and y > self.y1 - RADIUS:
            dx = self.x1 - RADIUS - x
            dy = self.y1 - RADIUS - y
            if dx*dx+dy*dy > RADIUS*RADIUS:
                return 0
        return 1

    def addStateAt(self, x,y):
	x0 = x
	x1 = x+MIN_WIDTH
	y0 = y
	y1 = y+MIN_HEIGHT
	# check that state is inside
	if not self._isStateInside(x0,y0,x1,y1):
            return None
        # check for intersections with separators
	for sep in self.separators:
            sepy = sep.getY()
	    if sepy >= y0 and sepy <= y1:
	        return None
	# check for intersections with other states
	for s in self.states:
            if s.intersectStateAt(x0,y0,x1,y1):
		return None
##        newState = State(x,y,self._getFreeName(x,y),self,self.handler,[],[],ds=1)
##        newState = State(x,y,self._getFreeName(x,y),self,self.handler,[],[],width=MIN_WIDTH, height=MIN_HEIGH*3,ds=1)
        newState = State(x,y,self._getFreeName(x,y),self,self.handler,[],[],width=MIN_WIDTH, height=500,ds=1)
        self.states.append(newState)
        componentNew = self.getComponentNumber(newState)
        for s in self.states:
            # if already a state in that component
            if self.getComponentNumber(s) == componentNew and s != newState:
                # not default state
                newState.setDS(0)
	return newState

    # return 1 iff I am this state or it is one
    # of my child states
    def belongsToThis(self,state):
        if state == self:
            return 1
        for s in self.states:
            if s.belongsToThis(state):
                return 1
        return 0

    def removeChild(self, state):
	self.states.remove(state)
        state.setCanvas(None)

    def removeSeparator(self, sep):
	self.separators.remove(sep)
        sep.setCanvas(None)

    def intersectStateAt(self,x0,y0,x1,y1):
    	"""return 1 iff this state intersects the
	   state at x0,y0,x1,y1"""
	intersectX = 0
	intersectY = 0
        if x0 > self.x0 and x0 < self.x1:
             intersectX = 1
        if x1 > self.x0 and x1 < self.x1:
             intersectX = 1
        if self.x0 > x0 and self.x0 < x1:
             intersectX = 1
        if self.x1 > x0 and self.x1 < x1:
             intersectX = 1
        if y0 > self.y0 and y0 < self.y1:
             intersectY = 1
        if y1 > self.y0 and y1 < self.y1:
             intersectY = 1
        if self.y0 > y0 and self.y0 < y1:
             intersectY = 1
        if self.y1 > y0 and self.y1 < y1:
             intersectY = 1
        return intersectX and intersectY

    def hasLegalPosition(self,child):
        if not self._isStateInside(child.x0,child.y0,child.x1,child.y1):
            return 0
        for s in self.states:
            if s != child and s.intersectStateAt(child.x0,child.y0,child.x1,child.y1):
                return 0
        for sep in self.separators:
            y = sep.getY()
            if y > child.y0 and y < child.y1:
                return 0
        return 1

    def isStateMine(self, child):
        if self == child:
            return 1
        for s in self.states:
            if s.isStateMine(child):
                return 1
        return 0

    def _isStateInside(self, x0,y0,x1,y1):
        x = x0 + RADIUS
        y = y0 + RADIUS
        if not self._isCircleInside(x,y):
            return 0
        x = x1 - RADIUS
        y = y0 + RADIUS
        if not self._isCircleInside(x,y):
            return 0
        x = x0 + RADIUS
        y = y1 - RADIUS
        if not self._isCircleInside(x,y):
            return 0
        x = x1 - RADIUS
        y = y1 - RADIUS
        if not self._isCircleInside(x,y):
            return 0
        return 1

    # circle with a radius of RADIUS
    def _isCircleInside(self,x,y):
        # check box
        if x < self.x0 + RADIUS: 
            return 0
        if x > self.x1 - RADIUS:
            return 0
        if y < self.y0 + RADIUS:
            return 0
        if y > self.y1 - RADIUS:
            return 0
        return 1

    def getStateAtXY(self, x, y):
        if not self.isPointInside(x,y):
            return None
        for state in self.states:
            s = state.getStateAtXY(x,y)
            if s != None:
                return s
        return self

    def getBorderPoint(self, x, y):
	ux,uy = self._getUnitVector(x,y)
        if self.getFS() == 1:
            bx = (self.x0 + self.x1)/2 + ux*FINAL_OUT_RADIUS
            by = (self.y0 + self.y1)/2 + uy*FINAL_OUT_RADIUS
            return bx,by
	intersect,bx,by = self._getLeftIntersect(ux,uy)
        if intersect:
            return bx,by
	intersect,bx,by = self._getRightIntersect(ux,uy)
        if intersect:
            return bx,by
	intersect,bx,by = self._getTopIntersect(ux,uy)
        if intersect:
            return bx,by
	intersect,bx,by = self._getBottomIntersect(ux,uy)
        if intersect:
            return bx,by

    def _getUnitVector(self,x,y):
        midx = (self.x0 + self.x1)/2
        midy = (self.y0 + self.y1)/2
	ux = float(x - midx)
        uy = float(y - midy)
	d = math.sqrt(float(ux*ux+uy*uy))
        if d < 0.01:
            return (1.,0.)
	return ux/d,uy/d
   
    def _getLeftIntersect(self,ux,uy):
       if ux > -0.01: # no chance
           return (None,0,0)
       by = (self.y1+self.y0)/2 - uy*(self.x1 - self.x0)/(2*ux)
       if by < self.y0:
           return (0,0,0)
       if by > self.y1:
           return (0,0,0)
       if by < self.y0 + RADIUS:
           by = self.y0 + RADIUS
       if by > self.y1 - RADIUS:
           by = self.y1 - RADIUS
       return (1,self.x0,by)

    def _getRightIntersect(self,ux,uy):
       if ux < 0.01: # no chance
           return (0,0,0)
       by = (self.y1+self.y0)/2 + uy*(self.x1 - self.x0)/(2*ux)
       if by < self.y0:
           return (0,0,0)
       if by > self.y1:
           return (0,0,0)
       if by < self.y0 + RADIUS:
           by = self.y0 + RADIUS
       if by > self.y1 - RADIUS:
           by = self.y1 - RADIUS
       return (1,self.x1,by)

    def _getTopIntersect(self,ux,uy):
       if uy > -0.01: # no chance
           return (None,0,0)
       bx = (self.x1+self.x0)/2 - ux*(self.y1 - self.y0)/(2*uy)
       if bx < self.x0:
           return (0,0,0)
       if bx > self.x1:
           return (0,0,0)
       if bx < self.x0 + RADIUS:
           bx = self.x0 + RADIUS
       if bx > self.x1 - RADIUS:
           bx = self.x1 - RADIUS
       return (1,bx,self.y0)

    def _getBottomIntersect(self,ux,uy):
       if uy < 0.01: # no chance
           return (None,0,0)
       bx = (self.x1+self.x0)/2 + ux*(self.y1 - self.y0)/(2*uy)
       if bx < self.x0:
           return (0,0,0)
       if bx > self.x1:
           return (0,0,0)
       if bx < self.x0 + RADIUS:
           bx = self.x0 + RADIUS
       if bx > self.x1 - RADIUS:
           bx = self.x1 - RADIUS
       return (1,bx,self.y1)

    def intersectY(self, y):
        if y < self.y0:
            return 0
        if y > self.y1:
            return 0
        return 1

    def addSeparator(self, y):
        if y < self.y0 + SEPARATOR_PAD:
            return None
        if y > self.y1 - SEPARATOR_PAD:
            return None
        for state in self.states:
            if state.intersectY(y):
                return None
        newSep = Separator(self, y, self.handler)
        self.separators.append(newSep)
	return newSep

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

    def setChildAsDefault(self, state):
	for s in self.states:
	    if self._sameComponent(s,state):
                s.setDS(0)
        state.setDS(1)

    def _sameComponent(self,state1,state2):
        count1 = 0
        count2 = 0
        for sep in self.separators:
            y = sep.getY()
            if state1.y0 >= y and state2.y0 < y:
                return 0
            if state1.y0 < y and state2.y0 >= y:
                return 0
        return 1

class Background:
    def __init__(self, state, handler, color="white"):
	self.state = state
        self.color = color
        self.handler = handler
        self.canvas = None
	self.previous_fs = self.state.fs.get()

    def setCanvas(self, canvas):
        if self.canvas == None and canvas != None:
            self.canvas = canvas
            self._createItems()
            self._bindEvents()
        elif self.canvas != None and canvas == None:
            self._deleteItems()
            self.canvas = None

    def lift(self):
	if self.canvas == None:
	    return
        for item in self.items:
            self.canvas.lift(item)

    def setHandler(self, handler):
        self.handler = handler

    def updateDisplay(self):
        if self.canvas == None:
            return
	new_fs = self.state.fs.get()
	if self.previous_fs != new_fs:
	    self._deleteItems()
            self._createItems()
            self._bindEvents()
            self.previous_fs = new_fs
        s = self.state
	if new_fs != 1:
            self.canvas.coords(self.middle, s.x0+s.r,s.y0,s.x1-s.r, s.y1)
            self.canvas.coords(self.left, s.x0, s.y0+s.r,s.x0+s.r, s.y1-s.r)
            self.canvas.coords(self.right, s.x1-s.r, s.y0+s.r, s.x1, s.y1-s.r)
            self.canvas.coords(self.topLeft, s.x0, s.y0, s.x0+s.r*2, s.y0+s.r*2)
            self.canvas.coords(self.topRight, s.x1-s.r*2, s.y0, s.x1, s.y0+s.r*2)
            self.canvas.coords(self.bottomLeft, s.x0, s.y1-s.r*2, s.x0+s.r*2, s.y1)
            self.canvas.coords(self.bottomRight, s.x1-s.r*2, s.y1-s.r*2, s.x1, s.y1)

    def _createItems(self):
	self.previous_fs = self.state.fs.get()
	if self.previous_fs == 1:
            self.items = []
            return
        s = self.state
        #create items
        self.middle = self.canvas.create_rectangle(s.x0+s.r,s.y0,s.x1-s.r, s.y1, fill=self.color, width=0)
        self.left = self.canvas.create_rectangle(s.x0, s.y0+s.r,s.x0+s.r, s.y1-s.r, fill=self.color, width=0)
        self.right = self.canvas.create_rectangle(s.x1-s.r, s.y0+s.r, s.x1, s.y1-s.r, fill=self.color, width=0)
        xy = s.x0, s.y0, s.x0+s.r*2, s.y0+s.r*2
        self.topLeft = self.canvas.create_arc(xy, start=90, extent=90, fill=self.color, outline=self.color)
        xy = s.x1-s.r*2, s.y0, s.x1, s.y0+s.r*2
        self.topRight = self.canvas.create_arc(xy, start=0, extent=90, fill=self.color, outline=self.color)
        xy = s.x0, s.y1-s.r*2, s.x0+s.r*2, s.y1
        self.bottomLeft = self.canvas.create_arc(xy, start=180, extent=90, fill=self.color, outline=self.color)
        xy = s.x1-s.r*2, s.y1-s.r*2, s.x1, s.y1
        self.bottomRight = self.canvas.create_arc(xy, start=270, extent=90, fill=self.color, outline=self.color)
        self.items = [self.middle, self.left, self.right, self.topLeft, self.topRight, self.bottomLeft, self.bottomRight]
        self.corners = [self.topLeft, self.topRight, self.bottomLeft, self.bottomRight]

    def _deleteItems(self):
        for item in self.items:
            self.canvas.delete(item)
        self.items = None
        self.corner = None

    def _bindEvents(self):
        for item in self.items:
            self.canvas.tag_bind(item, "<Button-1>", self.onButton1)
            self.canvas.tag_bind(item, "<Button-3>", self.onButton3)
            self.canvas.tag_bind(item, "<Double-Button-1>", self.onDoubleButton1)
            self.canvas.tag_bind(item, "<Double-Button-3>", self.onDoubleButton3)
            self.canvas.tag_bind(item, "<B1-Motion>", self.onButtonMotion1)
            self.canvas.tag_bind(item, "<B3-Motion>", self.onButtonMotion3)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.onButtonRelease1)
            self.canvas.tag_bind(item, "<ButtonRelease-3>", self.onButtonRelease3)

    def onButton1(self, event):
        self.handler.onStateButton1(self.state, event)

    def onButton3(self, event):
        self.handler.onStateButton3(self.state, event)

    def onDoubleButton1(self, event):
        self.handler.onStateDoubleButton1(self.state, event)

    def onDoubleButton3(self, event):
        self.handler.onStateDoubleButton3(self.state, event)

    def onButtonMotion1(self, event):
        self.handler.onStateButtonMotion1(self.state, event)

    def onButtonMotion3(self, event):
        self.handler.onStateButtonMotion3(self.state, event)

    def onButtonRelease1(self, event):
        self.handler.onStateButtonRelease1(self.state, event)

    def onButtonRelease3(self, event):
        self.handler.onStateButtonRelease3(self.state, event)



class Border:
    WIDTH = 2
    def __init__(self, state, handler, color="black"):
	self.state = state
        self.color = color
        self.canvas = None
        self.handler = handler
	self.previous_fs = self.state.fs.get()

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
        new_fs = self.state.fs.get()
	if self.previous_fs != new_fs:
	    self._deleteItems()
            self._createItems()
            self._bindEvents()
	    self.previous_fs = new_fs
	if new_fs != 1:
            s = self.state
            self.canvas.coords(self.N, s.x0+s.r-1,s.y0,s.x1-s.r+1,s.y0)
            self.canvas.coords(self.W, s.x0, s.y0+s.r-1, s.x0, s.y1-s.r+1)
            self.canvas.coords(self.E, s.x1,s.y0+s.r-1,s.x1,s.y1-s.r+1)
            self.canvas.coords(self.S, s.x0+s.r-1,s.y1,s.x1-s.r+1,s.y1)
            xy = s.x0, s.y0, s.x0+s.r*2, s.y0+s.r*2
            self.canvas.coords(self.NW, xy)
            xy = s.x1-s.r*2, s.y0, s.x1, s.y0+s.r*2
            self.canvas.coords(self.NE, xy)
            xy = s.x0, s.y1-s.r*2, s.x0+s.r*2, s.y1
            self.canvas.coords(self.SW, xy)
            xy = s.x1-s.r*2, s.y1-s.r*2, s.x1, s.y1
            self.canvas.coords(self.SE, xy)
            for edge in self.edges:
                self.canvas.itemconfig(edge, fill=self.state.borderColor)
            for corner in self.corners:
                self.canvas.itemconfig(corner, outline=self.state.borderColor)

    def lift(self):
	if self.canvas == None:
	    return
        for item in self.items:
            self.canvas.lift(item)

    def setHandler(self, handler):
        self.handler = handler

    def _createItems(self):
	self.previous_fs = self.state.fs.get()
	if self.previous_fs == 1:
            self.items = []
            return
        s = self.state
        self.N = self.canvas.create_line(s.x0+s.r-1,s.y0,s.x1-s.r+1,s.y0, width=Border.WIDTH, fill=self.state.borderColor)
        self.W = self.canvas.create_line(s.x0, s.y0+s.r-1, s.x0, s.y1-s.r+1, width=Border.WIDTH, fill=self.state.borderColor)
        self.E = self.canvas.create_line(s.x1,s.y0+s.r-1,s.x1,s.y1-s.r+1, width=Border.WIDTH, fill=self.state.borderColor)
        self.S = self.canvas.create_line(s.x0+s.r-1,s.y1,s.x1-s.r+1,s.y1, width=Border.WIDTH, fill=self.state.borderColor)
        xy = s.x0, s.y0, s.x0+s.r*2, s.y0+s.r*2
        self.NW = self.canvas.create_arc(xy, start=90, extent=90, style=ARC, width=Border.WIDTH, outline=self.state.borderColor)
        xy = s.x1-s.r*2, s.y0, s.x1, s.y0+s.r*2
        self.NE = self.canvas.create_arc(xy, start=0, extent=90, style=ARC, width=Border.WIDTH, outline=self.state.borderColor)
        xy = s.x0, s.y1-s.r*2, s.x0+s.r*2, s.y1
        self.SW = self.canvas.create_arc(xy, start=180, extent=90, style=ARC, width=Border.WIDTH, outline=self.state.borderColor)
        xy = s.x1-s.r*2, s.y1-s.r*2, s.x1, s.y1
        self.SE = self.canvas.create_arc(xy, start=270, extent=90, style=ARC, width=Border.WIDTH, outline=self.state.borderColor)
        self.items = [self.N, self.S, self.E, self.W, self.NW, self.NE, self.SW, self.SE]
        self.edges = [self.N, self.S, self.E, self.W]
        self.corners = [self.NW, self.NE, self.SW, self.SE]

    def _deleteItems(self):
        for item in self.items:
            self.canvas.delete(item)
        self.edges = None
        self.corners = None

    def _make_onEnter(self, name):
        return lambda event: self.handler.onStateBorderEnter(self.state, name, event)

    def _make_onLeave(self, name):
        return lambda event: self.handler.onStateBorderLeave(self.state, name, event)

    def _make_onButton1(self, name):
        return lambda event: self.handler.onStateBorderButton1(self.state, name, event)

    def _make_onButtonMotion1(self, name):
        return lambda event: self.handler.onStateBorderButtonMotion1(self.state, name, event)

    def _make_onButtonRelease1(self, name):
        return lambda event: self.handler.onStateBorderButtonRelease1(self.state, name, event)

    def _bindEvents(self):
	if len(self.items) == 0:
            return
        # event bindings
        # north
        tuples = [(self.N, "N"), (self.S, "S"), (self.E, "E"), (self.W, "W"), (self.NW, "NW"), (self.NE, "NE"), (self.SW, "SW"), (self.SE, "SE")]
        for item, name in tuples:
            self.canvas.tag_bind(item, "<Enter>", self._make_onEnter(name))
            self.canvas.tag_bind(item, "<Leave>", self._make_onLeave(name))
            self.canvas.tag_bind(item, "<Button-1>", self._make_onButton1(name))
            self.canvas.tag_bind(item, "<B1-Motion>", self._make_onButtonMotion1(name))
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self._make_onButtonRelease1(name))



class Name:
    def __init__(self, state, name, handler):
        self.state = state
        self.name = name
        self.canvas = None
        self.handler = handler
	self.previous_fs = self.state.fs.get()

    def get(self):
        return self.name

    def set(self, name):
        self.name = name
        if self.canvas != None:
            self.canvas.itemconfig(self.item, text=self._truncatedName())

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
	new_fs = self.state.fs.get()
	if self.previous_fs != new_fs:
	    self._deleteItems()
            self._createItems()
            self._bindEvents()
            self.previous_fs = new_fs
	if new_fs != 1:
            s = self.state
            self.canvas.itemconfig(self.item, text=self._truncatedName(), fill=self.state.borderColor)
            self.canvas.coords(self.item, s.x0 +s.r,s.y0+10)

    def lift(self):
	if self.canvas == None or self.previous_fs == 1:
	    return
        self.canvas.lift(self.item)

    # only to avoid having pickle to save the handler...
    def setHandler(self, handler):
        self.handler = handler

    def _createItems(self):
	self.previous_fs = self.state.fs.get()
	if self.previous_fs == 1:
            self.item = None
            return
        s = self.state
        self.item = self.canvas.create_text(s.x0+s.r, s.y0+10, text=self._truncatedName(), anchor=W,fill=self.state.borderColor)

    def _truncatedName(self):
	testItem = self.canvas.create_text(-15,0)
	width = self.state.x1 - self.state.x0
        i = 0
        while i <= len(self.name):
	    self.canvas.itemconfig(testItem, text=self.name[0:i])
            x0,y0,x1,y1 = self.canvas.bbox(testItem)
	    if x1 - x0 + 23 < width:
                truncated = self.name[0:i]
            i = i + 1
	if len(truncated) < len(self.name):
	    truncated = truncated + "..."
	self.canvas.delete(testItem)
	return truncated

    def _deleteItems(self):
        self.canvas.delete(self.item)

    def _bindEvents(self):
	if self.item == None:
            return
        i = self.item
        self.canvas.tag_bind(i, "<Button-1>", self.onButton1)
        self.canvas.tag_bind(i, "<Button-3>", self.onButton3)
        self.canvas.tag_bind(i, "<Double-Button-1>", self.onDoubleButton1)
        self.canvas.tag_bind(i, "<Double-Button-3>", self.onDoubleButton3)
        self.canvas.tag_bind(i, "<B1-Motion>", self.onButtonMotion1)
        self.canvas.tag_bind(i, "<B3-Motion>", self.onButtonMotion3)
        self.canvas.tag_bind(i, "<ButtonRelease-1>", self.onButtonRelease1)
        self.canvas.tag_bind(i, "<ButtonRelease-3>", self.onButtonRelease3)

    def onButton1(self, event):
        self.handler.onStateButton1(self.state, event)

    def onButton3(self, event):
        self.handler.onStateButton3(self.state, event)

    def onDoubleButton1(self, event):
        self.handler.onStateDoubleButton1(self.state, event)

    def onDoubleButton3(self, event):
        self.handler.onStateDoubleButton3(self.state, event)

    def onButtonMotion1(self, event):
        self.handler.onStateButtonMotion1(self.state, event)

    def onButtonMotion3(self, event):
        self.handler.onStateButtonMotion3(self.state, event)

    def onButtonRelease1(self, event):
        self.handler.onStateButtonRelease1(self.state, event)

    def onButtonRelease3(self, event):
        self.handler.onStateButtonRelease3(self.state, event)



# indicate whether the state is a default
# state in its component
class DS:
    ARROW_WIDTH = 2
    def __init__(self, state, ds, handler):
	self.state = state
        self.ds = ds
	self.handler = handler # unused for now
        self.canvas = None
	self.previous_fs = self.state.fs.get()

    def get(self):
        return self.ds

    def set(self, ds):
        self.ds = ds
        if self.canvas != None:
            self._deleteItems()
            self._createItems()

    def setCanvas(self, canvas):
        if self.canvas == None and canvas != None:
            self.canvas = canvas
            self._createItems()
        elif self.canvas != None and canvas == None:
            self._deleteItems()
            self.canvas = None

    def lift(self):
	if self.canvas == None:
	    return
        for item in self.items:
            self.canvas.lift(item)

    def setHandler(self, handler):
        self.handler = handler

    def updateDisplay(self):
	new_fs = self.state.fs.get()
	if self.previous_fs != new_fs:
	    self._deleteItems()
            self._createItems()
            self._bindEvents()
            self.previous_fs = new_fs
        if self.canvas == None:
            return
        s = self.state
	if self.ds == 1 and new_fs != 1:
            self.canvas.coords(self.arrow, s.x0+s.r/2, s.y0-s.r-5, s.x0+s.r, s.y0-s.r, s.x0+s.r, s.y0)
            self.canvas.coords(self.dot, s.x0+s.r/2-3, s.y0-s.r-8, s.x0+s.r/2+3, s.y0-s.r-2)
            self.canvas.itemconfig(self.arrow, fill=self.state.borderColor)
            self.canvas.itemconfig(self.dot, fill=self.state.borderColor)
            self.canvas.itemconfig(self.dot, outline=self.state.borderColor)


    def _createItems(self):
	self.previous_fs = self.state.fs.get()
        #create items
	if self.previous_fs == 1:
            self.items = []
            return
        if self.ds == 1:
            s = self.state
            self.arrow = self.canvas.create_line([s.x0+s.r/2, s.y0-s.r-5, s.x0+s.r, s.y0-s.r, s.x0+s.r, s.y0], width=DS.ARROW_WIDTH, arrow=LAST, smooth=1)
            self.dot = self.canvas.create_oval(s.x0+s.r/2-3, s.y0-s.r-8, s.x0+s.r/2+3, s.y0-s.r-2, fill=self.state.borderColor)
            self.items = [self.arrow, self.dot]
        else:
            self.items = []

    def _deleteItems(self):
        for item in self.items:
            self.canvas.delete(item)
        self.items = None

    def _bindEvents(self):
        pass

# state history support
class HS:
    def __init__(self, state, hs, handler):
	self.state = state
        self.hs = hs
        self.canvas = None
        self.handler = handler
	self.previous_fs = self.state.fs.get()

    def get(self):
        return self.hs

    def set(self, hs):
        self.hs = hs
        if self.canvas != None:
            self._deleteItems()
            self._createItems()
	    self._bindEvents()

    def setCanvas(self, canvas):
        if self.canvas == None and canvas != None:
            self.canvas = canvas
            self._createItems()
	    self._bindEvents()
        elif self.canvas != None and canvas == None:
            self._deleteItems()
            self.canvas = None

    def lift(self):
	if self.canvas == None:
	    return
        for item in self.items:
            self.canvas.lift(item)

    def setHandler(self, handler):
        self.handler = handler

    def updateDisplay(self):
        if self.canvas == None:
            return
	new_fs = self.state.fs.get()
	if self.previous_fs != new_fs:
	    self._deleteItems()
            self._createItems()
            self._bindEvents()
            self.previous_fs = new_fs
	if new_fs != 1:
            s = self.state
            self.canvas.itemconfig(self.text, fill=self.state.borderColor)
            self.canvas.coords(self.text, s.x1-s.r+2, s.y1-s.r+2)
#          self.canvas.itemconfig(self.circle, outline=color)
#        self.canvas.coords(self.circle, s.x1-s.r - 8, s.y0+s.r - 7, s.x1-s.r + 7, s.y0+s.r + 7)

    def _createItems(self):
	self.previous_fs = self.state.fs.get()
	if self.previous_fs == 1:
            self.items = []
            return
	if self.hs == NO_HS:
            hs_text = ""
        elif self.hs == ONE_HS:
            hs_text = "H"
        else: # DEEP_HS
            hs_text = "H*"
        s = self.state
        self.text = self.canvas.create_text(s.x1-s.r+2, s.y1-s.r+2, text=hs_text, anchor=CENTER, fill=self.state.borderColor)
 #       self.circle = self.canvas.create_oval(s.x1-s.r - 8, s.y0+s.r - 7, s.x1-s.r + 7, s.y0+s.r + 7, width = 1)
        self.items = [self.text]#, self.circle]

    def _bindEvents(self):
        for item in self.items:
            self.canvas.tag_bind(item, "<Button-1>", self.onButton1)
            self.canvas.tag_bind(item, "<Button-3>", self.onButton3)
            self.canvas.tag_bind(item, "<Double-Button-1>", self.onDoubleButton1)
            self.canvas.tag_bind(item, "<Double-Button-3>", self.onDoubleButton3)
            self.canvas.tag_bind(item, "<B1-Motion>", self.onButtonMotion1)
            self.canvas.tag_bind(item, "<B3-Motion>", self.onButtonMotion3)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.onButtonRelease1)
            self.canvas.tag_bind(item, "<ButtonRelease-3>", self.onButtonRelease3)

    def onButton1(self, event):
        self.handler.onStateButton1(self.state, event)

    def onButton3(self, event):
        self.handler.onStateButton3(self.state, event)

    def onDoubleButton1(self, event):
        self.handler.onStateDoubleButton1(self.state, event)

    def onDoubleButton3(self, event):
        self.handler.onStateDoubleButton3(self.state, event)

    def onButtonMotion1(self, event):
        self.handler.onStateButtonMotion1(self.state, event)

    def onButtonMotion3(self, event):
        self.handler.onStateButtonMotion3(self.state, event)

    def onButtonRelease1(self, event):
        self.handler.onStateButtonRelease1(self.state, event)

    def onButtonRelease3(self, event):
        self.handler.onStateButtonRelease3(self.state, event)

    def _deleteItems(self):
        for item in self.items:
            self.canvas.delete(item)
        self.items = None




# appearance of the state when it is final
class FS:
    def __init__(self, state, fs, handler):
	self.state = state
        self.fs = fs
        self.canvas = None
	self.handler = handler

    def get(self):
        return self.fs

    def set(self, fs):
	old_fs = self.fs
        self.fs = fs
        if self.canvas != None and self.fs != old_fs:
            self._deleteItems()
            self._createItems()
            self._bindEvents()

    def lift(self):
	if self.canvas == None:
	    return
        for item in self.items:
            self.canvas.lift(item)

    def setHandler(self, handler):
        self.handler = handler

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
	if self.previous_fs != self.state.fs.get():
	    self._deleteItems()
            self._createItems()
            self._bindEvents()
	    self.previous_fs = self.fs
        s = self.state
	if self.fs == 1:
            s = self.state
            x0 = (s.x0 + s.x1)/2 - FINAL_OUT_RADIUS
            y0 = (s.y0 + s.y1)/2 - FINAL_OUT_RADIUS
            x1 = (s.x0 + s.x1)/2 + FINAL_OUT_RADIUS
            y1 = (s.y0 + s.y1)/2 + FINAL_OUT_RADIUS
            self.canvas.coords(self.circle,x0,y0,x1,y1)
            x0 = (s.x0 + s.x1)/2 - FINAL_IN_RADIUS
            y0 = (s.y0 + s.y1)/2 - FINAL_IN_RADIUS
            x1 = (s.x0 + s.x1)/2 + FINAL_IN_RADIUS
            y1 = (s.y0 + s.y1)/2 + FINAL_IN_RADIUS
            self.canvas.coords(self.dot,x0,y0,x1,y1)
            self.canvas.itemconfig(self.circle, outline=self.state.borderColor)
            self.canvas.itemconfig(self.dot, fill=self.state.borderColor,outline=self.state.borderColor)


    def _createItems(self):
        #create items
	self.previous_fs = self.state.fs.get()
        if self.fs == 1:
            s = self.state
            x0 = (s.x0 + s.x1)/2 - FINAL_OUT_RADIUS
            y0 = (s.y0 + s.y1)/2 - FINAL_OUT_RADIUS
            x1 = (s.x0 + s.x1)/2 + FINAL_OUT_RADIUS
            y1 = (s.y0 + s.y1)/2 + FINAL_OUT_RADIUS
            self.circle = self.canvas.create_oval(x0,y0,x1,y1, fill="white", outline=self.state.borderColor)
            x0 = (s.x0 + s.x1)/2 - FINAL_IN_RADIUS
            y0 = (s.y0 + s.y1)/2 - FINAL_IN_RADIUS
            x1 = (s.x0 + s.x1)/2 + FINAL_IN_RADIUS
            y1 = (s.y0 + s.y1)/2 + FINAL_IN_RADIUS
            self.dot = self.canvas.create_oval(x0,y0,x1,y1, fill=self.state.borderColor)
            self.items = [self.circle, self.dot]
        else:
            self.items = []

    def _bindEvents(self):
        for item in self.items:
            self.canvas.tag_bind(item, "<Button-1>", self.onButton1)
            self.canvas.tag_bind(item, "<Button-3>", self.onButton3)
            self.canvas.tag_bind(item, "<Double-Button-1>", self.onDoubleButton1)
            self.canvas.tag_bind(item, "<Double-Button-3>", self.onDoubleButton3)
            self.canvas.tag_bind(item, "<B1-Motion>", self.onButtonMotion1)
            self.canvas.tag_bind(item, "<B3-Motion>", self.onButtonMotion3)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.onButtonRelease1)
            self.canvas.tag_bind(item, "<ButtonRelease-3>", self.onButtonRelease3)

    def onButton1(self, event):
        self.handler.onStateButton1(self.state, event)

    def onButton3(self, event):
        self.handler.onStateButton3(self.state, event)

    def onDoubleButton1(self, event):
        self.handler.onStateDoubleButton1(self.state, event)

    def onDoubleButton3(self, event):
        self.handler.onStateDoubleButton3(self.state, event)

    def onButtonMotion1(self, event):
        self.handler.onStateButtonMotion1(self.state, event)

    def onButtonMotion3(self, event):
        self.handler.onStateButtonMotion3(self.state, event)

    def onButtonRelease1(self, event):
        self.handler.onStateButtonRelease1(self.state, event)

    def onButtonRelease3(self, event):
        self.handler.onStateButtonRelease3(self.state, event)

    def _deleteItems(self):
        for item in self.items:
            self.canvas.delete(item)
        self.items = None











