"""
  Offers an API for controlling three iterator playheads which are all synchronised via the
  PlayheadMediator class .

  PlayheadMediator class mediates (using helper objects which use the PlayAPI)
    between the uses of the various playheads so that all playheads
    are consistent with one another.
    The sub-objects byEvent, byTime and byTurn know about each other via
    the mediator, and form the guts of the mediation object.
    
    All API calls are done to indirectly through byEvent, byTime or byTurn,
    USAGE:
      playheadmediator.byEvent.Start()
      playheadmediator.byTime.Next()
      playheadmediator.byTurn.GetCurrentValue()

    This module doesn't know about the storyline class.

"""

import turn as turnmodule
from render import Renderer
from playhead import Playhead
from utilcc import eventStrToList

class PlayAPI:
    def __init__(self, mediator, turnmanager, playhead):
        self.mediator = mediator
        self.playhead = playhead
        self.turnMgr = turnmanager

    def IsEmpty(self):
        return self.playhead.IsEmpty()
    def IsMoreToPlay(self):
        return self.playhead.IsMoreToPlay()

    def Start(self):
        self.playhead.GoStart()
        self.SynchroniseOtherPlayheads()
    def Endd(self):
        self.playhead.GoEnd()
        self.SynchroniseOtherPlayheads()

    def Next(self):
        self.playhead.GoNext()
        self.SynchroniseOtherPlayheads()
    def Previous(self):
        self.playhead.GoPrevious()
        self.SynchroniseOtherPlayheads()

    def _GetCurrentPosition(self):
        return self.playhead.Position
    def GetCurrentValue(self):
        raise 'Not Implemented'

    def _GetMaxPosition(self):
        return self.playhead.MaxPosition
    def GetMaxValue(self):
        raise 'Not Implemented'

    def _JumpToPosition(self, position):
        self.playhead.Go(position)
        self.SynchroniseOtherPlayheads()
    def JumpToValue(self, value):
        raise 'Not Implemented'

    def NotifyOfInsert(self, pos):
        self.playhead.NotifyOfInsert(pos)
        self.SynchroniseOtherPlayheads(toposition = pos)
    def NotifyPositionNowValid(self, pos):
        self.playhead.NotifyPositionNowValid(pos)
        self.SynchroniseOtherPlayheads(toposition = pos)

    def SynchroniseOtherPlayheads(self, toposition):
        """
        LOGIC SKETCH

        if toposition == None then
          toposition = Current playhead position
          
        if to event
          derive time and turn
          set time and turn playheads
        if to time
          derive turn and event (if any)
          set turn playhead
          if event - set to first event of that time
          if no event - set to highest event closest to but not exceeding time
        if to turn
          derive time and event (if any)
          set time playhead
          if event - set to last occurrence of event having that time
          if no event - set to highest event closest to but not exceeding time

        EMPTINESS LOGIC
        
        If turn playhead is empty ie. and thus playhead position is -1
        then what to tell other playheads?  Don't do anything.
        assert other playheads are mostly empty too, since:
        
        if there is an event, there will be a turn and a time it occurred in.
        if there is a time, there will be a turn but not necessarily an event
        if there is a turn, there will be time, but not necessarily an event

        if no events, maybe are turns, maybe is time (can have time and turns without events)
        if no time, should be no turns, and should be no events
        if no turns, should be no time, and should be no events

        SYNCING TO TURNS (& TIMES) - DISCUSSION
      
        The setting of the time playhead is based on turn, and thus on the theortical (according
        to turnspec) time of the start of the turn.  There is a possible discrepancy between what
        the time playhead is set to and what the time of the event at the event playhead position is set to.
        
        Resolve by favouring the time.  i.e.
        
        If there is an event in the time frame of that turn then the event playhead is set to it.
        But that event will not necessarily be of the time of the start of the turn.
        In fact there may be no event at all in the turn's timeframe, thus we choose an event
        which is closest (but a higher time, according to the current implementation of
        the routine _FindNearestEvent().

        There are similar arbitary decisions when synching to time, I think.  There is another function
                   _FindLatestEventWithTime() which makes this decision.
        """
        raise 'Not Implemented'

    def _FindLastEventWithTimeElseMostRecentEventLessthanTime(self, timeToFind):
        timepostofind = self.turnMgr.TimeToTimePosition(timeToFind)
        hi = len(self.mediator.story)
        lo = 0
        if not hi:
            return 0
        while lo < hi:
            mid = (lo+hi)//2
            event = self.mediator.story[mid]
            eventtime = eval( eventStrToList(event)[0] )
            timeposmid = self.turnMgr.TimeToTimePosition(eventtime)
            if timepostofind < timeposmid:
                hi = mid
            else:
                lo = mid + 1
        return max(0, lo-1)
    
    def _FindLastEventWithTimeElseMostRecentEventLessthanTime_ORI(self, timeToFind):
        """
          if 'timeToFind' matches event then return pos of last event with time of 'timeToFind'
          else return pos of latest event with time before 'timeToFind'
          if no matches return 0
          
          'timeToFind' is an tuple
              (simple mode)  e.g. (1,1)
              (normal mode)  e.g. (1,6,0)
        """
        pos = 0
        lastoccurenceoftime = -1

        for event in self.mediator.story:
            eventtime = eventStrToList(event)[0]
            eventtime = eval(eventtime)

            if self.turnMgr.TimeToTimePosition(eventtime) <= self.turnMgr.TimeToTimePosition(timeToFind):
                #if eventtime <= timeToFind:
                lastoccurenceoftime = pos
                pos+=1
            else:
                break
                # pos should now be positioned at the insertion point

        if lastoccurenceoftime<>-1:
            return lastoccurenceoftime
        maxpos = len(self.mediator.story)-1
        return min(maxpos, pos)

    def _EnsureMaxTimeCorrespondsToMaxTurn(self):
        """
        Must call this quite often so that time (from,to) corresponds to what the
        maxturn is.
        """
        maxturnsofar = self.mediator.byTurn.GetMaxValue()
        if maxturnsofar<>-1:
            # find out what the maximum time for that turn is
            timetuple, day = self.turnMgr.TurnToTime(maxturnsofar)
            maxtime = timetuple[1]
            maxtimepos = self.turnMgr.TimeToTimePosition((day, )+maxtime)

            self.mediator.timePlayhead.NotifyPositionNowValid(maxtimepos)

    def _GetPositionToSyncTo(self, toposition):
        """
        Used by SynchroniseOtherPlayheads()
        
        If you do supply a parameter 'toposition' that means we are merely notifying the other
        playheads that a valid position now exists & they should translate into their own
        'coordinate' systems and ensure that position also exists.
        
        If don't supply a parameter 'toposition', (the usual case) then it means we want to
        move the current position and synch the current position of the other playheads to it.
        """
        wanttomovecurrentpos = (toposition == None)
        if wanttomovecurrentpos:
            pos = self.playhead.Position
        else:
            pos = toposition
        return wanttomovecurrentpos, pos


