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

        def getpermutations(lzt):
            result = []
            for i in range(0, len(lzt)):
                for j in range(i+1, len(lzt)):
                    result.append((lzt[i], lzt[j]))
            return result

        def GetBounds(node):
            left = node.value.left
            right = node.value.left + node.value.width
            top = node.value.top
            bottom = node.value.top + node.value.height
            return left, right, top, bottom
        
        def ContractiveMoveWouldStayInBounds(node, deltaX=0, deltaY=0):
            assert deltaX >0 or deltaY >0
            if deltaX:
                return node.value.left - deltaX > 0
            if deltaY:
                return node.value.top - deltaY > 0

        def hit(node1, node2):
            l =   max(node1.value.left, node2.value.left)
            r =  min(node1.value.left+node1.value.width, node2.value.left+node2.value.width)
            t =    max(node1.value.top, node2.value.top)
            b = min(node1.value.top+node1.value.height, node2.value.top+node2.value.height)
            return (r>l) and (b>t)            

        def amhitting(currnode, ignorenode=None):
            for node in self.graph.nodes:
                if node == currnode or node == ignorenode:
                    continue
                if hit(currnode, node):
                    print "  ! sitting here, %s is hitting %s." % (currnode.value.id, node.value.id)
                    return node
            print "  ! sitting here, %s is NOT hitting  anything." % (currnode.value.id)
            return None

        def ContractiveMoveOk(movingnode, deltaY=0, deltaX=0, ignorenode=None):
            return ContractiveMoveWouldStayInBounds(movingnode, deltaX=deltaX, deltaY=deltaY) and \
                    not ContractiveMoveWouldClash(movingnode, deltaX=deltaX, deltaY=deltaY, ignorenode=ignorenode)
    
        def ContractiveMoveWouldClash(movingnode, deltaY=0, deltaX=0, ignorenode=None):
            l, r, t, b = GetBounds(movingnode)  # proposed
            checkednodesmsg = "node %s we are proposing to move: points are %s/%s/%s/%s " % (movingnode.value.id,(l,t), (r,t), (l,b), (r,b))
            
            l -= deltaX
            r -= deltaX
            t -= deltaY
            b -= deltaY
            proposednode = GraphNode(Div('temp moving proposed', top=t, left=l, width=r-l+1, height=b-t+1))
            left, right, top, bottom = GetBounds(proposednode)
            checkednodesmsg += "adjusted to proposed points %s/%s/%s/%s tmpnode %d/%d/%d/%d" % ((l,t), (r,t), (l,b), (r,b), left, right, top, bottom)
            
            for node in self.graph.nodes:
                if node == movingnode or node == ignorenode:
                    continue
                if hit(proposednode, node):
                    print "  ! moving %s by -%d/-%d would hit %s. %s" % (movingnode.value.id, deltaX, deltaY, node.value.id, checkednodesmsg)
                    return node
            print "  ! moving %s by -%d/-%d would NOT HIT anything. %s" % (movingnode.value.id, deltaX, deltaY, checkednodesmsg)
            return None

        def ExpansiveMoveWouldClash(movingnode, deltaY=0, deltaX=0, ignorenode=None):
            assert deltaX >0 or deltaY >0
            l, r, t, b = GetBounds(movingnode)  # proposed
            checkednodesmsg = "node %s we are proposing to move: points are %s/%s/%s/%s " % (movingnode.value.id,(l,t), (r,t), (l,b), (r,b))
            proposednode = GraphNode(Div('temp', top=t+deltaY, left=l+deltaX, width=r-l+deltaX+1, height=b-t+deltaY+1))

            # debug
            left, right, top, bottom = GetBounds(proposednode)
            checkednodesmsg += "adjusted to proposed points tmpnode %d/%d/%d/%d" % (left, right, top, bottom)

            for node in self.graph.nodes:
                if node == movingnode or node == ignorenode:
                    continue
                if hit(proposednode, node):
                    print "  ! expansive moving %s by +%d/+%d would hit %s. %s" % (movingnode.value.id, deltaX, deltaY, node.value.id, checkednodesmsg)
                    return node
            print "  ! expansive moving %s by +%d/+%d would NOT HIT anything. %s" % (movingnode.value.id, deltaX, deltaY, checkednodesmsg)
            return None
        
        def whoisonleft(node1, node2):
            if node1.value.left < node2.value.left:
                return node1, node2
            else:
                return node2, node1

        def whoisontop(node1, node2):
            if node1.value.top < node2.value.top:
                return node1, node2
            else:
                return node2, node1

        def calcbasics(node1, node2):
            leftnode, rightnode = whoisonleft(node1, node2)
            topnode, bottomnode = whoisontop(node1, node2)
            xoverlap_amount = (leftnode.value.left + leftnode.value.width + MARGIN) - rightnode.value.left
            yoverlap_amount = (topnode.value.top + topnode.value.height + MARGIN) - bottomnode.value.top
            return leftnode, rightnode, topnode, bottomnode, abs(xoverlap_amount), abs(yoverlap_amount)

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
            leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = calcbasics(node1, node2)
                        
            print "Overlap %s/%s by %d/%d  (leftnode is %s  topnode is %s)" % (node1.value.id, node2.value.id, xoverlap_amount, yoverlap_amount, leftnode.value.id, topnode.value.id)

            if ContractiveMoveOk(leftnode, deltaX=xoverlap_amount, ignorenode=rightnode):
                proposals.append({'node':leftnode, 'xory':'x', 'amount':-xoverlap_amount, 'clashnode':rightnode})
            else:
                proposals.append({'node':rightnode, 'xory':'x', 'amount':xoverlap_amount, 'clashnode':leftnode})
                
            if ContractiveMoveOk(topnode, deltaY=yoverlap_amount, ignorenode=bottomnode):
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
            leftnode, rightnode, topnode, bottomnode, xoverlap_amount, yoverlap_amount = calcbasics(clashingnode, movingnode)
            # check the axis opposite to that I just moved
            if lastmovedirection == 'x' and (yoverlap_amount < xoverlap_amount):  # check instant y movement possibilities
                if ((movingnode == topnode) and ContractiveMoveOk(movingnode, deltaY=yoverlap_amount)):
                    proposal = {'node':movingnode, 'xory':'y', 'amount':-yoverlap_amount, 'clashnode':clashingnode}
                    
                if ((movingnode == bottomnode) and not ExpansiveMoveWouldClash(movingnode, deltaY=yoverlap_amount)):
                    proposal = {'node':movingnode, 'xory':'y', 'amount':yoverlap_amount, 'clashnode':clashingnode}
                    
            if lastmovedirection == 'y' and (xoverlap_amount < yoverlap_amount):
                if ((movingnode == leftnode) and ContractiveMoveOk(movingnode, deltaX=xoverlap_amount)):
                    proposal = {'node':movingnode, 'xory':'x', 'amount':-xoverlap_amount, 'clashnode':clashingnode}
                    
                if ((movingnode == rightnode) and not ExpansiveMoveWouldClash(movingnode, deltaX=xoverlap_amount)):
                    proposal = {'node':movingnode, 'xory':'x', 'amount':+xoverlap_amount, 'clashnode':clashingnode}
            return proposal

        def applytrans(proposal):
            print dumpproposal(proposal)
            if proposal['xory'] == 'x':
                proposal['node'].value.left += proposal['amount']
            else:
                proposal['node'].value.top += proposal['amount']

        def ApplyMinimalProposal(proposals):
            amounts = [abs(p['amount']) for p in proposals]
            lowest_amount = min(amounts)
            proposal = [p for p in proposals if abs(p['amount']) == lowest_amount][0]
            applytrans(proposal)
            return proposal['node'], proposal['amount'], proposal['xory']

        def ApplyPostMoveMove(lastmovedirection, clashingnode, movednode):
            proposal = GatherProposal2(lastmovedirection, clashingnode, movednode)
            if proposal:
                applytrans(proposal)
                print "  * extra correction to %s" % (movednode.value.id)
                return True
            return False
        
        total_iterations = 0
        total_overlaps_found = 0
        total_contractive_moves = 0
        total_postmove_fixes = 0
        ignorenodes = []
        numfixedthisround = 0
        
        for i in range(0,10):
            total_iterations += 1
            numfixedthisround = 0

            self.gui.stateofthenation()
                    
            foundoverlap = False
            for node1, node2 in getpermutations(self.graph.nodes):  # a 'round'
                if hit(node1, node2):
                    foundoverlap = True
                    total_overlaps_found += 1
                    
                    proposals = GatherProposals(node1, node2, ignorenodes)
                    if not proposals:
                        continue
                    
                    movednode, movedamount, lastmovedirection = ApplyMinimalProposal(proposals)
                    ignorenodes.append(movednode)

                    numfixedthisround += 1
                    if movedamount < 0:
                        total_contractive_moves += 1
                    #self.gui.stateofthenation()
                    
                    # Post Move Algorithm - move the same node again, under certain circumstances, despite ignorenodes list
                    clashingnode = amhitting(movednode)  # What am I clashing with now?
                    if clashingnode:
                        if ApplyPostMoveMove(lastmovedirection, clashingnode, movednode):
                            total_postmove_fixes += 1
            if numfixedthisround == 0:
                if total_iterations > 1:
                    print "No fixes made last round, clearing bans"
                ignorenodes = []
            if not foundoverlap:
                break  # exit the failsafe for loop, our job is done !

        if total_overlaps_found:
            print "Overlaps fixed: %d  total_iterations made: %d  total_postmove_fixes: %d  total_contractive_moves: %d  " % (total_overlaps_found, total_iterations, total_postmove_fixes, total_contractive_moves)
            were_all_overlaps_removed = not foundoverlap
            if foundoverlap:
                print "Exiting with overlaps remaining :-("
        else:
            were_all_overlaps_removed = True
            print "No Overlaps found."

        self.stats['total_overlaps_found'] = total_overlaps_found
        self.stats['total_iterations'] = total_iterations
        self.stats['total_postmove_fixes'] = total_postmove_fixes
        self.stats['total_contractive_moves'] = total_contractive_moves

        return were_all_overlaps_removed, total_overlaps_found

