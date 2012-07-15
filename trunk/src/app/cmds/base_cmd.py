import sys
if ".." not in sys.path: sys.path.append("..")

from command_pattern import Command

class CmdBase(Command):
    """ Base uml command with hand init """

    def __init__(self, umlwin):
        """ pass in all the relevant context """
        self.umlwin = umlwin