class EventPlayAPI(PlayAPI):
    def GetCurrentValue(self):
        return self._GetCurrentPosition()  # Could have returned event object at this position, but no.
    def GetMaxValue(self):
        return self._GetMaxPosition()  # Could have returned event object at this position, but no.
    def JumpToValue(self, value):
        self._JumpToPosition(value)

    def _DeriveOtherPlayheadPositionsFrom(self, eventpos):
        # Derive timepos & turnpos
        def _TimeOfEventAt(eventpos, story, self):
            if eventpos == -1:
                return-1
            event = story[eventpos]
            timestr = eventStrToList(event)[0]
            #print event
            assert '('in timestr
            assert ')'in timestr
            return eval(timestr) # convert string tuple to tuple


        time = _TimeOfEventAt(eventpos, self.mediator.story, self)   # find out what turn the current event is in
        turn = self.turnMgr.TimeToTurn(time)
        timepos = self.turnMgr.TimeToTimePosition(time)   # time is already a 3 piece tuple
        turnpos = self.turnMgr.TurnToTurnPosition(turn)
        return timepos, turnpos


    def _SetOtherPlayheadsTo(self, wanttomovecurrentpos, timepos, turnpos):
        self.mediator.timePlayhead.NotifyPositionNowValid(timepos)
        self.mediator.turnPlayhead.NotifyPositionNowValid(turnpos)
        if wanttomovecurrentpos:
            self.mediator.timePlayhead.Go(timepos)
            self.mediator.turnPlayhead.Go(turnpos)

    def SynchroniseOtherPlayheads(self, toposition = None):
        if self.playhead.IsEmpty():
            # if no events, maybe are turns, maybe is time (can have time and turns without events)
            return
        wanttomovecurrentpos, eventpos = self._GetPositionToSyncTo(toposition)
        timepos, turnpos = self._DeriveOtherPlayheadPositionsFrom(eventpos)
        self._SetOtherPlayheadsTo(wanttomovecurrentpos, timepos, turnpos)
        self._EnsureMaxTimeCorrespondsToMaxTurn()

        # if there is an event, there will be a turn and a time it occurred in.
        assert not self.mediator.timePlayhead.IsEmpty()
        assert not self.mediator.turnPlayhead.IsEmpty()

