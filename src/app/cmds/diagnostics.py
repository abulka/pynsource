from .base_cmd import CmdBase
import wx

class CmdDumpUmlWorkspace(CmdBase):
    def execute(self):
        # Also called by Snapshot manager.
        # When create Snapshot manager we pass ourselves as a controller and DumpStatus() is expected to exist.
        import locale
        locale.setlocale(locale.LC_ALL, '')  # http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x
        
        print("v" * 50)
        self.context.displaymodel.Dump()
        print()
        print("  MISC Scaling etc info ")
        print()
        self.context.coordmapper.DumpCalibrationInfo(dump_nodes=False)
        print("line-line intersections", len(self.context.displaymodel.graph.CountLineOverLineIntersections()))
        print("node-node overlaps", self.context.overlap_remover.CountOverlaps())
        print("line-node crossings", self.context.displaymodel.graph.CountLineOverNodeCrossings()['ALL']/2) #, self.graph.CountLineOverNodeCrossings()
        print("bounds", self.context.displaymodel.graph.GetBounds())


        #print "SHAPE to classname list: -------------------"
        #for shape in self.umlboxshapes:
        #    print 'shape', shape, shape.node.classname

        print()
        print("^" * 50)
