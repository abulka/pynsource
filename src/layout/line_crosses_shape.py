# line intersecting with a shape?
# testing only

from graph import GraphNode
from .line_intersection import FindLineIntersection

# This function was migrated into GraphNode


def CalcLineIntersectionsWithNode(line_start_point, line_end_point, node):
    result = []
    for nodeline in node.lines:
        result.append(
            FindLineIntersection(line_start_point, line_end_point, nodeline[0], nodeline[1])
        )

    # trim out duplicated and Nones
    def remove_duplicates(lzt):
        d = {}
        for x in lzt:
            d[tuple(x)] = x
        return list(d.values())

    result = [r for r in result if r != None]
    result = remove_duplicates(result)
    return result


if __name__ == "__main__":
    res = FindLineIntersection((0, 0), (200, 200), (10, 10), (10, 50))
    assert res == [10.0, 10.0]

    res = FindLineIntersection((0, 30), (200, 30), (10, 10), (10, 50))
    assert res == [10.0, 30.0]

    node = GraphNode("A", 10, 10, 30, 40)
    assert len(node.lines) == 4
    assert (10, 10) in node.lines[0]
    assert (40, 10) in node.lines[0]
    assert (40, 10) in node.lines[1]
    assert (40, 50) in node.lines[1]
    assert (40, 50) in node.lines[2]
    assert (10, 50) in node.lines[2]
    assert (10, 50) in node.lines[3]
    assert (10, 10) in node.lines[3]

    res = CalcLineIntersectionsWithNode((0, 0), (200, 200), node)
    assert len(res) == 2
    assert [10.0, 10.0] in res
    assert [40.0, 40.0] in res

    res = CalcLineIntersectionsWithNode((20, 0), (20, 1000), node)
    assert len(res) == 2
    assert [20.0, 10.0] in res
    assert [20.0, 50.0] in res

    print("Done, tests passed")
