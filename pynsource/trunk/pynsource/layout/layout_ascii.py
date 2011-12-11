from asciiworkspace import AsciiWorkspace

"""
This layout is generated from the graph model and relies on the call
    graph.nodes_sorted_by_generalisation
which returns the nodes in an order conducive to ascii layout.
"""

class NodeWidthCalc:
    def __init__(self, node):
        self.node = node
        self.maxlen = 0
    def _scan(self, lzt):
        for line in lzt:
            if len(line) > self.maxlen:
                self.maxlen = len(line)
    def calc(self):
        self.maxlen = len(self.node.id)
        self._scan(self.node.attrs)
        self._scan(self.node.meths)
        return self.maxlen

class model_to_ascii_builder:
    def __init__(self):
        self.result = ""
        self.pending_composition_line_output = []
        #self.alternating_lines = False

    def line(self, ch='-', n=30, top_bottom=False):
        CORNER = "+"
        SIDE = "|"
        if top_bottom:
            s = CORNER + ch*n + CORNER
        else:
            s = SIDE + ch*n + SIDE
        return s + "\n"

    def top_or_bottom_line(self, maxwidth):
        return self.line(n=maxwidth, top_bottom=True)

    def attrs_or_meths(self, lzt, maxwidth):
        result = self.line(n=maxwidth)
        for entry in lzt:
            result += "| %-*s |" % (maxwidth -2, entry)
            if self.pending_composition_line_output: # and self.alternating_lines:
                edge = self.pending_composition_line_output.pop()
                result += "  ---->  [ %s ]" % (edge)
            #self.alternating_lines = not self.alternating_lines
            result += "\n"
        return result

    def removeDuplicates(self, lzt):
        # workaround a bug in pynsource where duplicate edges are recorded - to be fixed.  For now remove duplicates.
        return list(set(lzt))

    def CalcRelations(self, node, graph):
        rels_composition = self.removeDuplicates([edge['source'].id for edge in graph.edges if edge['target'].id == node.id and edge.get('uml_edge_type', '') != 'generalisation'])
        #rels_composition = self.removeDuplicates([edge['source'].id for edge in graph.edges if edge['target'].id == node.id and edge.get('uml_edge_type', '') == 'composition'])
        rels_generalisation = self.removeDuplicates([edge['target'].id for edge in graph.edges if edge['source'].id == node.id and edge.get('uml_edge_type', '') == 'generalisation'])
        return rels_composition, rels_generalisation

    def EnsureRootAsWideAsChild(self, maxwidth, child_node):
        # Ensure root or fc is as least as wide as its first child
        if child_node:
            childwidth = NodeWidthCalc(child_node).calc()
            if childwidth > maxwidth:
                maxwidth = childwidth
        return maxwidth

    def LookAheadForNext_fc(self, i, nodes):
        for node,annotation in nodes[i:]:
            if annotation == 'fc':
                return node
            if annotation == 'root':
                return None
        return None

    def LookAheadForNext_tabs(self, i, nodes):
        result = []
        for node,annotation in nodes[i:]:
            if annotation == 'tab':
                result.append(node)
            else:
                break
        return result


    def list_parents(self, rels_generalisation):
        parents = []
        for klass in rels_generalisation:
            parents += "[ " + klass + " ]"
        return parents

    def main(self, graph):
        w = AsciiWorkspace(margin=7)
        
        """
        Calling graph.nodes_sorted_by_generalisation gives us an annotated
        inheritance chain. We then process the nodes in that order, so that
        inheritance can be drawn top down (assuming single inheritance).
        """
        #print [(node.id,annotation) for node,annotation in graph.nodes_sorted_by_generalisation]

        NUM_ROOTS_PER_LINE = 3
        root_counter = 0
        s = ""
        i = 0
        nodes = graph.nodes_sorted_by_generalisation
        for i in range(len(nodes)):
            node,annotation = nodes[i]

            if s:
                """ Make decision re what to do with the last node"""
                
                # Any root needs to be put on a fresh line, and start new node off with a header margin of \n\n
                # Unless the root is part of a bunch of root loners as controlled by NUM_ROOTS_PER_LINE
                if annotation == 'root':
                    w.AddColumn(s)
                    if root_counter == 0:
                        w.Flush()
                        root_counter = NUM_ROOTS_PER_LINE
                    else:
                        root_counter -= 1
                    s = "\n\n\n"
                
                # Any fc (first child) needs to be put on a fresh line, but no header margin cos want to glue to parent
                elif annotation == 'fc':
                    w.AddColumn(s)
                    w.Flush()
                    root_counter = 0
                    s = ""
                # Else tab need to be added to previous line, thus no Flush.  Header margin depends on what the ??? is
                else:
                    w.AddColumn(s)
                    s = ""

            maxwidth = NodeWidthCalc(node).calc()
            # Ensure root or fc is as wide as its fc below it, so that parent nodes are not too thin and so generalisation line connects to parent properly.
            node_next_fc = None
            if annotation in ['fc', 'root']:
                node_next_fc = self.LookAheadForNext_fc(i+1, nodes)
                maxwidth = self.EnsureRootAsWideAsChild(maxwidth, node_next_fc)
            maxwidth += 2

            rels_composition, rels_generalisation = self.CalcRelations(node, graph)
        
            if rels_generalisation:
                if annotation == 'tab':
                    s += "".join(self.list_parents(rels_generalisation)).center(maxwidth, " ") + "\n"
                s += " . ".center(maxwidth, " ") + "\n"
                s += "/_\\".center(maxwidth, " ") + "\n"
                s += " | ".center(maxwidth, " ") + "\n"
                s += " | ".center(maxwidth, " ") + "\n"
                if annotation != 'tab':
                    s += " | ".center(maxwidth, " ") + "\n"     # draw extra line to match the 'tab' case where parents are listed, so that child nodes line up horizontally

            s += self.top_or_bottom_line(maxwidth)
            s += '|%s|' % node.id.center(maxwidth, " ") + "\n"

            self.pending_composition_line_output.extend(rels_composition)

            if node.attrs:
                s += self.attrs_or_meths(node.attrs, maxwidth)
            if node.meths:
                s += self.attrs_or_meths(node.meths, maxwidth)

            s += self.top_or_bottom_line(maxwidth)

            # Add extra height by drawing a veritcal line underneath current node
            # if any subsequent siblings are going to be pushing megarow to be taller
            # This way the generalisation line drawn later by the fc will actually join up.
            # Only need this if there is a fc coming up - hence the check for node_next_fc
            def height_of(node):
                return len(node.meths)+len(node.attrs)
                
            if annotation in ['fc', 'root'] and node_next_fc:
                siblings = [node]
                siblings.extend(self.LookAheadForNext_tabs(i+1, nodes))
                max_megarow_height = max([height_of(sibling) for sibling in siblings])
                padding_needed = max_megarow_height - height_of(node)
                if padding_needed:
                    s += (" | ".center(maxwidth, " ") + "\n") * padding_needed

            s = s.rstrip()

        w.AddColumn(s)
        w.Flush()
        return w.contents
