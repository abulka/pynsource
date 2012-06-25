    def RedrawEverything(self):
        print "Draw: RedrawEverything"
        diagram = self.GetDiagram()
        canvas = self
        assert self == canvas == diagram.GetCanvas()

        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        for shape in self.umlboxshapes:
            shape.Move(dc, shape.GetX(), shape.GetY())
            if shape.__class__.__name__ == 'DividedShape':
                shape.SetRegionSizes()
        diagram.Clear(dc)
        diagram.Redraw(dc)


    def Redraw222(self, clear=True):        # rename  dc_DiagramClearAndRedraw
        print "Draw: Redraw222"			# identical to RedrawEverything() except shapes not moved
        diagram = self.GetDiagram()
        canvas = self
        assert canvas == diagram.GetCanvas()
    
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        
        #for node in self.graph.nodes:    # TODO am still moving nodes in the pynsourcegui version?
        #    shape = node.shape
        #    shape.Move(dc, shape.GetX(), shape.GetY())
        
        if clear:
            diagram.Clear(dc)
        diagram.Redraw(dc)

		
    def stateofthenation(self, animate=False):  # rename  RenderAllUmlGraphNodes_AndRedraw222
		#
		# animate=False   can be removed
		#
        print "Draw: stateofthenation"        # identical to RedrawEverything except move shapes here and
        for node in self.umlworkspace.graph.nodes:   # call Redraw222 which doesnt move shapes.
            self.AdjustShapePosition(node)
        self.Redraw222()
        wx.SafeYield()

    def stage2(self, force_stateofthenation=False, watch_removals=True):   #  rename removeoverlaps_And_RedrawIfNecc
        print "Draw: stage2 force_stateofthenation=", force_stateofthenation
        ANIMATION = False
        
        #if ANIMATION:
        #    self.graph.SaveOldPositionsForAnimationPurposes()
        #    watch_removals = False  # added this when I turned animation on.
        
        self.overlap_remover.RemoveOverlaps(watch_removals=watch_removals)
        if self.overlap_remover.GetStats()['total_overlaps_found'] > 0 or force_stateofthenation:
            self.stateofthenation(animate=ANIMATION)		
		

    def AdjustShapePosition(self, node, point=None):   # rename  NodeShapeSetXy_Then_dc_ShapeMoveLinks
		#
		# point=None   can be removed
		#
		# Here we call setpos which sets the pos but doesn't actually render anything, which is why you need
		# a real shape.Move(dc, shape.GetX(), shape.GetY()) later
		#
        print "Draw:  AdjustShapePosition", node.left, node.top
        assert node.shape
        
        if point:
            x, y = point
        else:
            x, y = node.left, node.top
            
        # Don't need to use node.shape.Move(dc, x, y, False)
        setpos(node.shape, x, y)

        # But you DO need to use a dc to adjust the links
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)
        node.shape.MoveLinks(dc)
		
		
