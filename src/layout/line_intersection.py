# line_intersection


def FindLineIntersection(start1, end1, start2, end2):  # all are point tuples
    # Adapted from http://stackoverflow.com/questions/1119451/how-to-tell-if-a-line-intersects-a-polygon-in-c

    X, Y = 0, 1
    start1, end1, start2, end2 = (
        (float(start1[X]), float(start1[Y])),
        (float(end1[X]), float(end1[Y])),
        (float(start2[X]), float(start2[Y])),
        (float(end2[X]), float(end2[Y])),
    )

    denom = ((end1[X] - start1[X]) * (end2[Y] - start2[Y])) - (
        (end1[Y] - start1[Y]) * (end2[X] - start2[X])
    )

    #  AB & CD are parallel
    if denom == 0:
        return None

    numer = ((start1[Y] - start2[Y]) * (end2[X] - start2[X])) - (
        (start1[X] - start2[X]) * (end2[Y] - start2[Y])
    )
    r = numer / denom
    numer2 = ((start1[Y] - start2[Y]) * (end1[X] - start1[X])) - (
        (start1[X] - start2[X]) * (end1[Y] - start1[Y])
    )
    s = numer2 / denom
    if (r < 0 or r > 1) or (s < 0 or s > 1):
        return None

    # Find intersection point
    result = [0, 0]
    result[0] = start1[X] + (r * (end1[X] - start1[X]))
    result[1] = start1[Y] + (r * (end1[Y] - start1[Y]))

    return result
