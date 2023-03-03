import math
from gui.settings import PRO_EDITION, LOCAL_OGL
import wx
import sys

if PRO_EDITION:
    # import ogl
    from ogl2 import LineShape
    from ogl2 import GetPointOnLine
    from ogl2 import GetArrowPoints
    from ogl2 import ARROW_POSITION_START
    from ogl2 import ARROW_POSITION_MIDDLE
    from ogl2 import ARROW_POSITION_END

    from ogl2 import ARROW_HOLLOW_CIRCLE
    from ogl2 import ARROW_FILLED_CIRCLE
    from ogl2 import ARROW_ARROW
    from ogl2 import ARROW_SINGLE_OBLIQUE
    from ogl2 import ARROW_DOUBLE_OBLIQUE
    from ogl2 import ARROW_METAFILE

    from ogl2 import ShapeRegion, RectangleShape, Selectable
else:
    if LOCAL_OGL:
        from ogl import LineShape
        from ogl import GetPointOnLine
        from ogl import GetArrowPoints
        from ogl import ARROW_POSITION_START
        from ogl import ARROW_POSITION_MIDDLE
        from ogl import ARROW_POSITION_END
        from ogl import ARROW_HOLLOW_CIRCLE
        from ogl import ARROW_FILLED_CIRCLE
        from ogl import ARROW_ARROW
        from ogl import ARROW_SINGLE_OBLIQUE
        from ogl import ARROW_DOUBLE_OBLIQUE
        from ogl import ARROW_METAFILE
    else:
        from wx.lib.ogl import LineShape
        from wx.lib.ogl import GetPointOnLine
        from wx.lib.ogl import GetArrowPoints
        from wx.lib.ogl import ARROW_POSITION_START
        from wx.lib.ogl import ARROW_POSITION_MIDDLE
        from wx.lib.ogl import ARROW_POSITION_END
        from wx.lib.ogl import ARROW_HOLLOW_CIRCLE
        from wx.lib.ogl import ARROW_FILLED_CIRCLE
        from wx.lib.ogl import ARROW_ARROW
        from wx.lib.ogl import ARROW_SINGLE_OBLIQUE
        from wx.lib.ogl import ARROW_DOUBLE_OBLIQUE
        from wx.lib.ogl import ARROW_METAFILE

# Custom styles
ARROW_UML_GENERALISATION = 200
ARROW_UML_COMPOSITION = 201
ARROW_UML_AGGREGATION = 202


