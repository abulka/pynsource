# node overlap removal
# By Andy Bulka

# Removing node overlap is actually no easy task. None of the layout
# algorithms, or few perhaps in the graphing world take vertex
# size into account. As such, the technique is to usually run the layout
# you desire and then run an overlap removal algorithm afterwards which
# should slightly move the vertices around to remove overlap.

from graph import GraphNode

MARGIN = 5
MAX_CYCLES = 20

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

    def GatherProposals(self, node1, node2):
        proposals = []
        leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = self.CalcOverlapAmounts(node1, node2)
                    
        #print "Overlap %s/%s by %d/%d  (leftnode is %s  topnode is %s)" % (node1.id, node2.id, xoverlap_amount, yoverlap_amount, leftnode.id, topnode.id)

        if self.MoveLeftOk(leftnode, deltaX=xoverlap_amount, ignorenode=rightnode):
            proposals.append({'node':leftnode, 'xory':'x', 'amount':-xoverlap_amount, 'clashnode':rightnode})
        else:
            proposals.append({'node':rightnode, 'xory':'x', 'amount':xoverlap_amount, 'clashnode':leftnode})
            
        if self.MoveUpOk(topnode, deltaY=yoverlap_amount, ignorenode=bottomnode):
            proposals.append({'node':topnode, 'xory':'y', 'amount':-yoverlap_amount, 'clashnode':bottomnode})
        else:
            proposals.append({'node':bottomnode, 'xory':'y', 'amount':yoverlap_amount, 'clashnode':topnode})
        
        proposals = [p for p in proposals if not p['node'] in self.nodes_already_moved]
        return proposals
    
    def GatherPostMoveProposal(self, lastmovedirection, clashingnode, movingnode):
        proposal = None
        leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = self.CalcOverlapAmounts(clashingnode, movingnode)
        
        # check the axis opposite to that I just moved
        if lastmovedirection == 'x' and (yoverlap_amount < xoverlap_amount):  # check instant y movement possibilities
            if ((movingnode == topnode) and self.MoveUpOk(movingnode, deltaY=yoverlap_amount)):
                proposal = {'node':movingnode, 'xory':'y', 'amount':-yoverlap_amount, 'clashnode':clashingnode}
                
            if ((movingnode == bottomnode) and not self.MoveWouldHitSomething(movingnode, deltaY=+yoverlap_amount)):
                proposal = {'node':movingnode, 'xory':'y', 'amount':yoverlap_amount, 'clashnode':clashingnode}
                
        if lastmovedirection == 'y' and (xoverlap_amount < yoverlap_amount):
            if ((movingnode == leftnode) and self.MoveLeftOk(movingnode, deltaX=xoverlap_amount)):
                proposal = {'node':movingnode, 'xory':'x', 'amount':-xoverlap_amount, 'clashnode':clashingnode}
                
            if ((movingnode == rightnode) and not self.MoveWouldHitSomething(movingnode, deltaX=+xoverlap_amount)):
                proposal = {'node':movingnode, 'xory':'x', 'amount':+xoverlap_amount, 'clashnode':clashingnode}
        return proposal

    def MoveWouldHitSomething(self, movingnode, deltaX=0, deltaY=0, ignorenode=None):
        # delta values can be positive or negative
        # TODO make this take into account the margin?  Sometimes get very close nodes.
        l, t, r, b = movingnode.GetBounds()
        proposednode = GraphNode('temp', top=t+deltaY, left=l+deltaX, width=r-l, height=b-t)
        return self.IsHitting(proposednode, ignorenodes=[movingnode, ignorenode])

    def MoveLeftOk(self, movingnode, deltaX, ignorenode=None):
        return movingnode.left - deltaX >= 0 and not self.MoveWouldHitSomething(movingnode, -deltaX, 0, ignorenode)

    def MoveUpOk(self, movingnode, deltaY, ignorenode=None):
        return movingnode.top - deltaY >= 0 and not self.MoveWouldHitSomething(movingnode, 0, -deltaY, ignorenode)

    def SortNodesLrtb(self, node1, node2):
        L, R, T, B = 0, 1, 2, 3
        a = [node1, node2, node1, node2] # guess as to who is l,r,t,b with respect to each other
        if a[R].left < a[L].left: a[L], a[R] = a[R], a[L]
        if a[B].top < a[T].top:   a[T], a[B] = a[B], a[T]
        return a[L], a[R], a[T], a[B]

    def CalcOverlapAmounts(self, node1, node2):
        leftnode, rightnode, topnode, bottomnode = self.SortNodesLrtb(node1, node2)
        # Overlap amounts returned are always positive values
        xoverlap_amount = abs(leftnode.right + self.margin - rightnode.left)
        yoverlap_amount = abs(topnode.bottom + self.margin - bottomnode.top)
        return leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount

    def ApplyProposal(self, proposal):
        if proposal['xory'] == 'x':
            proposal['node'].left += proposal['amount']
        else:
            proposal['node'].top += proposal['amount']
        self.nodes_already_moved.append(proposal['node'])

    def ApplyMinimalProposal(self, proposals):
        amounts = [abs(p['amount']) for p in proposals]
        lowest_amount = min(amounts)
        proposal = [p for p in proposals if abs(p['amount']) == lowest_amount][0]
        self.ApplyProposal(proposal)
        if proposal['amount'] < 0:
            self.total_contractive_moves += 1
        else:
            self.total_expansive_moves += 1
        return proposal['node'], proposal['xory']

    def PostMoveAlgorithm(self, movednode, lastmovedirection):
        # Post Move Algorithm - move the same node again, safely (don't introduce oscillations),
        # under certain circumstances, for aesthetics, despite nodes_already_moved list

        def CheckForPostMoveMove(clashingnode):
            proposal = self.GatherPostMoveProposal(lastmovedirection, clashingnode, movednode)
            if proposal:
                self.ApplyProposal(proposal)
                self.total_postmove_fixes += 1
                #print "  * extra correction to %s" % (movednode.id)

        clashingnode = self.IsHitting(movednode)  # What am I clashing with now?
        if clashingnode:
            CheckForPostMoveMove(clashingnode)
        
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
    
    def RunRemovalCycle(self):
        numfixed_thiscycle = 0
        found_an_overlap_thiscycle = False

        for node1, node2 in self.GetPermutations(self.graph.nodes):  # a 'cycle'
            if self.Hit(node1, node2):
                found_an_overlap_thiscycle = True
                self.total_overlaps_found += 1
                
                proposals = self.GatherProposals(node1, node2)
                if not proposals:
                    continue
                
                lastmovednode, lastmovedirection = self.ApplyMinimalProposal(proposals)
                numfixed_thiscycle += 1

                self.PostMoveAlgorithm(lastmovednode, lastmovedirection)  # Optional nicety
                
        return found_an_overlap_thiscycle, numfixed_thiscycle
    
    def ResetBans(self):
        # Stop oscillation by not moving the same node too much
        self.nodes_already_moved = []
        
    def RemoveOverlaps(self):           # Main method to call
        self.InitStats()
        self.ResetBans()
        for total_cycles in range(1, MAX_CYCLES):
            
            found_overlaps, num_overlaps_fixed = self.RunRemovalCycle()
            
            if found_overlaps and num_overlaps_fixed == 0:  # found overlaps but none were fixed ! so try resetting bans
                self.ResetBans()
                
            if num_overlaps_fixed > 0:
                if self.gui:
                    self.gui.stateofthenation()     # refresh gui

            if not found_overlaps:
                break  # job done
                    
        all_overlaps_were_removed = not found_overlaps
        
        self.SetStats(total_cycles, all_overlaps_were_removed)
        return all_overlaps_were_removed

    def CountOverlaps(self):
        count = 0
        for node1, node2 in self.GetPermutations(self.graph.nodes):
            if self.Hit(node1, node2):
                count += 1
        return count
        