# Misc utility functions

import math
import time
import os, sys
from loglevels import Log
import pprint
from tables import DEFAULT_WARDATE_USFORMAT


if sys.version_info[:2] == (2,2):
    sys.path.append('../Libs/lib.win32-2.2')

elif sys.version_info[:2] == (2,3):
    sys.path.append('../Libs/lib.win32-2.3')

try:
    from _utilcc import eventStrToList
except:
    print "utilcc: Failed to load compiled extension (eventStrToList)"
    def eventStrToList(eventstr):
        """
            Input a string e.g. (1,1,0),o2,AT,2,(2,2,2),(3,3,3)
            and returns a list without breaking apart the any tuples.
        """
        commapositions = []
        insidebrackets = 0
        pos = 0
        for c in eventstr:
            if c in '({':
                insidebrackets += 1
            if c in ')}':
                insidebrackets -= 1
            if c == ',' and not insidebrackets:
                commapositions.append(pos)
            pos +=1
        assert insidebrackets == 0
        commapositions.append(pos)    # Add a fake comma position representing the r.h. end of the list

        #    Now do the split ourselves
        resultlist = []
        frompos = 0
        for topos in commapositions:
            chunk = eventstr[frompos:topos]
            resultlist.append(chunk)
            frompos = topos+1
        return resultlist

def show(*args, **kw):
    import traceback
    file, line, func, parms = traceback.extract_stack(limit=2)[0]
    names = parms[5:-1].split(',')
    print 'File "%s", line %s %s'%(file, line, func)
    result = ""
    for name, value in zip(names, args) + kw.items():
        if result: print '|%s'%result
        result = '%s = %s'%(name.strip(), value)
    if result: print '`%s'%result
if type(__builtins__) is dict:
    __builtins__['show'] = show
else:
    __builtins__.show = show

class UniqueList(list):
    def append(self, item):
        if item not in self:
            list.append(self, item)
    def __add__(self, L):
        for item in L:
            self.append(item)
        return self
    def __iadd__(self, L):
        return self + L

def ConvertShortTimeTupleToTimeStr(atime):
    """
    (7,0) converts to 7 AM
    (16,0) converts to 4 PM
    """
    assert len(atime) == 2, 'ShortTimeTuple has wrong number of elements'
    hour = atime[0]
    if hour > 12:
        hour -= 12
        ampm = 'PM'
    else:
        ampm = 'AM'
    return "%d %s" % (hour, ampm)

def ConvertTimeStrToShortTimeTuple(atimestr):
    """
    7 AM  converts to (7,0)
    4 PM  converts to (16,0)
    """
    hour, ampm = atimestr.split(' ')
    assert ampm in ('AM','PM'), 'weather editor string must contain am or pm'
    hour = eval(hour)
    assert hour >= 4 and hour <= 9, ('hour %d must be in range 4 to 9'%hour)
    if ampm == 'PM':
        hour += 12
    return (hour,0)


def getListItem(list, n, defaultvalueifnotthere=None):
    """
    Like somdict.get(key, default)
     except works on lists.
    """
    if len(list) >= n+1:
        return list[n]
    else:
        return defaultvalueifnotthere

#---Dummy function---#000000#FFFFFF---------------------------------------------
def AAAAAA():
    pass

