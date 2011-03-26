# node overlap removal
# By Andy Bulka

# Removing node overlap is actually no easy task. None of the layout
# algorithms, or few perhaps in the graphing world take vertex
# size into account. As such, the technique is to usually run the layout
# you desire and then run an overlap removal algorithm afterwards which
# should slightly move the vertices around to remove overlap.

from graph import GraphNode, Div

class OverlapRemoval:
    
    def __init__(self, graph, gui):
        self.graph = graph
        self.gui = gui
        self.stats = {}
        
    def remove_overlaps(self, fix=True):
        
        MARGIN = 5

        def GetPermutations(lzt):
            result = []
            for i in range(0, len(lzt)):
                for j in range(i+1, len(lzt)):
                    result.append((lzt[i], lzt[j]))
            return result

        def Hit(node1, node2):
            l = max(node1.value.left,   node2.value.left)
            r = min(node1.value.right,  node2.value.right)
            t = max(node1.value.top,    node2.value.top)
            b = min(node1.value.bottom, node2.value.bottom)
            return (r>l) and (b>t)            

        def IsHitting(currnode, ignorenode=None, ignorenodes=[]):
            for node in self.graph.nodes:
                if node == currnode or node == ignorenode or node in ignorenodes:
                    continue
                if Hit(currnode, node):
                    return node
            return None

        def MoveWouldHitSomething(movingnode, deltaX=0, deltaY=0, ignorenode=None):
            # delta values can be positive or negative
            l, t, r, b = movingnode.GetBounds()
            proposednode = GraphNode(Div('temp', top=t+deltaY, left=l+deltaX, width=r-l, height=b-t))
            return IsHitting(proposednode, ignorenodes=[movingnode, ignorenode])

        def MoveLeftOk(movingnode, deltaX, ignorenode=None):
            return movingnode.value.left - deltaX >= 0 and not MoveWouldHitSomething(movingnode, -deltaX, 0, ignorenode)

        def MoveUpOk(movingnode, deltaY, ignorenode=None):
            return movingnode.value.top - deltaY >= 0 and not MoveWouldHitSomething(movingnode, 0, -deltaY, ignorenode)
    
        def SortNodesLrtb(node1, node2):
            L, R, T, B = 0, 1, 2, 3
            a = [node1, node2, node1, node2] # guess as to who is l,r,t,b with respect to each other
            if a[R].value.left < a[L].value.left: a[L], a[R] = a[R], a[L]
            if a[B].value.top < a[T].value.top:   a[T], a[B] = a[B], a[T]
            return a[L], a[R], a[T], a[B]

        def CalcOverlapAmounts(node1, node2):
            leftnode, rightnode, topnode, bottomnode = SortNodesLrtb(node1, node2)
            
            # Overlap amounts returned are always positive values
            xoverlap_amount = abs(leftnode.value.right + MARGIN - rightnode.value.left)
            yoverlap_amount = abs(topnode.value.bottom + MARGIN - bottomnode.value.top)
            
            return leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount

        def dumpproposal(prop):
            return "  moving %s.%s by %s" % (prop['node'].value.id, prop['xory'], prop['amount'])
            
        def dumpproposals(props):
            msg = "  Proposals: "
            for p in props:
                msg += dumpproposal(p)
            return msg
            
        def dumpignorelist():
            msg = ""
            for n in ignorenodes:
                msg += " %s," % (n.value.id)
            print "  ignore list now ", msg

        def GatherProposals(node1, node2, ignorenodes):
            proposals = []
            leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = CalcOverlapAmounts(node1, node2)
                        
            print "Overlap %s/%s by %d/%d  (leftnode is %s  topnode is %s)" % (node1.value.id, node2.value.id, xoverlap_amount, yoverlap_amount, leftnode.value.id, topnode.value.id)

            if MoveLeftOk(leftnode, deltaX=xoverlap_amount, ignorenode=rightnode):
                proposals.append({'node':leftnode, 'xory':'x', 'amount':-xoverlap_amount, 'clashnode':rightnode})
            else:
                proposals.append({'node':rightnode, 'xory':'x', 'amount':xoverlap_amount, 'clashnode':leftnode})
                
            if MoveUpOk(topnode, deltaY=yoverlap_amount, ignorenode=bottomnode):
                proposals.append({'node':topnode, 'xory':'y', 'amount':-yoverlap_amount, 'clashnode':bottomnode})
            else:
                proposals.append({'node':bottomnode, 'xory':'y', 'amount':yoverlap_amount, 'clashnode':topnode})
            print dumpproposals(proposals)
            
            proposals = [p for p in proposals if not p['node'] in ignorenodes]
            if not proposals:
                print "  All proposals eliminated - worry about this overlap later"
            return proposals
        
        def GatherProposal2(lastmovedirection, clashingnode, movingnode):
            proposal = None
            leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = CalcOverlapAmounts(clashingnode, movingnode)
            # check the axis opposite to that I just moved
            if lastmovedirection == 'x' and (yoverlap_amount < xoverlap_amount):  # check instant y movement possibilities
                if ((movingnode == topnode) and MoveUpOk(movingnode, deltaY=yoverlap_amount)):
                    proposal = {'node':movingnode, 'xory':'y', 'amount':-yoverlap_amount, 'clashnode':clashingnode}
                    
                if ((movingnode == bottomnode) and not MoveWouldHitSomething(movingnode, deltaY=+yoverlap_amount)):
                    proposal = {'node':movingnode, 'xory':'y', 'amount':yoverlap_amount, 'clashnode':clashingnode}
                    
            if lastmovedirection == 'y' and (xoverlap_amount < yoverlap_amount):
                if ((movingnode == leftnode) and MoveLeftOk(movingnode, deltaX=xoverlap_amount)):
                    proposal = {'node':movingnode, 'xory':'x', 'amount':-xoverlap_amount, 'clashnode':clashingnode}
                    
                if ((movingnode == rightnode) and not MoveWouldHitSomething(movingnode, deltaX=+xoverlap_amount)):
                    proposal = {'node':movingnode, 'xory':'x', 'amount':+xoverlap_amount, 'clashnode':clashingnode}
            return proposal

        def ApplyProposal(proposal):
            print dumpproposal(proposal)
            if proposal['xory'] == 'x':
                proposal['node'].value.left += proposal['amount']
            else:
                proposal['node'].value.top += proposal['amount']

        def ApplyMinimalProposal(proposals):
            amounts = [abs(p['amount']) for p in proposals]
            lowest_amount = min(amounts)
            proposal = [p for p in proposals if abs(p['amount']) == lowest_amount][0]
            ApplyProposal(proposal)
            return proposal['node'], proposal['amount'], proposal['xory']

        def CheckForPostMoveMove(lastmovedirection, clashingnode, movednode):
            proposal = GatherProposal2(lastmovedirection, clashingnode, movednode)
            if proposal:
                ApplyProposal(proposal)
                print "  * extra correction to %s" % (movednode.value.id)
                return True
            return False
        
        total_iterations = 0
        total_overlaps_found = 0
        total_contractive_moves = 0
        total_postmove_fixes = 0
        ignorenodes = []
        numfixed_thisround = 0
        
        for i in range(0,10):
            total_iterations += 1
            numfixed_thisround = 0

            self.gui.stateofthenation()
                    
            foundoverlap_thisround = False
            for node1, node2 in GetPermutations(self.graph.nodes):  # a 'round'
                if Hit(node1, node2):
                    foundoverlap_thisround = True
                    total_overlaps_found += 1
                    
                    proposals = GatherProposals(node1, node2, ignorenodes)
                    if not proposals:
                        continue
                    
                    movednode, movedamount, lastmovedirection = ApplyMinimalProposal(proposals)
                    ignorenodes.append(movednode)

                    numfixed_thisround += 1
                    if movedamount < 0:
                        total_contractive_moves += 1
                    #self.gui.stateofthenation()
                    
                    # Post Move Algorithm - move the same node again, under certain circumstances, despite ignorenodes list
                    clashingnode = IsHitting(movednode)  # What am I clashing with now?
                    if clashingnode:
                        if CheckForPostMoveMove(lastmovedirection, clashingnode, movednode):
                            total_postmove_fixes += 1

            if not foundoverlap_thisround:
                break  # job done
            else:
                if numfixed_thisround == 0:  # found overlaps but none fixed
                    ignorenodes = []  # reset bans
            
        if total_overlaps_found:
            print "Overlaps fixed: %d  total_iterations made: %d  total_postmove_fixes: %d  total_contractive_moves: %d  " % (total_overlaps_found, total_iterations, total_postmove_fixes, total_contractive_moves)
            were_all_overlaps_removed = not foundoverlap_thisround
            if foundoverlap_thisround:
                print "Exiting with overlaps remaining :-("
        else:
            were_all_overlaps_removed = True
            print "No Overlaps found."

        self.stats['total_overlaps_found'] = total_overlaps_found
        self.stats['total_iterations'] = total_iterations
        self.stats['total_postmove_fixes'] = total_postmove_fixes
        self.stats['total_contractive_moves'] = total_contractive_moves

        return were_all_overlaps_removed, total_overlaps_found

