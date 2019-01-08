# basic layout

from view.display_model import DisplayModel


class LayoutBasic:
    def __init__(
        self,
        leftmargin=200,
        topmargin=230,
        verticalwhitespace=50,
        horizontalwhitespace=50,
        maxclassesperline=5,
    ):
        self.leftmargin = leftmargin
        self.topmargin = topmargin
        self.verticalwhitespace = verticalwhitespace
        self.horizontalwhitespace = horizontalwhitespace
        self.maxclassesperline = maxclassesperline

    def _getShapeSize(self, shape):
        """Return the size of a shape's representation, an abstraction point"""
        return shape.GetBoundingBoxMax()

    def _SortShapes(self, umlworkspace, umlboxshapes):
        priority1 = [
            parentclassname
            for (classname, parentclassname) in umlworkspace.associations_generalisation
        ]
        priority2 = [
            classname for (classname, parentclassname) in umlworkspace.associations_generalisation
        ]
        priority3 = [lhs for (rhs, lhs) in umlworkspace.associations_composition]
        priority4 = [rhs for (rhs, lhs) in umlworkspace.associations_composition]

        # convert classnames to shapes, avoid duplicating shapes.
        mostshapesinpriorityorder = []
        for classname in priority1 + priority2 + priority3 + priority4:

            if classname not in umlworkspace.classnametoshape:  # skip user deleted classes.
                continue

            shape = umlworkspace.classnametoshape[classname]
            if shape not in mostshapesinpriorityorder:
                mostshapesinpriorityorder.append(shape)

        # find and loose shapes not associated to anything
        remainingshapes = [
            shape for shape in umlboxshapes if shape not in mostshapesinpriorityorder
        ]

        # return list of sorted shapes
        return mostshapesinpriorityorder + remainingshapes

    def Layout(self, umlworkspace, umlboxshapes):

        shapeslist = self._SortShapes(umlworkspace, umlboxshapes)
        positions = []

        x = self.leftmargin
        y = self.topmargin

        biggestx = 0
        biggesty = 0

        biggestYthisrow = 0
        count = 0
        for classShape in shapeslist:
            count += 1
            if count == self.maxclassesperline:
                count = 0
                x = self.leftmargin
                y = y + biggestYthisrow + self.verticalwhitespace
                biggestYthisrow = 0

            width, height = self._getShapeSize(classShape)

            if height >= biggestYthisrow:
                biggestYthisrow = height

            positions.append((x, y))
            # print 'layout', classShape.region1.GetText(), (x,y)

            x = x + width + self.horizontalwhitespace
            if x > biggestx:
                biggestx = x

        biggesty = y + biggestYthisrow + self.verticalwhitespace

        assert len(positions) == len(shapeslist)

        newdiagramsize = (int(biggestx), int(biggesty))
        return positions, shapeslist, newdiagramsize


if __name__ == "__main__":

    class Shape:
        def GetBoundingBoxMax(self):
            return 10, 10

    layout = LayoutBasic(
        leftmargin=0, topmargin=0, verticalwhitespace=0, horizontalwhitespace=0, maxclassesperline=5
    )
    umlworkspace = DisplayModel()
    umlboxshapes = [Shape(), Shape(), Shape()]
    positions, shapeslist, newdiagramsize = layout.Layout(umlworkspace, umlboxshapes)
    print("positions", positions)
    # print "shapeslist", shapeslist
    print("newdiagramsize", newdiagramsize)
    assert positions == [(0, 0), (10, 0), (20, 0)]
    assert newdiagramsize == (30, 10)

    umlboxshapes = [Shape(), Shape(), Shape(), Shape(), Shape(), Shape()]
    positions, shapeslist, newdiagramsize = layout.Layout(umlworkspace, umlboxshapes)
    print("positions", positions)
    # print "shapeslist", shapeslist
    print("newdiagramsize", newdiagramsize)
    assert positions == [(0, 0), (10, 0), (20, 0), (30, 0), (0, 10), (10, 10)]
    assert newdiagramsize == (40, 20)
