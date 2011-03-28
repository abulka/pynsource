# line intersecting with a shape?

class Point:
    def __init__(self, x, y):
        self.X = float(x)
        self.Y = float(y)

class Line:
    def __init__(self, left, top, right, bottom):
        self.from_point = Point(left, top)
        self.to_point = Point(right, bottom)
    
class Shape:
    def __init__(self, top, left, width, height):
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        
        line1 = Line(self.left, self.top, self.right, self.top)
        line2 = Line(self.right, self.top, self.right, self.bottom)
        line3 = Line(self.right, self.bottom, self.left, self.bottom)
        line4 = Line(self.left, self.bottom, self.left, self.top)
        self.lines = [line1, line2, line3, line4]
    
    def get_bottom(self):
        return self.top + self.height

    def get_right(self):
        return self.left + self.width

    bottom = property(get_bottom)
    right = property(get_right)
    
def FindLineIntersection(start1, end1, start2, end2):
    denom = ((end1.X - start1.X) * (end2.Y - start2.Y)) - ((end1.Y - start1.Y) * (end2.X - start2.X))
    
    #  AB & CD are parallel
    if denom == 0:
        return None
    
    numer = ((start1.Y - start2.Y) * (end2.X - start2.X)) - ((start1.X - start2.X) * (end2.Y - start2.Y))
    r = numer / denom
    numer2 = ((start1.Y - start2.Y) * (end1.X - start1.X)) - ((start1.X - start2.X) * (end1.Y - start1.Y))
    s = numer2 / denom
    if ((r < 0 or r > 1) or (s < 0 or s > 1)):
        return None
    
    # Find intersection point
    result = [0,0]
    result[0] = start1.X + (r * (end1.X - start1.X))
    result[1] = start1.Y + (r * (end1.Y - start1.Y))
    
    return result

def NumIntersectionsWithShape(line, shape):
    result = []
    for shapeline in shape.lines:
        result.append(FindLineIntersection(line.from_point, line.to_point, shapeline.from_point, shapeline.to_point))

    # trim out duplicated and Nones
    def remove_duplicates(lzt):
        d = {}
        for x in lzt: d[tuple(x)]=x
        return d.values()
    result = [r for r in result if r != None]
    result = remove_duplicates(result)
    return result

if __name__ == '__main__':
    res = FindLineIntersection(Point(0,0), Point(200,200), Point(10,10), Point(10,50))
    assert res == [10.0, 10.0]
    
    res = FindLineIntersection(Point(0,30), Point(200,30), Point(10,10), Point(10,50))
    assert res == [10.0, 30.0]
    
    s = Shape(10, 10, 30, 40)
    l = Line(0, 0, 200, 200)
    res = NumIntersectionsWithShape(l, s)
    assert len(res) == 2
    assert [10.0, 10.0] in res
    assert [40.0, 40.0] in res
    
    l = Line(20, 0, 20, 1000)
    res = NumIntersectionsWithShape(l, s)
    assert len(res) == 2
    assert [20.0, 10.0] in res
    assert [20.0, 50.0] in res
    
    print "Done"
