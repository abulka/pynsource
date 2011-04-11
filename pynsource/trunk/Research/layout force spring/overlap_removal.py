# node overlap removal
# By Andy Bulka

# Removing node overlap is actually no easy task. None of the layout
# algorithms, or few perhaps in the graphing world take vertex
# size into account. As such, the technique is to usually run the layout
# you desire and then run an overlap removal algorithm afterwards which
# should slightly move the vertices around to remove overlap.

from graph import GraphNode
import math

MARGIN = 5
MAX_CYCLES = 20
AVOID_LINES = True

class OverlapRemoval:
    
    def __init__(self, graph, margin=MARGIN, gui=None):
        self.graph = graph
        self.gui = gui
        self.margin = margin
        self.stats = {}
        
    def GetPermutations(self, lzt):
        result = []
        for i in range(0, len(lzt)):
            for j in range(i+1, len(lzt)):
                result.append((lzt[i], lzt[j]))
        return result

    def Hit(self, node1, node2):
        l = max(node1.left,   node2.left)
        r = min(node1.right,  node2.right)
        t = max(node1.top,    node2.top)
        b = min(node1.bottom, node2.bottom)
        return (r>l) and (b>t)            

    def IsHitting(self, currnode, ignorenode=None, ignorenodes=[]):
        for node in self.graph.nodes:
            if node == currnode or node == ignorenode or node in ignorenodes:
                continue
            if self.Hit(currnode, node):
                return node
        return None

    def GetAllHits(self, currnode, ignorenodes=[]):
        result = []
        for node in self.graph.nodes:
            if node == currnode or node in ignorenodes:
                continue
            if self.Hit(currnode, node):
                result.append(node)
        return result

    def dumpproposal(self, prop, doing=False):
        if doing:
            msg = "Moving"
        else:
            msg = "to move"
        if prop == None:
            return "-- None --"
        linecrossings = prop.get('linecrossings', 0)
        if linecrossings == 0:
            linecrossings_msg = ""
        else:
            linecrossings_msg = "~%d~" % linecrossings
        return "  %s %s.%s by %s %s %s" % (msg, prop['node'].id, prop['xory'], prop['amount'], prop.get('destdeltaxy', ''), linecrossings_msg)
        
    def dumpproposals(self, props):
        msg = "  Proposals: "
        for p in props:
            msg += self.dumpproposal(p)
        return msg

    def GatherSnugProposals(self, node1, node2):
        proposals = []

        def MoveLeftThenVerticallyOk(movingnode, deltaX, ignorenode=None):
            if not self.MoveLeftStillOnscreen(movingnode, deltaX):
                return None, False
    
            existing_hits_on_right = [node for node in self.GetAllHits(movingnode) if node.left > movingnode.left]
            ignorelist = existing_hits_on_right
            ignorelist.extend([movingnode, ignorenode])
    
            proposednode = self.BuildProposedNode(self.BuildProposalXY(movingnode, -deltaX, 0))  # Move left
            clashingnode = self.IsHitting(proposednode, ignorenodes=ignorelist)
            if not clashingnode:
                return None, False
    
            leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = self.CalcOverlapAmounts(proposednode, clashingnode)
            if clashingnode == bottomnode:
                yoverlap_amount = -yoverlap_amount
            proposednode2 = self.BuildProposedNode(self.BuildProposalXY(proposednode, 0, yoverlap_amount))  # then Vertically
            if proposednode2.top < 0 or proposednode2.left < 0:
                return None, False
            clashingnode2 = self.IsHitting(proposednode2, ignorenodes=ignorelist)
            if not clashingnode2:
                "xy movement ok"
                proposal = self.BuildProposalXY(movingnode, -deltaX, yoverlap_amount)
                return proposal, True
    
            return None, False
        
        def MoveUpThenSidewaysOk(movingnode, deltaY, ignorenode=None):
            if not self.MoveUpStillOnscreen(movingnode, deltaY):
                return None, False
            existing_hits_on_bottom = [node for node in self.GetAllHits(movingnode) if node.top > movingnode.top]
            ignorelist = existing_hits_on_bottom
            ignorelist.extend([movingnode, ignorenode])
    
            proposednode = self.BuildProposedNode(self.BuildProposalXY(movingnode, 0, -deltaY))   # Move Up
            clashingnode = self.IsHitting(proposednode, ignorenodes=ignorelist)
            if not clashingnode:
                return None, False
    
            leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = self.CalcOverlapAmounts(proposednode, clashingnode)
            if clashingnode == rightnode:
                xoverlap_amount = -xoverlap_amount
            proposednode2 = self.BuildProposedNode(self.BuildProposalXY(proposednode, xoverlap_amount, 0))  # then Sideways
            if proposednode2.top < 0 or proposednode2.left < 0:
                return None, False
            clashingnode2 = self.IsHitting(proposednode2, ignorenodes=ignorelist)
            if not clashingnode2:
                "xy movement ok"
                proposal = self.BuildProposalXY(movingnode, xoverlap_amount, -deltaY)
                return proposal, True
    
            return None, False


        leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = self.CalcOverlapAmounts(node1, node2)
        xoverlap_amountQ = leftnode.width + rightnode.width - xoverlap_amount + self.margin + self.margin
        yoverlap_amountQ = topnode.height + bottomnode.height - yoverlap_amount + self.margin + self.margin

        # Lookahead
        proposal, ok = MoveUpThenSidewaysOk(topnode, deltaY=yoverlap_amount, ignorenode=bottomnode)
        if ok:
            proposals.append(proposal)

        proposal, ok = MoveUpThenSidewaysOk(bottomnode, deltaY=yoverlap_amountQ, ignorenode=topnode)
        if ok:
            proposals.append(proposal)

        proposal, ok = MoveLeftThenVerticallyOk(leftnode, deltaX=xoverlap_amount, ignorenode=rightnode)
        if ok:
            proposals.append(proposal)

        proposal, ok = MoveLeftThenVerticallyOk(rightnode, deltaX=xoverlap_amountQ, ignorenode=leftnode)
        if ok:
            proposals.append(proposal)

        proposals = [p for p in proposals if not p['node'] in self.nodes_already_moved]
        return proposals

    def GatherProposals(self, node1, node2):
        proposals = []
        leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = self.CalcOverlapAmounts(node1, node2)
                    
        #print "Overlap %s/%s by %d/%d  (leftnode is %s  topnode is %s)" % (node1.id, node2.id, xoverlap_amount, yoverlap_amount, leftnode.id, topnode.id)

        if self.MoveLeftOk(leftnode, deltaX=xoverlap_amount, ignorenode=rightnode):
            proposals.append({'node':leftnode, 'xory':'x', 'amount':-xoverlap_amount})
        else:
            proposals.append({'node':rightnode, 'xory':'x', 'amount':xoverlap_amount})

        if self.MoveUpOk(topnode, deltaY=yoverlap_amount, ignorenode=bottomnode):
            proposals.append({'node':topnode, 'xory':'y', 'amount':-yoverlap_amount})
        else:
            proposals.append({'node':bottomnode, 'xory':'y', 'amount':yoverlap_amount})

        proposals = [p for p in proposals if not p['node'] in self.nodes_already_moved]
        return proposals
   
    def GatherPostMoveProposal(self, lastmovedirection, clashingnode, movingnode, ignorenode=None, clashingnode_is_really_an_edge=False):
        """
        Check for instant movement possibilities in the opposite direction to
        the last move Normal situations where clashing node is a real node means
        the movingnode will only jump if its a small jump - viz. yoverlap_amount
        < xoverlap_amount or xoverlap_amount < yoverlap_amount. otherwise stay
        put on the overlap and the clashingnode will probably be eventually
        pushed away instead.
        
        When dealing with fake clashing nodes which are really edges, I relax
        the rules and allow a jump to either above or below, regardless of it is
        a small amount. When clashingnode_is_really_an_edge then as well as the
        normal trying of above/left - if that is off screen, we don't just
        abandon, we also try below/right. The below/right move is a jump of
        amountQ as normal amounts are calibrated for left nodes to move left, or
        top nodes to move up and thus not suitable for e.g. top nodes jumping
        down their entire own height plus a bit of the overlap.
        
        Perhaps should turn this routine into two. One for real nodes and
        another for fake clashing nodes (that are really the size of edge
        bounds).
        """
        proposal = None
        leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = self.CalcOverlapAmounts(clashingnode, movingnode)
        ignoreoverlapamounts = clashingnode_is_really_an_edge
        xoverlap_amountQ = leftnode.width + clashingnode.width - xoverlap_amount + self.margin + self.margin
        yoverlap_amountQ = topnode.height + clashingnode.height - yoverlap_amount + self.margin + self.margin
        
        # check the axis opposite to that I just moved
        if lastmovedirection == 'x' and (ignoreoverlapamounts or (yoverlap_amount < xoverlap_amount)):
            if ((movingnode == topnode) and self.MoveUpOk(movingnode, deltaY=yoverlap_amount, ignorenode=ignorenode)):
                proposal = {'node':movingnode, 'xory':'y', 'amount':-yoverlap_amount}
            elif clashingnode_is_really_an_edge and not self.MoveWouldHitSomething(movingnode, deltaY=+yoverlap_amountQ, ignorenode=ignorenode):
                proposal = {'node':movingnode, 'xory':'y', 'amount':+yoverlap_amountQ}
                
            if ((movingnode == bottomnode) and not self.MoveWouldHitSomething(movingnode, deltaY=+yoverlap_amount, ignorenode=ignorenode)):
                proposal = {'node':movingnode, 'xory':'y', 'amount':+yoverlap_amount}
                
        if lastmovedirection == 'y' and (ignoreoverlapamounts or (xoverlap_amount < yoverlap_amount)):
            if ((movingnode == leftnode) and self.MoveLeftOk(movingnode, deltaX=xoverlap_amount, ignorenode=ignorenode)):
                proposal = {'node':movingnode, 'xory':'x', 'amount':-xoverlap_amount}
            elif clashingnode_is_really_an_edge and not self.MoveWouldHitSomething(movingnode, deltaX=+xoverlap_amountQ, ignorenode=ignorenode):
                proposal = {'node':movingnode, 'xory':'x', 'amount':+xoverlap_amountQ}
                
            if ((movingnode == rightnode) and not self.MoveWouldHitSomething(movingnode, deltaX=+xoverlap_amount, ignorenode=ignorenode)):
                proposal = {'node':movingnode, 'xory':'x', 'amount':+xoverlap_amount}
        return proposal

    def Smart(self, proposal):
        SIMPLE_CALC = False #True

        movednode, lastmovedirection = proposal['node'], proposal['xory']
        deltaX, deltaY = self.ExtractDeltaXyFromProposal(proposal)
        clashingnode = self.MoveWouldHitSomething(movednode, deltaX, deltaY)   # builds a propsed node - # TODO refactor all this so we build proposed node ONCE not 3 times !
        if clashingnode:
            # there is a real, clashing node
            proposednode = self.BuildProposedNode(proposal)
            extra_proposal = self.GatherPostMoveProposal(lastmovedirection, clashingnode, proposednode, ignorenode=movednode) # use proposednode not movednode of course
            return extra_proposal

        # check for clashing with a line
        if not AVOID_LINES:
            return None
        proposednode = self.BuildProposedNode(proposal)
        crossings, edges = self.graph.ProposedNodeHitsWhatLines(proposednode, movingnode=proposal['node'])
        if not crossings:
            return None
        
        if crossings:
            print "Hey - opportunity to build a xy proposal due to line crossing against proposed node!", proposednode, crossings, [edge['source'].id + "_" +  edge['target'].id for edge in edges]
            # but can't since GatherPostMoveProposal relies on there being a clashingnode
            # hey so build one!  a fake one that takes the bounds of the line ;-)
            edge = edges[0]                         # TODO - a bit random - there could be more edges
            
            if SIMPLE_CALC:
                l,t = edge['source'].centre_point       # TODO - node will be too big - need to clip off source and target node areas
                r,b = edge['target'].centre_point       # TODO - might be the other way around
            else:
                from geometry_experiments import CalcEdgeBounds2, CalcEdgeBounds3
                l, t, r, b = CalcEdgeBounds2(edge['source'], edge['target'])
                #l, t, r, b = CalcEdgeBounds3(crossings)

            clashingnode = GraphNode('temp_clash', top=t, left=l, width=r-l, height=b-t)
            print "built fake clashingnode", clashingnode
            
            extra_proposal = self.GatherPostMoveProposal(lastmovedirection, clashingnode, proposednode, ignorenode=movednode, clashingnode_is_really_an_edge=True)
            return extra_proposal
    
    def AddPostMoveProposals(self, proposals):
        """
        Post Move Algorithm - propose moving the same node again, safely (don't
        introduce oscillations), under certain circumstances (if original
        proposal was a clash), for aesthetics.
        """
        
        #print "AddPostMoveProposals..."
        #print self.dumpproposals(proposals)
        
        extra_proposals = []
        for proposal in proposals:
            if proposal['xory'] == 'xy':
                continue
            extra_proposal = self.Smart(proposal)
            if extra_proposal:
                x,y = (-1,-1)
                if proposal['xory'] == 'x':        x = proposal['amount']
                if proposal['xory'] == 'y':        y = proposal['amount']
                if extra_proposal['xory'] == 'x':  x = extra_proposal['amount']
                if extra_proposal['xory'] == 'y':  y = extra_proposal['amount']
                assert x != -1
                assert y != -1
                extra_proposals.append( self.BuildProposalXY(proposal['node'], x, y) )
        proposals.extend(extra_proposals)
        
        #if len(extra_proposals) == 0:
        #    print "NO extra proposals"
        #else:
        #    print "Extra proposals are:"
        #    print self.dumpproposals(extra_proposals)
        
        return proposals
    
    def ExtractDeltaXyFromProposal(self, proposal):
        if proposal['xory'] == 'xy':
            deltaX, deltaY = proposal['destdeltaxy']
        elif proposal['xory'] == 'x':
            deltaX, deltaY = proposal['amount'], 0
        elif proposal['xory'] == 'y':
            deltaX, deltaY = 0, proposal['amount']
        return deltaX, deltaY
    
    def BuildProposalXY(self, node, deltaX, deltaY):
        return {'node':node, 'xory':'xy', 'amount': int(math.hypot(deltaX,deltaY)), 'destdeltaxy':(deltaX,deltaY)}
        
    def BuildProposedNode(self, proposal):
        l, t, r, b = proposal['node'].GetBounds()
        deltaX, deltaY = self.ExtractDeltaXyFromProposal(proposal)
        return GraphNode('temp', top=t+deltaY, left=l+deltaX, width=r-l, height=b-t)
    
    def ApplyProposal(self, proposal):
        node = proposal['node']
        assert node.id <> 'temp'
        print 'APPLYING PROPOSAL: ', self.dumpproposal(proposal, doing=True)
        
        x,y = 0,0
        if proposal['xory'] == 'xy':
            x,y = proposal['destdeltaxy']
        elif proposal['xory'] == 'x':
            x = proposal['amount']
        else:
            y = proposal['amount']
        
        node.left += x
        node.top += y
        self.BanNode(node)
        
        # Update Stats
        if proposal['amount'] < 0:
            self.total_contractive_moves += 1
        else:
            self.total_expansive_moves += 1
            if proposal['xory'] == 'xy':
                self.total_postmove_fixes += 1

    def ApplyBestProposal(self, proposals):
        """
        Ignore PostMoveAlgorithm generated "combo xy" proposals for initial
        decision making.  Then find any corresponding "combo xy" move and use it instead.
        Corresponding means if initial_proposal is an x move look for an xy
        move with the same x amount.
        
        Warning, lambda sorting on e.g. p['xory'] == 'xy' turns out to be a True
        which is a 1 which means it is DE-prioritised compared to 0. A little
        counter intuitive.
        """
        initial_proposal = sorted(proposals, key=lambda p: (abs(p['amount']), p['xory'] == 'xy'))[0]
        if initial_proposal['xory'] == 'x':
            xy_proposals = [p for p in proposals if p['xory'] == 'xy' and p['destdeltaxy'][0] == initial_proposal['amount']]
        else:
            xy_proposals = [p for p in proposals if p['xory'] == 'xy' and p['destdeltaxy'][1] == initial_proposal['amount']]

        if xy_proposals:
            proposal = xy_proposals[0]  # transform our initial_proposal to its matching postmove xy
        else:
            """
            If there are no ways to transform our initial minimal movement into
            a xy proposal, then try some simple line crossing avoidance logic.
            Note there may still be some xy's around so deprioritise them.
            """
            least_line_crossing_proposal = sorted(proposals, key=lambda p: (p['linecrossings'], abs(p['amount']), p['xory'] == 'xy'))[0]

            if AVOID_LINES:
                proposal = least_line_crossing_proposal
            else:
                proposal = initial_proposal

            # if there is a similar x or y move amount which is an xy move and the y is negative then choose it
            if proposal['xory'] <> 'xy':
                if proposal['xory'] == 'x':
                    xy_proposals = [p for p in proposals if p['xory'] == 'xy' and abs(p['destdeltaxy'][0]) == abs(proposal['amount'])]
                else:
                    xy_proposals = [p for p in proposals if p['xory'] == 'xy' and abs(p['destdeltaxy'][1]) == abs(proposal['amount'])]
                if xy_proposals:
                    proposal = xy_proposals[0]  # should make sure the xy move is a negative move.  oh well, not now.

        print self.dumpproposals(proposals)
        self.ApplyProposal(proposal)

    def ProposeRemovalsAndApply(self, node1, node2):
        # Return the number of overlaps removed
        proposals = self.GatherProposals(node1, node2)
        if not proposals:
            return 0
        proposals.extend(self.GatherSnugProposals(node1, node2))
        proposals = self.AddPostMoveProposals(proposals)
        proposals = self.CheckForLineCrossings(proposals)  # informational only
        
        self.ApplyBestProposal(proposals)
        return 1
    
    def MoveWouldHitSomething(self, movingnode, deltaX=0, deltaY=0, ignorenode=None, ignorenodes=[]):   # TODO make this take into account the margin?  Sometimes get very close nodes.
        # delta values can be positive or negative
        proposednode = self.BuildProposedNode(self.BuildProposalXY(movingnode, deltaX, deltaY))
        ignorelist = ignorenodes[:]    # ensure you don't mess with incoming parameter, make a copy. This took a while to debug!
        ignorelist.extend([movingnode, ignorenode])
        return self.IsHitting(proposednode, ignorenodes=ignorelist)

    def MoveLeftStillOnscreen(self, movingnode, deltaX):
        return movingnode.left - deltaX >= 0

    def MoveUpStillOnscreen(self, movingnode, deltaY):
        return movingnode.top - deltaY >= 0
    
    def MoveLeftOk(self, movingnode, deltaX, ignorenode=None):
        # Now smarter, node allowed to move left as long as it doesn't hit anything new on the LEFT. Existing hits on right ignored.
        existing_hits_on_right = [node for node in self.GetAllHits(movingnode) if node.left > movingnode.left]
        return self.MoveLeftStillOnscreen(movingnode, deltaX) and not self.MoveWouldHitSomething(movingnode, -deltaX, 0, ignorenode, ignorenodes=existing_hits_on_right)

    def MoveUpOk(self, movingnode, deltaY, ignorenode=None):
        existing_hits_on_bottom = [node for node in self.GetAllHits(movingnode) if node.top > movingnode.top]
        return self.MoveUpStillOnscreen(movingnode, deltaY) and not self.MoveWouldHitSomething(movingnode, 0, -deltaY, ignorenode, ignorenodes=existing_hits_on_bottom)

    def SortNodesLrtb(self, node1, node2):
        L, R, T, B = 0, 1, 2, 3
        a = [node1, node2, node1, node2] # guess as to who is l,r,t,b with respect to each other
        if a[R].left < a[L].left: a[L], a[R] = a[R], a[L]
        if a[B].top < a[T].top:   a[T], a[B] = a[B], a[T]
        return a[L], a[R], a[T], a[B]

    def CalcOverlapAmounts(self, node1, node2):
        leftnode, rightnode, topnode, bottomnode = self.SortNodesLrtb(node1, node2)
        xoverlap_amount = abs(leftnode.right + self.margin - rightnode.left)
        yoverlap_amount = abs(topnode.bottom + self.margin - bottomnode.top)
        # Overlap amounts returned are always positive values
        return leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount

    def CheckForLineCrossings(self, proposals):
        # Amend proposals list with line crossing info.
        newproposals = []
        for proposal in proposals:
            proposednode = self.BuildProposedNode(proposal)
            crossings, edges = self.graph.ProposedNodeHitsWhatLines(proposednode, movingnode=proposal['node'])
            proposal['linecrossings'] = len(crossings)
            newproposals.append(proposal)
        return newproposals
        
    def InitStats(self):
        self.total_overlaps_found = 0
        self.total_contractive_moves = 0
        self.total_expansive_moves = 0
        self.total_postmove_fixes = 0

    def SetStats(self, total_cycles, were_all_overlaps_removed):
        self.stats['warning_msg'] = ""
        self.stats['total_cycles'] = total_cycles
        self.stats['total_overlaps_found'] = self.total_overlaps_found
        self.stats['total_postmove_fixes'] = self.total_postmove_fixes
        self.stats['total_contractive_moves'] = self.total_contractive_moves
        self.stats['total_expansive_moves'] = self.total_expansive_moves
        if not were_all_overlaps_removed:
            self.stats['warning_msg'] = "Exiting with overlaps remaining :-("
        if self.total_overlaps_found == 0:
            self.stats['warning_msg'] = "No Overlaps found at all."

    def GetStats(self):
        return self.stats

    def BanNode(self, node):
        self.nodes_already_moved.append(node)

    def ResetBans(self):
        # Stop oscillation by not moving the same node too much
        self.nodes_already_moved = []
        
    def RunRemovalCycle(self):
        numfixed_thiscycle = 0
        found_an_overlap_thiscycle = False
    
        for node1, node2 in self.GetPermutations(self.graph.nodes):  # a 'cycle'
            if self.Hit(node1, node2):
                found_an_overlap_thiscycle = True
                self.total_overlaps_found += 1
                
                numfixed_thiscycle += self.ProposeRemovalsAndApply(node1, node2)
                
        return found_an_overlap_thiscycle, numfixed_thiscycle
    
    def RemoveOverlaps(self, watch_removals=True):           # Main method to call
        self.InitStats()
        self.ResetBans()
        for total_cycles in range(1, MAX_CYCLES):
            
            found_overlaps, num_overlaps_fixed = self.RunRemovalCycle()
            
            if found_overlaps and num_overlaps_fixed == 0:  # found overlaps but none were fixed ! so try resetting bans
                self.ResetBans()
                
            if num_overlaps_fixed > 0:
                if self.gui and watch_removals:
                    self.gui.stateofthenation()     # refresh gui

            if not found_overlaps:
                break  # job done
                    
        all_overlaps_were_removed = not found_overlaps
        
        self.SetStats(total_cycles, all_overlaps_were_removed)
        return all_overlaps_were_removed

    def CountOverlaps(self):           # Main method to call
        count = 0
        for node1, node2 in self.GetPermutations(self.graph.nodes):
            if self.Hit(node1, node2):
                count += 1
        return count
        