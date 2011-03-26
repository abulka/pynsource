# node overlap removal
# By Andy Bulka

# Removing node overlap is actually no easy task. None of the layout
# algorithms, or few perhaps in the graphing world take vertex
# size into account. As such, the technique is to usually run the layout
# you desire and then run an overlap removal algorithm afterwards which
# should slightly move the vertices around to remove overlap.

from graph import GraphNode, Div

MARGIN = 5
MAX_CYCLES = 10

class OverlapRemoval:
    
    def __init__(self, graph, gui):
        self.graph = graph
        self.gui = gui
        self.stats = {}
        
    def GetPermutations(self, lzt):
        result = []
        for i in range(0, len(lzt)):
            for j in range(i+1, len(lzt)):
                result.append((lzt[i], lzt[j]))
        return result

    def Hit(self, node1, node2):
        l = max(node1.value.left,   node2.value.left)
        r = min(node1.value.right,  node2.value.right)
        t = max(node1.value.top,    node2.value.top)
        b = min(node1.value.bottom, node2.value.bottom)
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
                    
        print "Overlap %s/%s by %d/%d  (leftnode is %s  topnode is %s)" % (node1.value.id, node2.value.id, xoverlap_amount, yoverlap_amount, leftnode.value.id, topnode.value.id)

        if self.MoveLeftOk(leftnode, deltaX=xoverlap_amount, ignorenode=rightnode):
            proposals.append({'node':leftnode, 'xory':'x', 'amount':-xoverlap_amount, 'clashnode':rightnode})
        else:
            proposals.append({'node':rightnode, 'xory':'x', 'amount':xoverlap_amount, 'clashnode':leftnode})
            
        if self.MoveUpOk(topnode, deltaY=yoverlap_amount, ignorenode=bottomnode):
            proposals.append({'node':topnode, 'xory':'y', 'amount':-yoverlap_amount, 'clashnode':bottomnode})
        else:
            proposals.append({'node':bottomnode, 'xory':'y', 'amount':yoverlap_amount, 'clashnode':topnode})
        #print self.dumpproposals(proposals)
        
        proposals = [p for p in proposals if not p['node'] in self.already_moved_nodes]
        return proposals
    
    def GatherProposal2(self, lastmovedirection, clashingnode, movingnode):
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
        l, t, r, b = movingnode.GetBounds()
        proposednode = GraphNode(Div('temp', top=t+deltaY, left=l+deltaX, width=r-l, height=b-t))
        return self.IsHitting(proposednode, ignorenodes=[movingnode, ignorenode])

    def MoveLeftOk(self, movingnode, deltaX, ignorenode=None):
        return movingnode.value.left - deltaX >= 0 and not self.MoveWouldHitSomething(movingnode, -deltaX, 0, ignorenode)

    def MoveUpOk(self, movingnode, deltaY, ignorenode=None):
        return movingnode.value.top - deltaY >= 0 and not self.MoveWouldHitSomething(movingnode, 0, -deltaY, ignorenode)

    def SortNodesLrtb(self, node1, node2):
        L, R, T, B = 0, 1, 2, 3
        a = [node1, node2, node1, node2] # guess as to who is l,r,t,b with respect to each other
        if a[R].value.left < a[L].value.left: a[L], a[R] = a[R], a[L]
        if a[B].value.top < a[T].value.top:   a[T], a[B] = a[B], a[T]
        return a[L], a[R], a[T], a[B]

    def CalcOverlapAmounts(self, node1, node2):
        leftnode, rightnode, topnode, bottomnode = self.SortNodesLrtb(node1, node2)
        
        # Overlap amounts returned are always positive values
        xoverlap_amount = abs(leftnode.value.right + MARGIN - rightnode.value.left)
        yoverlap_amount = abs(topnode.value.bottom + MARGIN - bottomnode.value.top)
        
        return leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount

    def dumpproposal(self, prop):
        return "  moving %s.%s by %s" % (prop['node'].value.id, prop['xory'], prop['amount'])
        
    def dumpproposals(self, props):
        msg = "  Proposals: "
        for p in props:
            msg += self.dumpproposal(p)
        return msg
        
    def dumpignorelist(self):
        msg = ""
        for n in ignorenodes:
            msg += " %s," % (n.value.id)
        #print "  ignore list now ", msg

    def ApplyProposal(self, proposal):
        #print self.dumpproposal(proposal)
        if proposal['xory'] == 'x':
            proposal['node'].value.left += proposal['amount']
        else:
            proposal['node'].value.top += proposal['amount']
        self.already_moved_nodes.append(proposal['node'])

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
        # under certain circumstances, for aesthetics, despite already_moved_nodes list

        def CheckForPostMoveMove(clashingnode):
            proposal = self.GatherProposal2(lastmovedirection, clashingnode, movednode)
            if proposal:
                self.ApplyProposal(proposal)
                self.total_postmove_fixes += 1
                #print "  * extra correction to %s" % (movednode.value.id)

        clashingnode = self.IsHitting(movednode)  # What am I clashing with now?
        if clashingnode:
            CheckForPostMoveMove(clashingnode)
        
    def InitStats(self):
        self.total_overlaps_found = 0
        self.total_contractive_moves = 0
        self.total_expansive_moves = 0
        self.total_postmove_fixes = 0

    def SetStats(self, total_iterations):
        self.stats['total_iterations'] = total_iterations
        self.stats['total_overlaps_found'] = self.total_overlaps_found
        self.stats['total_postmove_fixes'] = self.total_postmove_fixes
        self.stats['total_contractive_moves'] = self.total_contractive_moves
        self.stats['total_expansive_moves'] = self.total_expansive_moves

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
                
        return numfixed_thiscycle, found_an_overlap_thiscycle
    
    def RemoveOverlaps(self):     # Main method to call
        total_iterations = 0
        self.already_moved_nodes = []
        self.InitStats()
        for i in range(0, MAX_CYCLES):
            total_iterations += 1
            
            numfixed_thiscycle, found_an_overlap_thiscycle = self.RunRemovalCycle()
            
            if not found_an_overlap_thiscycle:
                break  # job done
            else:
                if numfixed_thiscycle == 0:         # found overlaps but none fixed
                    self.already_moved_nodes = []   # so reset bans
                else:
                    self.gui.stateofthenation()     # refresh gui
                    
        if self.total_overlaps_found:
            were_all_overlaps_removed = not found_an_overlap_thiscycle
            if found_an_overlap_thiscycle:
                print "Exiting with overlaps remaining :-("
        else:
            were_all_overlaps_removed = True
            print "No Overlaps found at all."

        self.SetStats(total_iterations)

        return were_all_overlaps_removed, self.total_overlaps_found

