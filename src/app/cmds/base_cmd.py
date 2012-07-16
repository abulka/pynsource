import sys
if ".." not in sys.path: sys.path.append("..")

from command_pattern import Command

class CmdBase(Command):
    """ Base uml command with hand init """

    def __init__(self, context):
        """ pass in all the relevant context """
        self.context = context

    def redo(self):
        """ redoes the command. Usually as simple as re executing it. """
        self.execute()
