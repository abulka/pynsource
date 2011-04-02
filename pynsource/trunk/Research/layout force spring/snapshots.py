# snapshots

from graph import Graph

class GraphSnapshotMgr:
    def __init__(self, graph, controller):
        self.graph = graph
        self.controller = controller
        self.Clear()
        self.quick_save_slots = {}

    def Clear(self):
        self.snapshots = []

    def QuickSave(self, slot=1):
        snapshot = self.AddSnapshot(layout_score=-1, LL=-1, NN=-1, LN=-1,
                    scale=self.controller.coordmapper.scale,
                    bounds=(-1,-1), bounds_area_simple=-1,
                    graph_memento=self.graph.GetMementoOfPositions(),
                    quicksave=True)
        self.quick_save_slots['slot'+`slot`] = snapshot
    
    def QuickRestore(self, slot=1):
        snapshot = self.quick_save_slots.get('slot'+`slot`, None)
        if snapshot:
            self.RestoreGraph(snapshot['memento'], snapshot['scale'])

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
            msg += "LL %(LL)2d   NN pre rm overlaps %(NN_pre_OR)2d   LN %(LN)2d   scale %(scale).1f   bounds %(bounds_area_simple)2d  %(bounds)s" % snapshot
            if current_snapshot_index <> None and i == current_snapshot_index:
                msg += " <---"
            print msg
        print '-'*len(header)

    def AddSnapshot(self, layout_score, LL, NN, LN, scale, bounds, bounds_area_simple, graph_memento, quicksave=False):
        
        snapshot = {
            'layout_score':layout_score,  # not used yet
            'LL':LL,
            'NN_pre_OR':NN,
            'LN':LN,
            'scale':scale,
            'bounds':bounds,
            'bounds_area_simple':bounds_area_simple,
            '_original_add_index':len(self.snapshots)+1,
            'memento':graph_memento}
        
        if quicksave:
            return snapshot
        else:
            self.snapshots.append(snapshot)
        
    def Sort(self):
        """
        blackboard now sorting smarter because I have converted snapshots to
        dictionary format and thus can control which elements to sort by and
        whether to maximise or minimise any particular key in that snapshot
        dictionary.
        """
        b = self.snapshots
        #self.snapshots = sorted(b, key=lambda d: (d['LN'], d['LL'], d['bounds_area_simple'], -d['scale'], d['NN_pre_OR']))
        self.snapshots = sorted(b, key=lambda d: (d['LL'], d['LN'], d['bounds_area_simple'], -d['scale'], d['NN_pre_OR']))

