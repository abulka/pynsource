# basic layout

class LayoutBasic:

    def getShapeSize( self, shape ):
        """Return the size of a shape's representation, an abstraction point"""
        return shape.GetBoundingBoxMax()
    
    def SortShapes(self, umlworkspace):
        priority1 = [parentclassname for (classname, parentclassname) in umlworkspace.associations_generalisation ]
        priority2 = [classname       for (classname, parentclassname) in umlworkspace.associations_generalisation ]
        priority3 = [lhs            for (rhs, lhs) in umlworkspace.associations_composition ]
        priority4 = [rhs             for (rhs, lhs) in umlworkspace.associations_composition ]
    
        # convert classnames to shapes, avoid duplicating shapes.
        mostshapesinpriorityorder = []
        for classname in (priority1 + priority2 + priority3 + priority4):
    
            if classname not in umlworkspace.classnametoshape:  # skip user deleted classes.
                continue
    
            shape = umlworkspace.classnametoshape[classname]
            if shape not in mostshapesinpriorityorder:
                mostshapesinpriorityorder.append(shape)
    
        # find and loose shapes not associated to anything
        remainingshapes = [ shape for shape in umlworkspace.umlboxshapes if shape not in mostshapesinpriorityorder ]
    
        # return list of sorted shapes
        return mostshapesinpriorityorder + remainingshapes
    
    def Layout(self, umlworkspace):
        shapeslist = self.SortShapes(umlworkspace)
    
        # When look at the status bar whilst dragging UML shapes, the coords of the top left are
        # this.  This is different to what you see when mouse dragging on the canvas - there you DO get 0,0
        # Perhaps one measurement takes into account the menubar and the other doesn't.  Dunno.
        # UPDATE!!!! - it depends onteh size of the class you are dragging - get different values!
        LEFTMARGIN = 200
        TOPMARGIN = 230
    
        positions = []
    
        x = LEFTMARGIN
        y = TOPMARGIN
    
        maxx = 0
        biggestYthisrow = 0
        verticalWhiteSpace = 50
        count = 0
        for classShape in shapeslist:
            count += 1
            if count == 5:
                count = 0
                x = LEFTMARGIN
                y = y + biggestYthisrow + verticalWhiteSpace
                biggestYthisrow = 0
    
            whiteSpace = 50
            shapeX, shapeY = self.getShapeSize(classShape)
    
            if shapeY >= biggestYthisrow:
                biggestYthisrow = shapeY
    
            # snap to diagram grid coords
            #csX, csY = self.GetDiagram().Snap((shapeX/2.0)+x, (shapeY/2.0)+y)
            #csX, csY = self.GetDiagram().Snap(x, y)
            # don't display until finished
            positions.append((x,y))
    
            #print 'layout', classShape.region1.GetText(), (x,y)
    
            x = x + shapeX + whiteSpace
            if x > maxx:
                maxx = x + 300
    
        assert len(positions) == len(shapeslist)
    
        # Calculate new size of entire diagram.
        height = y + 500
        width = maxx
        newdiagramsize = (int(width+50), int(height+50)) # fudge factors to keep some extra space
        print "newdiagramsize", newdiagramsize
        
        return positions, shapeslist, newdiagramsize
