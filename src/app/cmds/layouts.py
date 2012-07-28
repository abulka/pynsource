from base_cmd import CmdBase

class CmdLayout(CmdBase):
    def execute(self):
        canvas = self.context.umlwin
        
        if canvas.GetDiagram().GetCount() == 0:
            return
        canvas.layout_and_position_shapes()
        
    def undo(self):  # override
        """ Docstring """
        # not implemented

class CmdLayoutExpandContractBase(CmdBase):   # BASE
    def __init__(self, remap_world_to_layout=False, remove_overlaps=True):
        self.remap_world_to_layout = remap_world_to_layout
        self.remove_overlaps = remove_overlaps

    def ChangeScale(self, delta):
        coordmapper = self.context.coordmapper
        
        # Experimental - only needed when you've done world coord changes 
        if self.remap_world_to_layout:
            coordmapper.AllToLayoutCoords()
            
        coordmapper.Recalibrate(scale=coordmapper.scale + delta)
        coordmapper.AllToWorldCoords()
        numoverlaps = self.context.umlwin.overlap_remover.CountOverlaps()
        if self.remove_overlaps:
            self.context.umlwin.stage2(force_stateofthenation=True, watch_removals=False) # does overlap removal and stateofthenation
        else:
            self.context.umlwin.stateofthenation()
            
class CmdLayoutExpand(CmdLayoutExpandContractBase):
    def execute(self):
        if self.context.coordmapper.scale > 0.8:
            self.ChangeScale(-0.2)
            #print "expansion ", self.coordmapper.scale
        else:
            print "Max expansion prevented.", self.context.coordmapper.scale

class CmdLayoutContract(CmdLayoutExpandContractBase):
    def execute(self):
        if self.context.coordmapper.scale < 3:
            self.ChangeScale(0.2)
            #print "contraction ", self.coordmapper.scale
        else:
            print "Min expansion thwarted.", self.context.coordmapper.scale


from blackboard_thread import MainBlackboardFrame
from layout.blackboard import LayoutBlackboard

class CmdDeepLayout(CmdBase):
    def execute(self):
        """Init Main App."""
        f = MainBlackboardFrame(parent=self.context.frame)
        f.Show(True)
        
        b = LayoutBlackboard(graph=self.context.model.graph, umlwin=self.context.umlwin)
        f.SetBlackboardObject(b)
        f.Start(num_attempts=3)
        print "CmdDeepLayout end"