class TimePlayAPI(PlayAPI):
    """
    Time playhead ok, set event & turn playheads
    """
    def GetCurrentValue(self):
        result = self.turnMgr.TimePositionToTime(self._GetCurrentPosition())
        return result
    def GetMaxValue(self):
        result = self.turnMgr.TimePositionToTime(self._GetMaxPosition())
        return result
    def JumpToValue(self, value):
        self._JumpToPosition(self.turnMgr.TimeToTimePosition(value))

    def _DeriveOtherPlayheadPositionsFrom(self, timepos):
        # Derive eventpos & turnpos
        time = self.turnMgr.TimePositionToTime(timepos)       # (day,hour,min)
        turn = self.turnMgr.TimeToTurn(time)
        eventpos = self._FindLastEventWithTimeElseMostRecentEventLessthanTime(time)
        turnpos = self.turnMgr.TurnToTurnPosition(turn)
        return eventpos, turnpos

    def _SetOtherPlayheadsTo(self, wanttomovecurrentpos, eventpos, turnpos):
        self.mediator.turnPlayhead.NotifyPositionNowValid(turnpos)
        self.mediator.eventPlayhead.NotifyPositionNowValid(eventpos)
        if wanttomovecurrentpos:
            self.mediator.turnPlayhead.Go(turnpos)
            self.mediator.eventPlayhead.Go(eventpos)

    def SynchroniseOtherPlayheads(self, toposition = None):
        if self.playhead.IsEmpty():
            # if no time, should be no turns, and should be no events
            assert self.mediator.turnPlayhead.IsEmpty()
            assert self.mediator.eventPlayhead.IsEmpty()
            return

        wanttomovecurrentpos, timepos = self._GetPositionToSyncTo(toposition)
        eventpos, turnpos = self._DeriveOtherPlayheadPositionsFrom(timepos)
        self._SetOtherPlayheadsTo(wanttomovecurrentpos, eventpos, turnpos)
        self._EnsureMaxTimeCorrespondsToMaxTurn()

        # if there is a time, there will be a turn but not necessarily an event
        assert not self.mediator.turnPlayhead.IsEmpty()

