# blackboard

from graph import Graph
from layout_spring import GraphLayoutSpring

class LayoutBlackboard:
    def __init__(self, graph, controller):
        self.graph = graph
        self.controller = controller

    def LayoutMultipleChooseBest(self, numlayouts=3):
        """
        Blackboard
        Rerun layout several times, remembering each as a memento.  Then pick the best.

        Don't remember starting scale since we are going to change it anyway
        We could add mementos for a layout at the current scale - in which case
        
        Coordinate scaling runs 3.2 to max within ScaleUpMadly()
        Finish at the best scale as chosen by this algorithm
        """
        self.controller.AllToLayoutCoords()    # doesn't matter what scale the layout starts with
        layouter = GraphLayoutSpring(self.graph, gui=None)
        self.controller.mementos = []
        
        oriscale = self.controller.coordmapper.scale

        # Generate a few totally fresh layout variations
        for i in range(numlayouts):
            layouter.layout(keep_current_positions=False)
            
            # Do a layout and expand directly to the original scale, and calc vitals stats
            #self.coordmapper.Recalibrate(scale=oriscale) # need this if scale changed
            #scale, num_line_line_crossings, num_node_node_overlaps, num_line_node_crossings = \
            #    self.LayoutAndGetVitalStats()
            
            #self.AllToWorldCoords()  # need this if gui animation off
            #self.overlap_remover.RemoveOverlaps()  # you DO want to take into account a post overlap removal situation
            #num_line_line_crossings = len(self.graph.CountLineOverLineIntersections())
            #num_line_node_crossings = self.graph.CountLineOverNodeCrossings()['ALL']/2    # ignore? 
            
            scale, num_line_line_crossings, num_node_node_overlaps, num_line_node_crossings = \
                self.ScaleUpMadly(strategy=":reduce post overlap removal LN crossings")
            memento = self.graph.GetMementoOfPositions()
            self.controller.mementos.append((num_line_line_crossings,
                                  num_node_node_overlaps,
                                  num_line_node_crossings,
                                  scale,
                                  88,
                                  memento))
                
            #self.stateofthenation()
            #wx.SafeYield()
        
        self.controller.DumpMementos()
        print "sort"
        self.controller.mementos.sort()  # should sort by 1st item in tuple, followed by next item in tuple etc. - perfect!
        self.controller.DumpMementos()
        
        self.controller.DisplayMemento(self.controller.mementos[0][5], self.controller.mementos[0][3])


    def LayoutThenPickBestScale(self, strategy=None, scramble=False, animate_at_scale=None):
        """
        x = layout a few times to untangle then scale up till line-node crossings low
        z = layout a few times to untangle then scale up till natural node overlaps low (don't apply overlap removal till end)
        """
        self.controller.AllToLayoutCoords()  # doesn't matter what scale the layout starts with
        
        if animate_at_scale:
            self.controller.coordmapper.Recalibrate(scale=animate_at_scale) # Scale up just for watching purposes...
        
        layouter = GraphLayoutSpring(self.graph, gui=self.controller)  # TODO gui = controller - yuk
        layouter.layout(keep_current_positions=not scramble)

        self.ScaleUpMadly(strategy, animate=True)
        self.controller.stateofthenation()

    def LayoutRepeatedly(self, maxtimes=10, scramble=True):
        """
        Relayout till nothing seems to move anymore in real world coordinates.
        Stay at same scale. DEFUNCT - integrated this algorithm into the lower
        level spring layout, operating there on layout coords - Spring Layout
        itself drops out early if nothing seems to be changing.
        """
        self.controller.AllToLayoutCoords()     # doesn't matter what scale the layout starts with
        memento1 = self.graph.GetMementoOfPositions()
        
        layouter = GraphLayoutSpring(self.graph, gui=self.controller)  # TODO gui = controller - yuk
        layouter.layout(keep_current_positions=not scramble)

        for i in range(1, maxtimes):
            self.controller.AllToWorldCoords()
            memento2 = self.graph.GetMementoOfPositions()
            
            if Graph.MementosEqual(memento1, memento2):
                print "Layout %d World Position Mementos Equal - break" % i
                break
            else:
                print "Layout %d World Positions in flux - keep trying" % i
                layouter.layout(keep_current_positions=True)

            layouter.layout(keep_current_positions=True)
            memento1 = memento2
        
        self.controller.AllToWorldCoords()
        self.controller.stage2() # does overlap removal and stateofthenation
        
    def ScaleUpMadly(self, strategy, animate=False):
        """
        Leaves the scale at max level it got to - doesn't restore scale

        strategy = ":reduce pre overlap removal NN overlaps"
        strategy = ":reduce post overlap removal LN crossings"
        
        Operates repeatedly on the layout coords, so ignores anything you
        have done since, like world coord overlap removal.

        Running overlap removal at different scales can remove or introduce
        LL and LN crossings (but by definition, no NN overlaps ;-)
        
        After AllToWorldCoords() we are getting a picture of the pure layout result
        
        Calling self.coordmapper.Recalibrate(scale) before AllToWorldCoords() simply
        expands or contracts the appearance of the world view nodes
        
        After AllToWorldCoords(), looking at pure layout result there will typically be
         -- LL == 0, unless the spring layout couldn't untangle itself, that is.
         *- NN many, scaling up helps reduce (running overlap remover removes totally)
         -- LN many, scaling up helps reduce (running overlap remover may make it better or worse)
        
        After RemoveOverlaps()
         *- LL == 0
         -- NN == 0, unless algorithm failed
         *- LN some
         
         Note: * indicates the things we are looping and testing
        """
        NODE_NODE = 3
        MAX_SCALE = 1.4
        SCALE_STEP = 0.2
        SCALE_START = 3.2
        
        self.controller.coordmapper.Recalibrate(scale=SCALE_START)
        for i in range(15):
            self.controller.coordmapper.Recalibrate(scale=self.controller.coordmapper.scale - SCALE_STEP)
            self.controller.AllToWorldCoords()

            if animate:
                self.controller.stateofthenation()
            
            """Pre Overlap Removal"""
            
            # see how many INITIAL, PRE OVERLAP REMOVAL line-line crossings there are.
            num_line_line_crossings = len(self.graph.CountLineOverLineIntersections())
            if num_line_line_crossings > 0:
                print "Mad: Aborting - no point since found %d tangled, post spring layout LL crossings!" % num_line_line_crossings
                break

            # see how many INITIAL, PRE OVERLAP REMOVAL node-node overlaps the expansion fixes
            num_node_node_overlaps = self.controller.overlap_remover.CountOverlaps()

            """Remove Overlaps (NN)"""
            self.controller.overlap_remover.RemoveOverlaps(watch_removals=False)

            """Post Overlap Removal"""

            # How many LN reduced (or perhaps increased) after expansion & post removing NN overlaps
            num_line_node_crossings = self.graph.CountLineOverNodeCrossings()['ALL']/2
            
            # How many LL reduced (or perhaps increased) after expansion & post removing NN overlaps
            num_line_line_crossings = len(self.graph.CountLineOverLineIntersections())

            print "Mad: At scale %.1f LL %d NN %d LN %d" % (self.controller.coordmapper.scale, num_line_line_crossings, num_node_node_overlaps, num_line_node_crossings)
        
            if strategy == ":reduce pre overlap removal NN overlaps":
                if num_node_node_overlaps <= NODE_NODE:
                    print "Mad: Aborting expansion since num NN overlaps <= %d" % NODE_NODE
                    break
            elif strategy == ":reduce post overlap removal LN crossings":
                if num_line_node_crossings == 0:
                    print "Mad: Finished expansion since LN crossings == 0 :-)"
                    break
            elif strategy == ":reduce post overlap removal LN and LL crossings":
                if num_line_node_crossings == 0 and num_line_node_crossings == 0:
                    print "Mad: Finished expansion since LN and LL crossings == 0 :-)"
                    break
            else:
                assert False, "Mad: unknown strategy"
    
            # Never accept LN crossings introduced as a result of expansion
            #if num_line_node_crossings > 0:
            #    print "Mad: Warning - introduced LN crossings as a result of expansion, expanding more..."
            #    continue  # risky since we avoid MAX_SCALE check
            
            if self.controller.coordmapper.scale < MAX_SCALE:
                print "Mad: Aborting expansion - gone too far."
                break
    
        print "Mad: End - scale ended up as ", self.controller.coordmapper.scale

        if animate:
            self.controller.stateofthenation()
        #self.stage2() # does overlap removal and stateofthenation
        
        return self.controller.coordmapper.scale, num_line_line_crossings, num_node_node_overlaps, num_line_node_crossings

    def LayoutAndGetVitalStats(self, scale, animate=False):
        """
        Do a layout and expand directly to the original scale, and calc vitals stats
        Same as ScaleUpMadly except only one scale made
        """
        
        # TODO
        
        return self.controller.coordmapper.scale, num_line_line_crossings, num_node_node_overlaps, num_line_node_crossings

        