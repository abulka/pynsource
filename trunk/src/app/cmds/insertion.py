from base_cmd import CmdBase

class CmdInsertNewComment(CmdBase):
    """ Delete nodes """

    def execute(self):
        """ Docstring """
        assert self.umlwin
        self.umlwin.CmdInsertNewComment()
            
    def undo(self):  # override
        """ Docstring """
        # not implemented

        