class TurnPlayAPI(PlayAPI):
    """
    Turn playhead ok, set time & event playheads
    """
    def GetCurrentValue(self):
        return self.turnMgr.TurnPositionToTurn(self._GetCurrentPosition())
    def GetMaxValue(self):
        return self.turnMgr.TurnPositionToTurn(self._GetMaxPosition())
    def JumpToValue(self, value):
        self._JumpToPosition(self.turnMgr.TurnToTurnPosition(value))

    def _DeriveOtherPlayheadPositionsFrom(self, turnpos):
        # Derive eventpos & timepos
        turn = self.turnMgr.TurnPositionToTurn(turnpos)
        pairOftimetuples, day = self.turnMgr.TurnToTime(turn)
        timefrom, totime = pairOftimetuples
        timefrom = (day, )+timefrom      # e.g. (1,6,0)

        #ORIG eventpos = self._FindNearestEvent(timefrom)
        eventpos = self._FindLastEventWithTimeElseMostRecentEventLessthanTime(timefrom)

        timepos = self.turnMgr.TimeToTimePosition(timefrom)
        return eventpos, timepos

    def _SetOtherPlayheadsTo(self, wanttomovecurrentpos, eventpos, timepos):
        self.mediator.timePlayhead.NotifyPositionNowValid(timepos)
        self.mediator.eventPlayhead.NotifyPositionNowValid(eventpos)
        if wanttomovecurrentpos:
            self.mediator.timePlayhead.Go(timepos)
            self.mediator.eventPlayhead.Go(eventpos)

    def SynchroniseOtherPlayheads(self, toposition = None):
        if self.playhead.IsEmpty():
            # if no turns, should be no time, and should be no events
            assert self.mediator.timePlayhead.IsEmpty()
            assert self.mediator.eventPlayhead.IsEmpty()
            return

        wanttomovecurrentpos, turnpos = self._GetPositionToSyncTo(toposition)
        eventpos, timepos = self._DeriveOtherPlayheadPositionsFrom(turnpos)
        self._SetOtherPlayheadsTo(wanttomovecurrentpos, eventpos, timepos)
        self._EnsureMaxTimeCorrespondsToMaxTurn()

        # if there is a turn, there will be time, but not necessarily an event
        assert not self.mediator.timePlayhead.IsEmpty()



class PlayheadMediator:
    """
    This PlayheadMediator class owns 3 playheads (simple iterators) and 3 PlayAPI iterators which are
    wrappers smart and synchronise to each other
    
    USAGE:
      playheadmediator.byEvent.Start()
      playheadmediator.byTime.Next()
      playheadmediator.byTurn.GetCurrentValue()

    Initialise with a turnmanager and a reference to a story list (usually provided by the storyline class).
    The story list object will actually by a reference, so changes elsewhere to that list will be
    reflected here.  When we Clear() this class, we delete all objects in the story list,
    but keeping same list obj in memory so all other refs work ok.
    I.e. we
      del self.story[0:]   rather than
      self.story = [] 
    """
    def __init__(self, turnmanager, storyListRef = []):
        self.turnMgr = turnmanager    # aggregated, not owned
        self.story = storyListRef     # reference to list owned by storyline.  Changes there are reflected here.

        self.eventPlayhead = Playhead()
        self.timePlayhead = Playhead()
        self.turnPlayhead = Playhead()

        self.byEvent = EventPlayAPI(self, turnmanager, self.eventPlayhead)
        self.byTime = TimePlayAPI(self, turnmanager, self.timePlayhead)
        self.byTurn = TurnPlayAPI(self, turnmanager, self.turnPlayhead)
    def Clear(self):
        del self.story[0:]
        self.eventPlayhead.Clear()
        self.timePlayhead.Clear()
        self.turnPlayhead.Clear()
    def IsEmpty(self):
        return len(self.story) == 0and \
          self.byEvent.IsEmpty()and self.byTime.IsEmpty()and self.byTurn.IsEmpty()



import unittest
from turn import TurnMgr

