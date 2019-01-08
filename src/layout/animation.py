# animated easing algorithm
# Adapted from http://www.hesido.com/web.php?page=javascriptanimation

import math


def easeInOut(minValue, maxValue, totalSteps, actualStep, powr):
    delta = maxValue - minValue
    stepp = minValue + (math.pow(((1.0 / totalSteps) * actualStep), powr) * delta)
    return math.ceil(stepp)


def doValChangeMem(startval, endval, steps, intervals_failsafe=200, powr=0.35):
    result = []
    actStep = 0
    for i in range(intervals_failsafe):
        val = easeInOut(startval, endval, steps, actStep, powr)
        result.append(int(val))
        actStep += 1
        if actStep > steps:
            break
    return result


def GeneratePoints(point1, point2, steps=8):
    X, Y = 0, 1
    xs = doValChangeMem(startval=point1[X], endval=point2[X], steps=steps)
    ys = doValChangeMem(startval=point1[Y], endval=point2[Y], steps=steps)
    return list(zip(xs, ys))


if __name__ == "__main__":
    print(GeneratePoints((0, 0), (10, 10)))
    print(GeneratePoints((10, 0), (100, 10)))

    print("Done")
