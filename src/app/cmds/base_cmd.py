from common.command_pattern import Command


class CmdBase(Command):
    """ Base command """

    def execute(self):
        raise Exception("virtual, not implemented")

    def undo(self):
        raise Exception("virtual, not implemented")

    def redo(self):
        """ redoes the command. Usually as simple as re executing it. """
        self.execute()