class LineShapeUml(LineShape):
    """
    Custom lines for UML purposes
    Entire DrawArrow() method replicated here, and enhanced
    """

    def __init__(self):
        LineShape.__init__(self)

    def DrawArrow(self, dc, arrow, XOffset, proportionalOffset):
        """Draw the given arrowhead (or annotation)."""
        first_line_point = self._lineControlPoints[0]
        second_line_point = self._lineControlPoints[1]

        last_line_point = self._lineControlPoints[-1]
        second_last_line_point = self._lineControlPoints[-2]

        # Position of start point of line, at the end of which we draw the arrow
        startPositionX, startPositionY = 0.0, 0.0

        ap = arrow.GetPosition()
        if ap == ARROW_POSITION_START:
            # If we're using a proportional offset, calculate just where this
            # will be on the line.
            realOffset = XOffset
            if proportionalOffset:
                totalLength = math.sqrt(
                    (second_line_point[0] - first_line_point[0])
                    * (second_line_point[0] - first_line_point[0])
                    + (second_line_point[1] - first_line_point[1])
                    * (second_line_point[1] - first_line_point[1])
                )
                realOffset = XOffset * totalLength

            positionOnLineX, positionOnLineY = GetPointOnLine(
                second_line_point[0],
                second_line_point[1],
                first_line_point[0],
                first_line_point[1],
                realOffset,
            )

            startPositionX = second_line_point[0]
            startPositionY = second_line_point[1]
        elif ap == ARROW_POSITION_END:
            # If we're using a proportional offset, calculate just where this
            # will be on the line.
            realOffset = XOffset
            if proportionalOffset:
                totalLength = math.sqrt(
                    (second_last_line_point[0] - last_line_point[0])
                    * (second_last_line_point[0] - last_line_point[0])
                    + (second_last_line_point[1] - last_line_point[1])
                    * (second_last_line_point[1] - last_line_point[1])
                )
                realOffset = XOffset * totalLength

            positionOnLineX, positionOnLineY = GetPointOnLine(
                second_last_line_point[0],
                second_last_line_point[1],
                last_line_point[0],
                last_line_point[1],
                realOffset,
            )

            startPositionX = second_last_line_point[0]
            startPositionY = second_last_line_point[1]
        elif ap == ARROW_POSITION_MIDDLE:
            # Choose a point half way between the last and penultimate points
            x = (last_line_point[0] + second_last_line_point[0]) / 2.0
            y = (last_line_point[1] + second_last_line_point[1]) / 2.0

            # If we're using a proportional offset, calculate just where this
            # will be on the line.
            realOffset = XOffset
            if proportionalOffset:
                totalLength = math.sqrt(
                    (second_last_line_point[0] - x) * (second_last_line_point[0] - x)
                    + (second_last_line_point[1] - y) * (second_last_line_point[1] - y)
                )
                realOffset = XOffset * totalLength

            positionOnLineX, positionOnLineY = GetPointOnLine(
                second_last_line_point[0], second_last_line_point[1], x, y, realOffset
            )
            startPositionX = second_last_line_point[0]
            startPositionY = second_last_line_point[1]

        # Add yOffset to arrow, if any

        # The translation that the y offset may give
        deltaX = 0.0
        deltaY = 0.0
        if arrow.GetYOffset and not self._ignoreArrowOffsets:
            #                             |(x4, y4)
            #                             |d
            #                             |
            #   (x1, y1)--------------(x3, y3)------------------(x2, y2)
            #   x4 = x3 - d * math.sin(theta)
            #   y4 = y3 + d * math.cos(theta)
            #
            #   Where theta = math.tan(-1) of (y3-y1) / (x3-x1)
            x1 = startPositionX
            y1 = startPositionY
            x3 = float(positionOnLineX)
            y3 = float(positionOnLineY)
            d = -arrow.GetYOffset()  # Negate so +offset is above line

            if x3 == x1:
                theta = math.pi / 2.0
            else:
                theta = math.atan((y3 - y1) / (x3 - x1))

            x4 = x3 - d * math.sin(theta)
            y4 = y3 + d * math.cos(theta)

            deltaX = x4 - positionOnLineX
            deltaY = y4 - positionOnLineY

        at = arrow._GetType()
        if at == ARROW_ARROW:
            arrowLength = arrow.GetSize()
            arrowWidth = arrowLength / 3.0

            tip_x, tip_y, side1_x, side1_y, side2_x, side2_y = GetArrowPoints(
                startPositionX + deltaX,
                startPositionY + deltaY,
                positionOnLineX + deltaX,
                positionOnLineY + deltaY,
                arrowLength,
                arrowWidth,
            )

            points = [[tip_x, tip_y], [side1_x, side1_y], [side2_x, side2_y], [tip_x, tip_y]]

            dc.SetPen(self._pen)
            dc.SetBrush(self._brush)

            # convert all points to integers - fix needed for Python 3.10
            points = [[int(x), int(y)] for x, y in points]

            dc.DrawPolygon(points)

        # CUSTOM

        elif at == ARROW_UML_GENERALISATION:
            arrowLength = arrow.GetSize()
            arrowWidth = arrowLength  # don't divide by three, making arrow bigger  # / 3.0

            tip_x, tip_y, side1_x, side1_y, side2_x, side2_y = GetArrowPoints(
                startPositionX + deltaX,
                startPositionY + deltaY,
                positionOnLineX + deltaX,
                positionOnLineY + deltaY,
                arrowLength,
                arrowWidth,
            )

            points = [[tip_x, tip_y], [side1_x, side1_y], [side2_x, side2_y], [tip_x, tip_y]]

            dc.SetPen(self._pen)

            # dc.SetBrush(self._brush)  # Set the brush for filling the shape's shape
            # dc.SetBrush(wx.TRANSPARENT_BRUSH)
            # dc.SetBrush(wx.WHITE_BRUSH)
            # brush = wx.Brush("LIGHT BLUE")
            # dc.SetBrush(brush)
            dc.SetBrush(self.GetBackgroundBrush())

            # convert all points to integers - fix needed for Python 3.10
            points = [[int(x), int(y)] for x, y in points]

            dc.DrawPolygon(points)

        elif at in [ARROW_UML_COMPOSITION, ARROW_UML_AGGREGATION]:
            arrowLength = arrow.GetSize()  # / 1.4 to make a bit smaller
            arrowWidth = arrowLength / 2

            def GetArrowPointsCustom(x1, y1, x2, y2, length, width):
                l = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))

                if l < 0.01:
                    l = 0.01

                i_bar = (x2 - x1) / l
                j_bar = (y2 - y1) / l

                x3 = -length * i_bar + x2
                y3 = -length * j_bar + y2

                # Extra point to make a diamond
                x4 = -length * 2 * i_bar + x2
                y4 = -length * 2 * j_bar + y2

                return (
                    x2,
                    y2,
                    width * -j_bar + x3,
                    width * i_bar + y3,
                    x4,
                    y4,
                    -width * -j_bar + x3,
                    -width * i_bar + y3,
                )

            tip_x, tip_y, side1_x, side1_y, side3_x, side3_y, side2_x, side2_y = GetArrowPointsCustom(
                startPositionX + deltaX,
                startPositionY + deltaY,
                positionOnLineX + deltaX,
                positionOnLineY + deltaY,
                arrowLength,
                arrowWidth,
            )
            points = [
                [tip_x, tip_y],
                [side1_x, side1_y],
                [side3_x, side3_y],  # extra point introduced
                [side2_x, side2_y],
                [tip_x, tip_y],
            ]

            dc.SetPen(self._pen)
            # dc.SetBrush(self.GetBackgroundBrush())
            dc.SetBrush(wx.Brush("BLACK"))

            # convert all points to integers - fix needed for Python 3.10
            points = [[int(x), int(y)] for x, y in points]

            dc.DrawPolygon(points)

        # END CUSTOM

        elif at in [ARROW_HOLLOW_CIRCLE, ARROW_FILLED_CIRCLE]:
            # Find point on line of centre of circle, which is a radius away
            # from the end position
            diameter = arrow.GetSize()
            x, y = GetPointOnLine(
                startPositionX + deltaX,
                startPositionY + deltaY,
                positionOnLineX + deltaX,
                positionOnLineY + deltaY,
                diameter / 2.0,
            )
            x1 = x - diameter / 2.0
            y1 = y - diameter / 2.0
            dc.SetPen(self._pen)
            if arrow._GetType() == ARROW_HOLLOW_CIRCLE:
                dc.SetBrush(self.GetBackgroundBrush())
            else:
                dc.SetBrush(self._brush)

            dc.DrawEllipse(x1, y1, diameter, diameter)
        elif at == ARROW_SINGLE_OBLIQUE:
            pass
        elif at == ARROW_METAFILE:
            if arrow.GetMetaFile():
                # Find point on line of centre of object, which is a half-width away
                # from the end position
                #
                #                 width
                #  <-- start pos  <-----><-- positionOnLineX
                #                 _____
                #  --------------|  x  | <-- e.g. rectangular arrowhead
                #                 -----
                #
                x, y = GetPointOnLine(
                    startPositionX,
                    startPositionY,
                    positionOnLineX,
                    positionOnLineY,
                    arrow.GetMetaFile()._width / 2.0,
                )
                # Calculate theta for rotating the metafile.
                #
                # |
                # |     o(x2, y2)   'o' represents the arrowhead.
                # |    /
                # |   /
                # |  /theta
                # | /(x1, y1)
                # |______________________
                #
                theta = 0.0
                x1 = startPositionX
                y1 = startPositionY
                x2 = float(positionOnLineX)
                y2 = float(positionOnLineY)

                if x1 == x2 and y1 == y2:
                    theta = 0.0
                elif x1 == x2 and y1 > y2:
                    theta = 3.0 * math.pi / 2.0
                elif x1 == x2 and y2 > y1:
                    theta = math.pi / 2.0
                elif x2 > x1 and y2 >= y1:
                    theta = math.atan((y2 - y1) / (x2 - x1))
                elif x2 < x1:
                    theta = math.pi + math.atan((y2 - y1) / (x2 - x1))
                elif x2 > x1 and y2 < y1:
                    theta = 2 * math.pi + math.atan((y2 - y1) / (x2 - x1))
                else:
                    raise RuntimeError("Unknown arrowhead rotation case")

                # Rotate about the centre of the object, then place
                # the object on the line.
                if arrow.GetMetaFile().GetRotateable():
                    arrow.GetMetaFile().Rotate(0.0, 0.0, theta)

                if self._erasing:
                    # If erasing, just draw a rectangle
                    minX, minY, maxX, maxY = arrow.GetMetaFile().GetBounds()
                    # Make erasing rectangle slightly bigger or you get droppings
                    extraPixels = 4
                    dc.DrawRectangle(
                        deltaX + x + minX - extraPixels / 2.0,
                        deltaY + y + minY - extraPixels / 2.0,
                        maxX - minX + extraPixels,
                        maxY - minY + extraPixels,
                    )
                else:
                    arrow.GetMetaFile().Draw(dc, x + deltaX, y + deltaY)