#---Back to normal functions---#000000#FFFFFF-----------------------------------
def PixelCoordToAbsQuad(pixelcoord):
##    assert pixelcoord[0] >= 32, pixelcoord[0]
##    assert pixelcoord[1] >= 32, pixelcoord[1]
    result = (pixelcoord[0]//64, pixelcoord[1]//64) # TODO 64
    return result


def AbsQuadCoordToPixel(absquadcoord):
##    assert absquadcoord[0] >= 0, absquadcoord[0]
##    assert absquadcoord[1] >= 0, absquadcoord[1]
    result = (absquadcoord[0] * 64 + 32, absquadcoord[1] * 64 + 32) # TODO 64
    return result


def ImportScenarioFile(filename):
    filename = FilenameToFullScenarioPathName(filename)
    globalsdict = {}
    execfile(filename, globalsdict)
    return globalsdict

def repr_SortedDict(thedict):
    items = thedict.items()
    items.sort()

    def safeconvert(k,v):
        if k in ('readiness',):
            return "'%s':%s"%(k,str(v))
        else:
            return "'%s':%s"%(k,repr(v))

    return '{'+(", ".join([ safeconvert(*i) for i in items ]))+'}'

def repr_SortedDictEx(thedict, *listofkeys):
    return repr_SortedDict(dict([ (k,v) for k,v in thedict.items() if k in listofkeys]))

def DeriveScenarioFolderPath():
    """
    Better to go upwards and look for the 'Scenarios' subfolder.
    """
# This is going to be wrong when an Delphi app calls.
#
##    currentmoduledir = os.path.dirname(os.path.abspath(sys.argv[0]))
##    parent, current = os.path.split(currentmoduledir)
##    resultpath = os.path.join(parent, 'Scenarios')

# SMARTER version
    folderstofind = ('Client', 'Storyline', 'Ai', 'MapEditor')
    def PopFoldersTillFind(currentmoduledir, folders):
        currentmoduledir = currentmoduledir.lower()
        folders = map(str.lower, folders)

        for failsafe in range(10): # maximum number of loops
            currentmoduledir, current = os.path.split(currentmoduledir)
            if current in folders:
                return currentmoduledir
            if current == '': # top of the tree
                break
        raise RuntimeError, ('PopFoldersTillFind cannot find any one of' + `folderstofind`)


    currentmoduledir = os.path.dirname(os.path.abspath(sys.argv[0]))  # better to use os.path.abspath(".")

    if os.path.isdir(os.path.join(currentmoduledir, 'Scenarios')): # you might be in .../Devel already!
        parent = currentmoduledir
    else:
        parent = PopFoldersTillFind(currentmoduledir, folders=folderstofind)
    resultpath = os.path.join(parent, 'Scenarios')

##    pp = pprint.PrettyPrinter(indent = 4)
##    Log('Any', lambda : 'def DeriveScenarioFolderPath():  \n\n resultpath=%s \n\n currentmoduledir %s \n\n os.path.abspath(sys.argv[0])=%s  \n\n sys.argv[0]=%s  \n\n SysPath = %s\n\n' % \
##        (resultpath, currentmoduledir, os.path.abspath(sys.argv[0]), sys.argv[0], pp.pformat(sys.path)))

    return resultpath
    #importfilename = os.path.splitext(os.path.basename(filename))[0]
    #return currentmoduledir

def FilenameToFullScenarioPathName(filename):
    """
    Pass in either a full pathname or a file name.
     If just a file name then prepend the scenario directory.
     If a full pathname, then just return it untouched.
    """
    parent, current = os.path.split(filename)
    if not parent:
        assert os.path.splitext(current)[1] == '', 'Should not be specifying an extension when supplying a simple filename without a path'
        return os.path.join(DeriveScenarioFolderPath(), current) + '.py'
    else:
        return filename  # already a full path.

def roundit(floatval, decimalplaces):
    poweroften = math.pow(10.0, decimalplaces)
    return math.floor( poweroften * floatval ) / poweroften

def TilequadToAbsquad(tiletuple, quadtuple):
    resultx = tiletuple[0] * 2 + quadtuple[0]
    resulty = tiletuple[1] * 2 + quadtuple[1]
    return (resultx, resulty)

def AbsquadToTilequad(absquad):
    tileresultx = absquad[0]/2
    tileresulty = absquad[1]/2
    quadresultx = absquad[0]%2
    quadresulty = absquad[1]%2
    return (tileresultx,tileresulty), (quadresultx,quadresulty)


def eventStrToList_OLD(eventstr):
  """
    Input a string e.g. (1,1,0),o2,AT,2,(2,2,2),(3,3,3)
    and returns a list without breaking apart the any tuples.
  """
  commapositions = []
  insidebrackets = 0
  pos = 0
  for c in eventstr:
    if c in '({':
      insidebrackets += 1
    if c in ')}':
      insidebrackets -= 1
    if c == ',' and not insidebrackets:
      commapositions.append(pos)
    pos +=1
  assert insidebrackets == 0
  commapositions.append(pos)  # Add a fake comma position representing the r.h. end of the list

  #  Now do the split ourselves
  resultlist = []
  frompos = 0
  for topos in commapositions:
    chunk = eventstr[frompos:topos]
    resultlist.append(chunk)
    frompos = topos+1
  return resultlist

def extractQualityInfo(event):
    info = eventStrToList(event)
    if len(info) > 4:
        return int(info[4]) # if there is a quality attribute, grab it
    else:
        return 0

def chunkToTabbedChunk(str):
    list = str.split('\n')
    return '\n\t'.join(list)


##def asciiDate(datetuple, timepos, stryearoverride):
##  secs = time.mktime(datetuple)
##  secs += float(timepos)*60
##  strdate = time.ctime(secs)
##
##  list = strdate.split(' ')
##  list[4] = stryearoverride    # e.g. '1944'
##  strdate = ' '.join(list)
##  print list
##  return strdate

##def asciiDate(datetuple, timepos, stryearoverride):
##  print datetuple
##  secs = time.mktime(datetuple)
##  secs += float(timepos)*60
##  strdate = time.ctime(secs)
##  print strdate
##
##  list = strdate.split(' ')
##  list[4] = stryearoverride    # e.g. '1944'
##
##  list[3] = list[3][0:-3]
##
##  strdate = ' '.join(list[0:3]) + ' ' + list[4] + ' ' + list[3]
##  return strdate

##def asciiDate(datetuple, timepos, stryearoverride):
##  #print datetuple
##  dateobject = mx.DateTime.mktime(datetuple)
##  #delta = mx.DateTime.DateTimeDeltaFromSeconds(timepos)
##  delta = mx.DateTime.TimeDelta(0.0,timepos,0.0)  # hour=0.0,minute=0.0,second=0.0
##  resultdate = dateobject + delta
##  #print 'res', resultdate
##  #strdate = resultdate.localtime() # won't give Sun Jul 01 06:30:00 2001
##  #print strdate                    # gives      2001-07-01 16:30:00.00
##  strdate = resultdate.strftime("%a %b %d %H:%M:%S %Y")
##  #print strdate
##
##
##  list = strdate.split(' ')
##  list[4] = stryearoverride    # e.g. '1944'
##
##  list[3] = list[3][0:-3]
##
##  strdate = ' '.join(list[0:3]) + ' ' + list[4] + ' ' + list[3]
##  return strdate
if sys.version_info[:2] <= (2,2):
    import mx.DateTime
    def asciiDate(datetuple, timepos, stryearoverride):

        #print datetuple
        dateobject = mx.DateTime.mktime(datetuple)
        delta = mx.DateTime.TimeDelta(0.0,timepos,0.0)  # hour=0.0,minute=0.0,second=0.0
        resultdate = dateobject + delta
        strdate = resultdate.strftime("%a %b %d ") + \
                  stryearoverride + \
                  resultdate.strftime(" %H:%M")   # e.g. "Sun Jul 01 1944 06:01"
        #print strdate
        return strdate


    def TimePosToDateStr1943(timepos, modernyear=2001, waryear=int(DEFAULT_WARDATE_USFORMAT[2]), month=int(DEFAULT_WARDATE_USFORMAT[0]), day=int(DEFAULT_WARDATE_USFORMAT[1]), hour=6):
        datetuple = (modernyear, month, day, hour, 000, 0, 0, 1, 0)
        result = asciiDate(datetuple, timepos, str(waryear))
        return result

else:
    import datetime
    def asciiDate(d, timepos, year):
        basetime = datetime.datetime(int(year),*d[1:5])
        result = basetime + datetime.timedelta(0,0,0,0,timepos)
        return result.strftime("%a %b %d %Y %H:%M")



    def TimePosToDateStr1943(timepos, modernyear=2001, waryear=int(DEFAULT_WARDATE_USFORMAT[2]), month=int(DEFAULT_WARDATE_USFORMAT[0]), day=int(DEFAULT_WARDATE_USFORMAT[1]), hour=6):
        basetime = datetime.datetime(waryear,month,day,hour)
        result = basetime + datetime.timedelta(0,0,0,0,timepos)
        return result.strftime("%a %b %d %Y %H:%M")
##        return result.ctime()??


def cleanchunk(str):
    res = []
    lines = str.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            res.append(line)
    return "\n".join(res)

import os

def GetAllFromFile(FILENAME):
    if os.path.exists(FILENAME):
        fp = open(FILENAME, 'r')
        chunk = fp.read(999999)
        fp.close()
    else:
        chunk = ''
    return chunk


import types

def CoordCompare(coord1, coord2):
##    # Assume coords are either int or tuple e.g. 1  or (10,10)
##    if not isinstance(coord1, types.TupleType):
##        return coord1 == coord2
##    # Could have (x,y) vs. (x,y,time)
##    # Could have (x,y) vs. (x,y,time,newx,newy)
##    return coord1[0:2] == coord2[0:2]
    return CoordXYonly(coord1) == CoordXYonly(coord2)

def CoordXYonly(coord):
    if not isinstance(coord, types.TupleType):
        return coord
    return coord[0:2]


def FormatSignalsDictForDisplay(sigdict):
    """
    A signals dict might be:

       {'NonRadio': [   'Telephone', 'Rider', 'Runner'],
          'Radio': {   'whilstmoving': '',
                       'whilststationary': ''}}

        or

        {
        'NonRadio': [ '?? signals - enemy'],
          'Radio': {  'whilstmoving':     '?? radio signals - enemy',
                      'whilststationary': '?? radio signals - enemy' }}
    """
    # Should only be called by post scenario40, V2 trooptype system.  which will be oob newstyle
    result = ''
    if sigdict['NonRadio']:
        result += str(sigdict['NonRadio']) + '\n'
    if sigdict['Radio']['whilststationary']:
        result += sigdict['Radio']['whilststationary'] + '   (whilst stationary)\n'
    if sigdict['Radio']['whilstmoving']:
        result += sigdict['Radio']['whilstmoving'] + '   (whilst moving)'
    return result



import unittest, random

class TestCase00(unittest.TestCase):
    def setUp(self):
      self.simplestr = '1,o2,AT,2'
      self.normalstr = '(1,1,0),o2,AT,2'
    def checkSimple(self):
      assert eventStrToList( self.simplestr ) == ['1', 'o2', 'AT', '2']
      assert eventStrToList( self.simplestr ) == self.simplestr.split(',')
    def checkNormal(self):
      assert eventStrToList( self.normalstr ) == ['(1,1,0)', 'o2', 'AT', '2']

    def checkNormalOrder(self):
      orderstr = '(1,1,0),o2,ORDER:MOVE,2,0,(1,1,1),(2,2,2),(3,3,3),(4,4,4)'
      assert eventStrToList( orderstr ) == ['(1,1,0)', 'o2', 'ORDER:MOVE', '2', '0', '(1,1,1)','(2,2,2)','(3,3,3)','(4,4,4)']

    def checkSplitModernAT(self):
      at = "(1, 6, 0),me_6,AT,(32, 32)"
      assert len(eventStrToList( at )) == 4

    def checkSplitFutureAT(self):
      at = "(1, 6, 0),me_6,AT,(32, 32),((0,0),(1,1))"
      assert len(eventStrToList( at )) == 5

    def checkSplitHasWithDicts(self):
      has = "(1, 6, 0),me_1,HAS,{'coord':(0,0),'ammo':500,'experience':0}"
      assert len(has.split(',')) == 9
      assert len(eventStrToList( has )) == 4

    def checkasciiDate(self):
      datetuple = (2001, 7, 1, 6, 30, 0, 0, 1, 0)
      timepos = 0
      result = asciiDate(datetuple, timepos, '1944')
      #print result
      #assert result == "Sun Jul 01 06:30:00 1944"
      if sys.version_info[:2] <= (2,2):
          assert result == "Sun Jul 01 1944 06:30"
      else:
          assert result == "Sat Jul 01 1944 06:30" # it really was a saturday!


    def checkasciiDateAgain(self):
      datetuple = (2001, 7, 1, 6, 0, 0, 0, 0, 0)
      timepos = 1
      result = asciiDate(datetuple, timepos, '1944')
      #print result
      if sys.version_info[:2] <= (2,2):
          assert result == "Sun Jul 01 1944 06:01"
      else:
          assert result == "Sat Jul 01 1944 06:01" # it really was a saturday!
    def checkCoordCompare(self):
      assert CoordCompare(1,1) == 1
      assert CoordCompare(1,2) == 0
      assert CoordCompare( (10,10), (10,10) ) == 1
      assert CoordCompare( (10,10), (10,11) ) == 0

      assert CoordCompare( (10,10,60), (10,10) ) == 1
      assert CoordCompare( (10,10,60,1,1), (10,10,99) ) == 1

    def checkRoundit(self):
        assert roundit(0.70999999999999996, 2) == 0.71
        assert roundit(1.3953488372093024, 2) == 1.39

    def checkScenarioPath(self):
        apath = DeriveScenarioFolderPath()
##        print apath
        assert apath.lower() in map(str.lower,[
            'C:\\Documents and Settings\\Administrator\Desktop\\Combat Mission Campaign Devel\\Devel\\Scenarios',
            'C:\\CC\\Devel\\Scenarios',
            'D:\\CC\\Devel\\Scenarios',
            ])
    def checkFullPathForSingleFile(self):
        apath = FilenameToFullScenarioPathName('Alpha3')
##        print apath
        assert apath.lower() in map(str.lower,[
            'C:\\Documents and Settings\\Administrator\Desktop\\Combat Mission Campaign Devel\\Devel\\Scenarios\\Alpha3.py',
            'C:\\CC\\Devel\\Scenarios\\Alpha3.py',
            'D:\\CC\\Devel\\Scenarios\\Alpha3.py',
            ])
        try:
            FilenameToFullScenarioPathName('Alpha3.py')
            assert 0, 'Should not be able to pass in a single filename with an extension cos the import never allowed it so neither should we'
        except:
            pass

    def checkImportFileScenarioFile01(self):
        filename = 'Alpha3_turbo03_withbrokenmemappings'
        adict = ImportScenarioFile(filename)
        assert 'version' in adict
        assert 'mapinfo' in adict
        assert 'allies' in adict
        assert 'axis' in adict
        assert 'axis' in adict
        assert 'alliedparentrelations' in adict
        assert 'axisparentrelations' in adict

    def checkPixelToAbsQuadconversions(self):  # TODO 64
        """
          n * 64 + 32     quad to pixel

          (n - 32) / 64   pixel to quad  or
           n//64
        """
        assert PixelCoordToAbsQuad((32,32)) == (0,0)
        assert PixelCoordToAbsQuad((96,32)) == (1,0)
        assert PixelCoordToAbsQuad((32,96)) == (0,1)
        assert PixelCoordToAbsQuad((96,96)) == (1,1)

        assert AbsQuadCoordToPixel((0,0)) == (32,32)
        assert AbsQuadCoordToPixel((0,1)) == (32,96)
        assert AbsQuadCoordToPixel((1,0)) == (96,32)
        assert AbsQuadCoordToPixel((1,1)) == (96,96)
        assert AbsQuadCoordToPixel((2,3)) == (160,224)

    def checkspeedofeventstrtolist(self):
      orderstr = '(1,1,0),o2,ORDER:MOVE,2,0,(1,1,1),(2,2,2),(3,3,3),(4,4,4)'

      import time
      LOOPSIZE = 550

      starttime1 = time.time()
      for i in range(1,LOOPSIZE):
          resultlist = eventStrToList_OLD( orderstr )
      endtime1 = time.time()
      timetaken1 = endtime1-starttime1

      starttime2 = time.time()
      for i in range(1,LOOPSIZE):
          resultlist = eventStrToList( orderstr )
      endtime2 = time.time()
      timetaken2 = endtime2-starttime2

##      starttime3 = time.time()
##      for i in range(1,LOOPSIZE):
##          pass
##      endtime3 = time.time()
##      timetaken3 = endtime3-starttime3

      assert timetaken2 < timetaken1
      #print 'timetaken1', timetaken1, 'timetaken2', timetaken2, 'timetaken3', timetaken3
      #print 'C code is faster by %d percent'%((timetaken1-timetaken2)/timetaken2*100)
      #time.sleep(8)

    def checkSortedDict_01(self):
        adict = {'b':1,'a':2}
        adictsorted = repr_SortedDict(adict)
        assert adictsorted == "{'a':2, 'b':1}"

    def checkSortedDict_01a(self):
        assert getListItem([], 0, 120) == 120  # not there so use default
        assert getListItem([], 1, 120) == 120  # not there so use default

        assert getListItem([10], 0, 120) == 10   # ok
        assert getListItem([10], 1, 120) == 120  # not there so use default

        assert getListItem([10,11], 0, 120) == 10   # ok
        assert getListItem([10,11], 1, 120) == 11   # ok
        assert getListItem([10,11], 2, 120) == 120  # not there so use default
        assert getListItem([10,11], 3, 120) == 120  # not there so use default


def suite():
    suite1 = unittest.makeSuite(TestCase00,'check')
    alltests = unittest.TestSuite( (suite1,) )
    return alltests

def main():
    """ Run all the suites.  To run via a gui, then
            python unittestgui.py NestedDictionaryTest.suite
        Note that I run with VERBOSITY on HIGH  :-) just like in the old days
        with pyUnit for python 2.0
        Simply call
          runner = unittest.TextTestRunner(descriptions=0, verbosity=2)
        The default arguments are descriptions=1, verbosity=1
    """
    runner = unittest.TextTestRunner(descriptions=0, verbosity=2) # default is descriptions=1, verbosity=1
    #runner = unittest.TextTestRunner(descriptions=0, verbosity=1) # default is descriptions=1, verbosity=1
    runner.run( suite() )

if __name__ == '__main__':
    main()