class TestCase01(unittest.TestCase):
    def setUp(self):
        turnmanager = turnmodule.TurnMgr()
        self.goto = PlayheadMediator(turnmanager, [])  # init with empty story list

    def checkInit(self):
        assert self.goto.byEvent.mediator == self.goto
        
    def checkStartNoItemsNormal(self):
        self.goto.byEvent.Start()
        assert self.goto.byEvent._GetCurrentPosition() == -1
        assert self.goto.byTime._GetCurrentPosition() == -1
        assert self.goto.byTurn._GetCurrentPosition() == -1
        assert self.goto.byTime.GetCurrentValue() == self.goto.turnMgr.EarlistTimeMinusOne()
        assert self.goto.byTurn.GetCurrentValue() == -1

        assert self.goto.byTurn.IsEmpty()
        assert self.goto.byTime.IsEmpty()
        assert self.goto.byTurn.IsEmpty()

    def checkStartNoItemsAndGoPreviousNormal(self):
        self.goto.byTurn.Previous()
        assert self.goto.byEvent._GetCurrentPosition() == -1
        assert self.goto.byTime._GetCurrentPosition() == -1
        assert self.goto.byTurn._GetCurrentPosition() == -1
        assert self.goto.byTime.GetCurrentValue() == self.goto.turnMgr.EarlistTimeMinusOne()
        assert self.goto.byTurn.GetCurrentValue() == -1

        self.goto.byTime.Previous()
        assert self.goto.byEvent._GetCurrentPosition() == -1
        assert self.goto.byTime._GetCurrentPosition() == -1
        assert self.goto.byTurn._GetCurrentPosition() == -1
        assert self.goto.byTime.GetCurrentValue() == self.goto.turnMgr.EarlistTimeMinusOne()
        assert self.goto.byTurn.GetCurrentValue() == -1

        self.goto.byEvent.Previous()
        assert self.goto.byEvent._GetCurrentPosition() == -1
        assert self.goto.byTime._GetCurrentPosition() == -1
        assert self.goto.byTurn._GetCurrentPosition() == -1
        assert self.goto.byTime.GetCurrentValue() == self.goto.turnMgr.EarlistTimeMinusOne()
        assert self.goto.byTurn.GetCurrentValue() == -1

    def checkStartOneItemNormal(self):
        # Insert a single event - this is usually done by storyline class
        self.goto.story = ["(1,6,30),o2,AT,2"]
        self.goto.eventPlayhead.NotifyOfInsert(0)

        # Position theoretically still undefined cos even though have inserted an event, haven't moved the head.
        # But playhead is helpful & automatically move the head if were empty and item is inserted.
        assert self.goto.byEvent._GetCurrentPosition() == 0

        self.goto.byEvent._JumpToPosition(0) # this will ripple to the other playheads.
        timepos = self.goto.byTime._GetCurrentPosition()
        assert timepos == 30
        assert self.goto.byTime.GetCurrentValue() == (1,6,30)

        turnpos = self.goto.byTurn._GetCurrentPosition()
        assert turnpos == 0
        assert self.goto.byTurn.GetCurrentValue() == 1

        self.goto.byEvent.Start()
        assert self.goto.byEvent.GetCurrentValue() == 0
        assert self.goto.byTime.GetCurrentValue() == (1,6,30)
        assert self.goto.byTurn.GetCurrentValue() == 1

    def checkBasicMovementSynch01Normal(self):
        # Insert a events - this is usually done by storyline class
        self.goto.story = ["(1,6,30),o2,AT,2", "(1,7,0),x2,AT,4"]
        self.goto.byEvent.NotifyPositionNowValid(1)  # this will ripple to the other playheads.

        self.goto.byEvent._JumpToPosition(1)
        assert self.goto.byEvent._GetCurrentPosition() == 1
        assert self.goto.byTime.GetCurrentValue() == (1,7,0)
        assert self.goto.byTurn.GetCurrentValue() == 2

        self.goto.byEvent._JumpToPosition(2) # invalid position, goto max, which means time stays where it is
        assert self.goto.byEvent._GetCurrentPosition() == 1
        assert self.goto.byTime.GetCurrentValue() == (1,7,0)
        assert self.goto.byTurn.GetCurrentValue() == 2
        self.goto.byEvent.Start()
        self.goto.byEvent.Endd()
        assert self.goto.byEvent.GetCurrentValue() == 1
        assert self.goto.byTime.GetCurrentValue() == (1,7,0)
        assert self.goto.byTurn.GetCurrentValue() == 2

    def checkBasicMovementSynch02Normal(self):
        """
         events go 0...n  so can jump playhead directly without conversions
         times go 1..n    so must convert timepositions to times  using self.goto.turnMgr.TimeToTimePosition()
         turns go 1..n    so must conver turnpositions to turns and vice versa.
        """
        # Insert a events - this is usually done by storyline class
        self.goto.story = ["(1,6,30),o2,AT,2", "(1,7,0),x2,AT,4", "(2,6,45),o2,AT,2"]
        self.goto.eventPlayhead.NotifyPositionNowValid(2)

        self.goto.byEvent._JumpToPosition(2)
        assert self.goto.byEvent._GetCurrentPosition() == 2
        assert self.goto.byEvent.GetCurrentValue() == 2
        assert self.goto.byTime.GetCurrentValue() == (2,6,45)
        assert self.goto.byTurn.GetCurrentValue() == 17

        # For events, jumping by position and by value are the same.
        self.goto.byEvent.JumpToValue(2)
        assert self.goto.byEvent._GetCurrentPosition() == 2
        assert self.goto.byEvent.GetCurrentValue() == 2

        # Check by time positioning

        self.goto.byEvent.Start()
        self.goto.byTime.JumpToValue((1,7,0))
        assert self.goto.byEvent.GetCurrentValue() == 1
        assert self.goto.byTime.GetCurrentValue() == (1,7,0)
        assert self.goto.byTurn.GetCurrentValue() == 2

        self.goto.byTime.Next()
        assert self.goto.byEvent.GetCurrentValue() == 1  # reverting to older findNearest event algorithm undershoots - pretty arbitrary
        assert self.goto.byTime.GetCurrentValue() == (1,7,1)
        assert self.goto.byTurn.GetCurrentValue() == 2

        self.goto.byTime.Start()
        assert self.goto.byEvent.GetCurrentValue() == 0
        assert self.goto.byTime.GetCurrentValue() == (1,6,0)
        assert self.goto.byTurn.GetCurrentValue() == 1

        self.goto.byTime.Endd()
        assert self.goto.byEvent.GetCurrentValue() == 2
        assert self.goto.byTime.GetCurrentValue() == (2,6,59)
        assert self.goto.byTurn.GetCurrentValue() == 17

        # Test byTurn positioning

        self.goto.byTurn.JumpToValue(1)
        assert self.goto.byEvent.GetCurrentValue() == 0
        assert self.goto.byTurn.GetCurrentValue() == 1
        assert self.goto.byTime.GetCurrentValue() == (1,6,0)

        self.goto.byTurn.JumpToValue(2)
        assert self.goto.byEvent.GetCurrentValue() == 1 or self.goto.byEvent.GetCurrentValue() == 2
        assert self.goto.byTurn.GetCurrentValue() == 2
        """
         There is a possible discrepancy between what the time playhead is set to and what the time
         of the event at the event playhead position is set to.
         Resolve by favouring the time.  i.e.
        """
        assert self.goto.byTime.GetCurrentValue() == (1, 7, 0)    # if we favor the theoretical time corresponding to the turn start time.

    def checkMaxValue(self):
        self.goto.story = ["(1,6,30),o2,AT,2", "(1,7,0),x2,AT,4", "(2,6,45),o2,AT,2"]
        self.goto.byEvent.NotifyPositionNowValid(2)  # this will ripple to the other playheads.

        assert self.goto.byEvent.GetMaxValue() == 2
        assert self.goto.byTime.GetMaxValue() == (2, 6, 59)   # this is an important test. Ensure time is expanding to max for max turn
        assert self.goto.byTurn.GetMaxValue() == 17

    def checkJumpToAndValidateCurrentValueNormal(self):
        self.goto.story = ["(1,6,30),o2,AT,2", "(1,7,0),x2,AT,4", "(2,6,45),o2,AT,2"]
        self.goto.byEvent.NotifyPositionNowValid(2)  # this will ripple to the other playheads.

        for i in range(1, 5+1):  # should go up to time (1,6,5)
            self.goto.byTime.JumpToValue((1,6,i))
            assert self.goto.byTime.GetCurrentValue() == (1,6,i)
        assert self.goto.byTime.GetCurrentValue() == (1,6,5)

        for i in range(1, 2+1):  # should go up to turn 2
            self.goto.byTurn.JumpToValue(i)
            assert self.goto.byTurn.GetCurrentValue() == i

        for i in range(0, 2+1):  # events should go 0,1,2
            self.goto.byEvent.JumpToValue(i)
            assert self.goto.byEvent.GetCurrentValue() == i

    def checkIsEmptyNormal(self):
        self.goto.story = ["(1,6,30),o2,AT,2", "(1,7,0),x2,AT,4", "(2,6,45),o2,AT,2"]
        self.goto.byEvent.NotifyPositionNowValid(2)  # this will ripple to the other playheads.

        assert not self.goto.IsEmpty()
        assert not self.goto.byEvent.IsEmpty()
        assert not self.goto.byTime.IsEmpty()
        assert not self.goto.byTurn.IsEmpty()

        self.goto.Clear()
        assert self.goto.IsEmpty()
        assert self.goto.byEvent.IsEmpty()
        assert self.goto.byTime.IsEmpty()
        assert self.goto.byTurn.IsEmpty()

    def checkByTimeAndEventPositioningNormal(self):
        # Insert a events - this is usually done by storyline class
        self.goto.story = ["(1,6,30),o2,AT,2", "(1,7,0),x2,AT,4", "(2,6,45),o2,AT,2"]

        #self.goto.eventPlayhead.NotifyPositionNowValid(2)  # naughty - do not address dumb playhead class directly
        self.goto.byEvent.NotifyPositionNowValid(2)

        # Check by time positioning

        self.goto.byTime.JumpToValue((1, 6, 30))
        assert self.goto.byTime.GetCurrentValue() == (1, 6, 30)
        assert self.goto.byEvent.GetCurrentValue() == 0

        self.goto.byTime.JumpToValue((1, 7, 0))
        assert self.goto.byTime.GetCurrentValue() == (1, 7, 0)
        assert self.goto.byEvent.GetCurrentValue() == 1

        self.goto.byTime.Next()
        assert self.goto.byEvent.GetCurrentValue() == 1
        assert self.goto.byTime.GetCurrentValue() == (1, 7, 1)

        self.goto.byTime.Start()
        assert self.goto.byEvent.GetCurrentValue() == 0
        assert self.goto.byTime.GetCurrentValue() == (1, 6, 0)
        assert self.goto.byTurn.GetCurrentValue() == 1

        self.goto.byTime.Endd()
        assert self.goto.byEvent.GetCurrentValue() == 2
        #print self.goto.byTime.GetCurrentValue()
        assert self.goto.byTime.GetCurrentValue() == (2, 6, 59)   # not 2,6,45  cos time always padded to end of turn time

    def checkByTurnPositioningNormal(self):
        self.goto.story = ["(1,12,1),o1,AT,6"]
        self.goto.byEvent.NotifyPositionNowValid(0)

        # Check by turn positioning
        self.goto.byTurn.JumpToValue(6)
        assert self.goto.byEvent.GetCurrentValue() == 0

    def checkByTimeAndEventPositioningNormal02(self):
        # Insert a events - this is usually done by storyline class
        self.goto.story = ["(1,12,1),p1,AT,0", "(2,8,0),p1,AT,4"]
        self.goto.byEvent.NotifyPositionNowValid(1)

        # Check by time positioning
        self.goto.byEvent.Endd()
        assert self.goto.byEvent.GetCurrentValue() == 1

        self.goto.byTime.JumpToValue((1, 23, 59))
        assert self.goto.byEvent.GetCurrentValue() == 0
        self.goto.byTime.Next()
        assert self.goto.byTime.GetCurrentValue() == (1, 0, 0)
        assert self.goto.byEvent.GetCurrentValue() == 0