"""
    // UML DOCO MISC

    @startuml


        note as N1
            line = ogl.LineShape()

            When we create a line, we specify the arrow using the
            AddArrow() call.

            if edge_label == 'generalisation':
                arrowtype = ogl.ARROW_ARROW
            elif edge_label == 'composition':
                arrowtype = ogl.ARROW_FILLED_CIRCLE
            else:
                arrowtype = None
        end note

        note as N2
            AddArrow(arrowtype)

            wraps the arrowtype in an ArrowHead object

                arrow = ArrowHead(type, end, size, xOffset, name, mf, arrowId)
                self._arcArrows.append(arrow)
                return arrow


            Add an arrow (or annotation) to the line.

            type may currently be one of:

            ARROW_HOLLOW_CIRCLE
              Hollow circle.
            ARROW_FILLED_CIRCLE
              Filled circle.
            ARROW_ARROW
              Conventional arrowhead.
            ARROW_SINGLE_OBLIQUE
              Single oblique stroke.
            ARROW_DOUBLE_OBLIQUE
              Double oblique stroke.
            ARROW_DOUBLE_METAFILE
              Custom arrowhead.

            end may currently be one of:

            ARROW_POSITION_END
              Arrow appears at the end.
            ARROW_POSITION_START
              Arrow appears at the start.

            arrowSize specifies the length of the arrow.

            xOffset specifies the offset from the end of the line.

            name specifies a name for the arrow.

            mf can be a wxPseduoMetaFile, perhaps loaded from a simple Windows
            metafile.

            arrowId is the id for the arrow.
        end note

        note as N3
            DrawArrow(self, dc, arrow, XOffset, proportionalOffset)

            at = arrow._GetType()

            elif at in [ARROW_HOLLOW_CIRCLE, ARROW_FILLED_CIRCLE]:
                # Find point on line of centre of circle, which is a radius away
                # from the end position
                diameter = arrow.GetSize()
                x, y = GetPointOnLine(startPositionX + deltaX, startPositionY + deltaY,
                                   positionOnLineX + deltaX, positionOnLineY + deltaY,
                                   diameter / 2.0)
                x1 = x - diameter / 2.0
                y1 = y - diameter / 2.0
                dc.SetPen(self._pen)
                if arrow._GetType() == ARROW_HOLLOW_CIRCLE:
                    dc.SetBrush(self.GetBackgroundBrush())
                else:
                    dc.SetBrush(self._brush)

                dc.DrawEllipse(x1, y1, diameter, diameter)
            elif at == ARROW_SINGLE_OBLIQUE:
                pass

        end note

    @enduml


"""

