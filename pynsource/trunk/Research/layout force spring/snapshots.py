# snapshots

from graph import Graph

class GraphSnapshotMgr:
    def __init__(self, graph, controller):
        self.graph = graph
        self.controller = controller
        self.Clear()

    def Restore(self, snapshot_number):
        # snapshot_number is 0 array based
        if not self.snapshots:
            return
        if snapshot_number < len(self.snapshots):
            self.RestoreGraph(self.snapshots[snapshot_number]['memento'], self.snapshots[snapshot_number]['scale'])
            self.DumpSnapshots(current_snapshot_index=snapshot_number, label="Restoring %d" % (snapshot_number+1))
            self.controller.DumpStatus()
        else:
            print "No such snapshot", snapshot_number+1
        
    def RestoreGraph(self, memento, scale):
        self.graph.RestoreWorldPositions(memento)
        self.controller.stateofthenation()

        # Unecessary, but just in case you choose to <- or -> "scale from layout" next
        self.controller.coordmapper.Recalibrate(scale=scale)
        self.controller.AllToLayoutCoords() 
            
    def DumpSnapshots(self, current_snapshot_index=None, label=""):
        # If supplied, current_snapshot is 0 based
        header = '-'*40 + label + '-'*40
        print header
        for i, snapshot in enumerate(self.snapshots):
            msg = "Snapshot %d [%d] " % ((i+1), snapshot['_original_add_index'])
            msg += "Layout score %(layout_score)2d   LL %(LL)2d   NN pre %(NN)2d   LN %(LN)2d   scale %(scale).1f   bounds %(bounds)d" % snapshot
            if current_snapshot_index <> None and i == current_snapshot_index:
                msg += " <---"
            print msg
        print '-'*len(header)

    def Clear(self):
        self.snapshots = []

    def AddSnapshot(self, layout_score, LL, NN, LN, scale, bounds, graph_memento):
        
        snapshot = {
            'layout_score':layout_score,
            'LL':LL,
            'NN':NN,
            'LN':LN,
            'scale':scale,
            'bounds':bounds,
            '_original_add_index':len(self.snapshots)+1,
            'memento':graph_memento}
        
        self.snapshots.append(snapshot)
        
    def Sort(self):
        #self.snapshots.sort()  # should sort by 1st item in tuple, followed by next item in tuple etc. - perfect!
        b = self.snapshots
        self.snapshots = sorted(b, key=lambda d: (d['LN'], -d['scale']))        