class TestCase02(unittest.TestCase):
    def setUp(self):
        """
        First turn should be 4 hours long
        """
        turnmanager = turnmodule.TurnMgr()
        specs = [((7, 0), (10, 59)),
                ((11, 0), (16, 59)),
                ((17, 0), (17, 59)),
                ((18, 0), (18, 59)),
                ((19, 0), (19, 59)),
                ((20, 0), (20, 59)),
                ((21, 0), (21, 59)),
                ((22, 0), (22, 59)),
                ((23, 0), (23, 59)),
                ((0, 0), (0, 59)),
                ((1, 0), (1, 59)),
                ((2, 0), (2, 59)),
                ((3, 0), (3, 59)),
                ((4, 0), (4, 59)),
                ((5, 0), (6, 59))]
        turnmanager.SetTurnSpecs(specs)
        self.goto = PlayheadMediator(turnmanager, [])  # init with empty story list

    def CalcAmountOfTimeInStoryline(self, playheads):  # DUPLICATED in playheadmanager.py and unittestgogo01.py
        numminutes = 0
        while playheads.byTime.IsMoreToPlay():
            playheads.byTime.Next()
            numminutes += 1
        numhours = (numminutes+1)/60
        return numminutes, numhours

    def EnsureSanity(self):
    
        # Check earliest time
        assert self.goto.turnMgr.EarlistTimeMinusOne() == (0,6,59)

        # Check max values for playheads
        #print 'byTime.GetMaxValue', self.goto.byTime.GetMaxValue()
        assert self.goto.byTime.GetMaxValue() == (1,10,59)
        #print 'byEvent.GetMaxValue', self.goto.byEvent.GetMaxValue()
        assert self.goto.byEvent.GetMaxValue() == 1                     # 0 based
        #print 'byTurn.GetMaxValue', self.goto.byTurn.GetMaxValue()
        assert self.goto.byTurn.GetMaxValue() == 1                      # 1 based

        # Check amount of time in storyline
        
        numminutes, numhours = self.CalcAmountOfTimeInStoryline(self.goto)
        #print 'PASS 1 numminutes =%d #hours= %d' % (numminutes, numhours)
        assert numhours == 4

        self.goto.byTime.Start()
        numminutes, numhours = self.CalcAmountOfTimeInStoryline(self.goto)
        #print 'PASS 2 numminutes =%d #hours= %d' % (numminutes, numhours)
        assert numhours == 4

        self.goto.byEvent.Start()
        numminutes, numhours = self.CalcAmountOfTimeInStoryline(self.goto)
        #print 'PASS 3 numminutes =%d #hours= %d' % (numminutes, numhours)
        assert numhours == 4

        self.goto.byTurn.Start()
        numminutes, numhours = self.CalcAmountOfTimeInStoryline(self.goto)
        #print 'PASS 4 numminutes =%d #hours= %d' % (numminutes, numhours)
        assert numhours == 4
    
    def check01(self):
        # Insert a events - this is usually done by storyline class
        self.goto.story = ["(1,7,0),p1,AT,0", "(1,7,59),p1,AT,4"]
        self.goto.byEvent.NotifyPositionNowValid(1)
        self.EnsureSanity()


