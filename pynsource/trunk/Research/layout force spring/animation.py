# animated easing algorithm

# Adapted from http://www.hesido.com/web.php?page=javascriptanimation

import math

def GeneratePoints(point1, point2, num_points=2):
    """
    For two points (x,y) and (xn,yn) generate a list of
    points (x1,y1), (x2,y2), (x4,y3) 
    """
    X, Y = 0, 1
    
    point = list(point1)
    newPosition = point2
    
    for i in range(20):    
        # if the distance between where the mc is and where it's going is less than 1...
        if abs(newPosition[Y] - point[Y]) < 1:
            point[Y] = newPosition[Y]  # then snap the Y to it's new position
            break
        else:
            point[Y] += 0.2 * (newPosition[Y] - point[Y]) # keep going if not
        print point    
    
    return [point1, point2]
    
    return

"""
http://www.hesido.com/web.php?page=javascriptanimation

elem: element that we're going to animate
startWidth: starting width of animation
endWidth: target width of animation
steps: total steps of animation
intervals: intervals the animation will be done in miliseconds
powr: value used for determining ease-in and out.
----
elem.widthChangeMemInt: The interval animation value for self inhibition.
elem.currenWidth: The objects 'memory' of its last set width.
actstep: actual step of the animation, increased 1 per every execution.

"""

def easeInOut(minValue, maxValue, totalSteps, actualStep, powr):
    #Generic Animation Step Value Generator By www.hesido.com 
    delta = maxValue - minValue
    stepp = minValue+(math.pow(((1.0 / totalSteps) * actualStep), powr) * delta)
    return math.ceil(stepp)
    
def doWidthChangeMem(startWidth, endWidth, steps, intervals_failsafe=200, powr=0.5):
    result = []
    actStep = 0
    for i in range(intervals_failsafe):
        currentWidth = easeInOut(startWidth, endWidth, steps, actStep, powr)
        result.append(int(currentWidth))
        actStep += 1
        if actStep > steps:
            break
    return result

def GeneratePoints(point1, point2, steps=10):
    X, Y = 0, 1
    xs = doWidthChangeMem(startWidth=point1[X], endWidth=point2[X], steps=steps)
    ys = doWidthChangeMem(startWidth=point1[Y], endWidth=point2[Y], steps=steps)
    return zip(xs, ys)

if __name__ == "__main__":
    #result = GeneratePoints((0,0), (10,10))
    #assert result[0] == (0,0)
    #assert result[1] == (10,10)

    #result = GeneratePoints((20,20), (10,10))
    
    #print doWidthChangeMem(15, startWidth=10, endWidth=170, steps=10, intervals=10, powr=0.5)
    print GeneratePoints((0,0), (10,10))
    print GeneratePoints((10,0), (100,10))
    #result = GeneratePoints((0,0), (10,10))
    
    print "Done"