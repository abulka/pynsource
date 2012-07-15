from base_cmd import CmdBase

class CmdInsertNewComment(CmdBase):
    """ Delete nodes """

    def execute(self):
        """ Docstring """
        print 'doing CmdNodeDelete'
        #self._oldstate = TestCase01.fakeScreen
        
        assert self.umlwin
        
        self.umlwin.CmdInsertNewComment()
            
    def redo(self):  # override
        """ Docstring """
        # print 'redo B'
        self.execute()

    def undo(self):  # override
        """ Docstring """
        # print 'undo B'
        #TestCase01.fakeScreen = self._oldstate
        