##    def check02(self):
##        # Insert bad nonsensical events - this is usually done by storyline class
##        self.goto.story = ["(1,5,0),p1,AT,0", "(1,6,59),p1,AT,4"]  # illegal values cos time starts at 1,7,0
##        self.goto.byEvent.NotifyPositionNowValid(1)
##        #self.goto.byTime.SynchroniseOtherPlayheads()
##
##        self.EnsureSanity()
##        return
##        
##        #print 'EarlistTimeMinusOne', self.goto.turnMgr.EarlistTimeMinusOne()
##        assert self.goto.turnMgr.EarlistTimeMinusOne() == (0,6,59)
##
##        print 'PASS 1 numminutes =%d #hours= %d' % self.CalcAmountOfTimeInStoryline(self.goto)
##        self.goto.byTime.Start()
##        print 'PASS 2 numminutes =%d #hours= %d' % self.CalcAmountOfTimeInStoryline(self.goto)
##        self.goto.byEvent.Start()
##        print 'PASS 3 numminutes =%d #hours= %d' % self.CalcAmountOfTimeInStoryline(self.goto)
##        self.goto.byTurn.Start()
##        print 'PASS 4 numminutes =%d #hours= %d' % self.CalcAmountOfTimeInStoryline(self.goto)
##
##        print 'byTime.GetMaxValue', self.goto.byTime.GetMaxValue()
##        print 'byEvent.GetMaxValue', self.goto.byEvent.GetMaxValue()
##        print 'byTurn.GetMaxValue', self.goto.byTurn.GetMaxValue()


def suite():
    suite1 = unittest.makeSuite(TestCase01, 'check')
    suite2 = unittest.makeSuite(TestCase02, 'check')
    alltests = unittest.TestSuite((suite1,suite2))
##    alltests = unittest.TestSuite((suite2,))
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
    runner = unittest.TextTestRunner(descriptions = 0, verbosity = 2) # default is descriptions=1, verbosity=1
    #runner = unittest.TextTestRunner(descriptions=0, verbosity=1) # default is descriptions=1, verbosity=1
    runner.run(suite())

if __name__ == '__main__':
    main()


