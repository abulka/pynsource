from base_cmd import CmdBase

class CmdNodeDelete(CmdBase):
    """ Delete nodes """

    def execute(self):
        """ Docstring """
        print 'doing CmdNodeDelete'
        #self._oldstate = TestCase01.fakeScreen
        
        assert self.umlwin
        
        for shape in self.umlwin.GetDiagram().GetShapeList():
            if shape.Selected():
                self.umlwin.CmdZapShape(shape)
            
    def redo(self):  # override
        """ Docstring """
        # print 'redo B'
        self.execute()

    def undo(self):  # override
        """ Docstring """
        # print 'undo B'
        #TestCase01.fakeScreen = self._oldstate
        
