# CoordinateMapper

import locale

locale.setlocale(locale.LC_ALL, "")
# http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x

from beautifultable import BeautifulTable


class CustomException(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


# UTILITY


def compare_loose_int(val1, val2):
    if abs(abs(val1) - abs(val2)) < 2:
        return True
    else:
        print("** Lost something in the conversion", val1, val2)
        return False


def compare_loose_float(val1, val2):
    if abs(abs(val1) - abs(val2)) < 0.1:
        return True
    else:
        print("** Lost something in the conversion", val1, val2)
        return False


def validate_world_to_layout(cc, x, y):  # x, y are int
    res = cc.WorldToLayout((x, y))
    print("WorldToLayout((%d, %d)) = %s" % (x, y, res))
    res2 = cc.LayoutToWorld((res[0], res[1]))
    print("LayoutToWorld((%f, %f)) = %s" % (res[0], res[1], res2))
    return compare_loose_int(x, res2[0]) and compare_loose_int(y, res2[1])


def validate_layout_to_world(cc, x, y):  # x, y are floats
    res = cc.LayoutToWorld((x, y))
    print("LayoutToWorld((%f, %f)) = %s" % (x, y, res))
    res2 = cc.WorldToLayout((res[0], res[1]))
    print("WorldToLayout((%d, %d)) = %s" % (res[0], res[1], res2))
    return compare_loose_float(x, res2[0]) and compare_loose_float(y, res2[1])


#####################


class CoordinateMapper:
    def __init__(self, graph, world_size, scale=2):
        self.graph = graph
        self.world_size = world_size
        self.radius = 10
        self.scale = scale
        self.factorX = -99
        self.factorY = -99

        # Actually it is too soon to call Recalibrate() because wxpython3 (phoenix)
        # doesn't set canvas size properly till later,
        # even though frame has been shown, unlike wxpython2.8 which does set canvas size immediately.
        #
        # self.Recalibrate()

    def Recalibrate(self, new_world_size=None, scale=None):
        # self.DumpCalibrationInfo("is_function_start", new_world_size, scale)

        if new_world_size:
            self.world_size = new_world_size
        if scale:
            self.scale = scale

        ww, wh = self.world_size  # world width, world height

        # Don't want the world size to be 0 or too small otherwise get insane
        # values when translate world to layout coords
        """
        However, as the comment in 
            /home/andy/Devel/pynsource/src/gui/uml_canvas.py
        says:
            Don't assert canvas size sanity anymore as wxpython3 (phoenix) doesn't set canvas size
            as quickly as wxpython2.8 does, even though frame has been sized and shown        
        """
        MIN_WORLD_DIMENSION = 20  # should probably be 200
        errmsg = f"world coords too small {(ww, wh)}, ensure a juicy, big enough frame.GetClientSize() or canvas.GetSize() value is being passed into CoordinateMapper either through the .__init__ or via .Recalibrate()"
        # assert ww > MIN_WORLD_DIMENSION, errmsg
        # assert wh > MIN_WORLD_DIMENSION, errmsg
        if ww <= MIN_WORLD_DIMENSION or wh <= MIN_WORLD_DIMENSION:
            print(errmsg)
            self.world_size = (1000, 1000)  # hack repair to see if it helps things - nope doesn't help

        lw = self.graph.layoutMaxX - self.graph.layoutMinX  # layout width
        lh = self.graph.layoutMaxY - self.graph.layoutMinY  # layout height

        # assert lw
        # assert lh
        if lw == 0:
            lw = 1.0  # 0.0001
        if lh == 0:
            lh = 1.0  # 0.0001

        self.factorX = ww / self.scale / lw
        self.factorY = wh / self.scale / lh

        # self.DumpCalibrationInfo("is_function_end", new_world_size, scale)

    def DumpCalibrationInfo(
        self, dump_mode=None, new_world_size=None, scale=None, dump_nodes=True, doprint=True
    ):

        t = BeautifulTable()
        t.set_style(BeautifulTable.STYLE_BOX)  # nice ─── chars
        
        # t.columns.header = ["items", "info1", "info2"]

        if dump_mode == "is_function_start":
            t.rows.append(
                [
                    "CoordinateMapper.Recalibrate START, calling with: new_world_size, scale",
                    new_world_size,
                    scale,
                ]
            )
        elif dump_mode == "is_function_end":
            t.rows.append(["CoordinateMapper.Recalibrate END", "", ""])

        t.rows.append(["scale and radius", self.scale, self.radius])

        # subtable support not yet released, cos of newline support issue in beautifuletable
        # subtable1 = BeautifulTable()
        # subtable1.columns.header = ["scale", "radius"]
        # subtable1.rows.append([self.scale, self.radius])

        t.rows.append(["world_size", self.world_size[0], self.world_size[1]])

        t.rows.append(
            ["layout MinX MinY", "%2.2f" % self.graph.layoutMinX, "%2.2f" % self.graph.layoutMinY]
        )
        t.rows.append(
            ["layout MaxX Maxy", "%2.2f" % self.graph.layoutMaxX, "%2.2f" % self.graph.layoutMaxY]
        )

        t.rows.append(
            [
                "layout width height",
                "%2.2f" % (self.graph.layoutMaxX - self.graph.layoutMinX),
                "%2.2f" % (self.graph.layoutMaxY - self.graph.layoutMinY),
            ]
        )

        t.rows.append(
            [
                "factorX factorY",
                locale.format_string("%d", self.factorX, grouping=True),
                locale.format_string("%d", self.factorY, grouping=True),
            ]
        )

        # t.rows.append([subtable1, "", "", ""])

        if doprint:
            t.columns.alignment[0] = BeautifulTable.ALIGN_LEFT
            print(t)
        else:
            return t

        if dump_nodes:
            for node in self.graph.nodes:
                print(node)

    def DumpCalibrationInfo_OLD(
        self, dump_mode=None, new_world_size=None, scale=None, dump_nodes=True
    ):
        indent = ""
        if dump_mode == "is_function_start":
            print()
            print(
                indent
                + "CoordinateMapper.Recalibrate START, calling with new_world_size=%s, scale=%s"
                % (new_world_size, scale)
            )
        elif dump_mode == "is_function_end":
            indent = "\t"
            print(indent + "CoordinateMapper.Recalibrate END")

        print(indent + "scale and radius \t\t\t", self.scale, "\t\t", self.radius)
        print(indent + "world_size\t\t\t", self.world_size)
        print(
            indent
            + "layout (MinX/MinY)(MaxX/Maxy)\t(%2.2f,%2.2f) (%2.2f,%2.2f)"
            % (
                self.graph.layoutMinX,
                self.graph.layoutMinY,
                self.graph.layoutMaxX,
                self.graph.layoutMaxY,
            )
        )
        print(
            indent
            + "layout width height\t\t%2.2f %2.2f"
            % (
                self.graph.layoutMaxX - self.graph.layoutMinX,
                self.graph.layoutMaxY - self.graph.layoutMinY,
            )
        )
        print(
            indent + "factorX factorY\t\t\t",
            locale.format_string("%d", self.factorX, grouping=True),
            locale.format_string("%d", self.factorY, grouping=True),
        )
        if dump_nodes:
            for node in self.graph.nodes:
                print(node)

    def LayoutToWorld(self, point):
        return [
            int((point[0] - self.graph.layoutMinX) * self.factorX + self.radius),
            int((point[1] - self.graph.layoutMinY) * self.factorY + self.radius),
        ]

    def WorldToLayout(self, point):
        return [
            (point[0] - self.radius) / self.factorX + self.graph.layoutMinX,
            (point[1] - self.radius) / self.factorY + self.graph.layoutMinY,
        ]

    def AllToLayoutCoords(self):
        something_wrong = False

        for node in self.graph.nodes:
            layoutPosX, layoutPosY = self.WorldToLayout([node.left, node.top])

            if abs(layoutPosX) > 50.0:
                print("??!", "About to set Big layoutPosX?", layoutPosX, "for", node)
                something_wrong = True
            if abs(layoutPosY) > 50.0:
                print("??!", "About to set Big layoutPosY?", layoutPosY, "for", node)
                something_wrong = True

            node.layoutPosX, node.layoutPosY = layoutPosX, layoutPosY

        if something_wrong:
            print("\nSomething went wrong with AllToLayoutCoords - DumpCalibrationInfo\n")
            self.DumpCalibrationInfo(False)

    def AllToWorldCoords(self):
        for node in self.graph.nodes:
            node.left, node.top = self.LayoutToWorld([node.layoutPosX, node.layoutPosY])

            # if not validate_layout_to_world(self, node.layoutPosX, node.layoutPosY):
            # validate_layout_to_world(self, node.layoutPosX, node.layoutPosY)

            # rederive_layoutPosX, rederive_layoutPosY = self.WorldToLayout([node.left, node.top])
            # rederive_X_ok = abs(abs(rederive_layoutPosX) - abs(node.layoutPosX)) < 0.001
            # rederive_Y_ok = abs(abs(rederive_layoutPosY) - abs(node.layoutPosY)) < 0.001
            # if not rederive_X_ok:
            #    rederive_X_ok = "False !!!!!"
            # if not rederive_Y_ok:
            #    rederive_Y_ok = "False !!!!!"
            # print "rederive check X % 3.4f % 3.4f \t\t%s" % (rederive_layoutPosX, node.layoutPosX, rederive_X_ok)
            # print "rederive check Y % 3.4f % 3.4f \t\t%s" % (rederive_layoutPosY, node.layoutPosY, rederive_Y_ok)
            # print

            if node.left > 20000:
                print("-" * 40, "Something's gone wrong!")
                print("node.layoutPosX, node.layoutPosY", node.layoutPosX, node.layoutPosY)
                self.DumpCalibrationInfo(False)
                raise CustomException("Insane x values being generated")


if __name__ == "__main__":

    from view.graph import Graph, GraphNode

    g = Graph()

    n1 = GraphNode("A", 0, 0, 200, 200)
    n2 = GraphNode("B", 0, 0, 200, 200)
    g.AddEdge(n1, n2)

    """
    coordinate mapper translation tests
    """

    # Force some values
    g.layoutMaxX, g.layoutMinX, g.layoutMaxY, g.layoutMinY = (
        5.14284838307,
        -7.11251323652,
        4.97268108065,
        -5.77186339003,
    )

    c = CoordinateMapper(g, (784, 739))

    # LayoutToWorld

    res = c.LayoutToWorld((-2.7556504645221258, 0.39995144721675263))
    print(res)
    assert res[0] == 149, res
    assert res[1] == 221, res

    res = c.LayoutToWorld((-5.4927475878590482, -1.7573960183470871))
    print(res)
    assert res[0] == 61, res
    assert res[1] == 147, res

    # WorldToLayout

    def trunc(f, n):
        """Truncates/pads a float f to n decimal places without rounding"""
        slen = len("%.*f" % (n, f))
        return str(f)[:slen]

    res = c.WorldToLayout((149, 221))
    print(res)
    print("results should approximate -2.7556504645221258, 0.39995144721675263")
    assert trunc(res[0], 1) == "-2.7", trunc(res[0], 1)
    assert trunc(res[1], 1) == "0.3", trunc(res[1], 1)

    res = c.WorldToLayout((61, 147))
    print(res)
    assert trunc(res[0], 0) == "-5", trunc(res[0], 0)
    assert trunc(res[1], 1) == "-1.7", trunc(res[1], 1)

    # Symmetry Validation

    print("Symmetry Validation")

    validate_world_to_layout(c, 100, 200)
    validate_world_to_layout(c, 0, 0)
    validate_world_to_layout(c, 50, 50)

    validate_layout_to_world(c, 0.0, 0.0)
    validate_layout_to_world(c, -1.0, 1.0)

    # More complex validation

    """
scale and radius 			2 		10
world_size			(1008, 687)
layout (MinX/MinY)(MaxX/Maxy)	(-4.63,-7.49) (6.18,7.53)
layout width height		10.81 15.02
factorX factorY			46 22
line-line intersections 2
node-node overlaps 0
line-node crossings 16
bounds (303, 795)    
    """

    g.layoutMaxX, g.layoutMinX, g.layoutMaxY, g.layoutMinY = 6.18, -4.63, 7.53, -7.49
    c2 = CoordinateMapper(g, (1008, 687))
    validate_world_to_layout(c2, 100, 200)
    validate_world_to_layout(c2, 0, 0)
    validate_world_to_layout(c2, 50, 50)

    validate_layout_to_world(c2, 0.0, 0.0)
    validate_layout_to_world(c2, -1.0, 1.0)
    validate_layout_to_world(c2, -5.0, -5.0)
    validate_layout_to_world(c2, 5.0, 5.0)

    print("Done")
