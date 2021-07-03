"""
Command Pattern

Command Class and Command Manager for managing the queue.
"""

import logging
from common.logger import config_log
log = logging.getLogger(__name__)
config_log(log)


class Command(object):
    """ Each command is a subclass of this. """

    def execute(self):
        """ Docstring """
        pass

    def undo(self):
        """ Docstring """
        pass

    def redo(self):
        """ Docstring """
        pass


class CommandManager(object):
    """ manages the queue """

    MaxListSize = 2000

    def __init__(self, max_items):
        """ Docstring """
        self._list = []
        self._max_items = max_items
        if self._max_items > CommandManager.MaxListSize:
            self._max_items = CommandManager.MaxListSize
        self._current_undo = -1

    def _can_redo(self):
        """ Docstring """
        return len(self._list) > 0 and self._current_undo < (len(self._list) - 1)

    def _can_undo(self):
        """ Docstring """
        return self._current_undo >= 0

    def _get_current_item(self):
        """ Docstring """
        # returns a Command
        if self._can_undo():
            return self._list[self._current_undo]
        else:
            return None

    def _get_current_redo_item(self):
        """ Docstring """
        # returns a Command
        if self._can_redo():
            return self._list[self._current_undo + 1]  # succ(CurrentUndo)
        else:
            return None

    def _get_max_items(self):
        """ Docstring """
        return self._max_items

    def _set_max_items(self, max_items):
        """ Docstring """
        self._max_items = max_items
        # delete oldest entries if list is shrinking
        if max_items < self._max_items:
            for _ in range(0, (self._max_items - max_items) - 1):
                self._list.pop(0)
        self._max_items = max_items
        self._current_undo = len(self._list) - 1

    # public

    def clear(self):
        """ Docstring """
        del self._list[0:]
        self._current_undo = -1

    def redo(self, num):
        """ Docstring """
        for _ in range(1, num + 1):
            if self._can_redo():
                self.currentRedoItem.redo()
                self._current_undo += 1

    def remove_last_item(self):
        """ Docstring """
        if len(self._list):
            self._list.pop()
        self._current_undo -= 1

    def run(self, item):
        """
        Main API for driving the command manager.
        Pass in a command object.
        """
        log.info(f'Command: {item}')

        item.execute()

        # Get rid of any commands in redo list (those above the pointer)
        if self._can_redo():
            for _ in range(len(self._list) - 1, self._current_undo + 1, -1):
                self._list.pop()

        # check if stack is full; if so, pop off oldest command
        if len(self._list) >= self._max_items:
            self._list.pop(0)

        self._list.append(item)

        # point at top of stack (the size of which may have been modified above
        # can't just inc(CurrentUndo)
        self._current_undo = len(self._list) - 1

    def undo(self, num):
        """ Docstring """
        # print 'undo module num is', num
        if self._can_undo():
            for _ in range(1, num + 1):
                self.currentItem.undo()
                self._current_undo -= 1
                if not self._can_undo():
                    return

    currentItem = property(_get_current_item)
    currentRedoItem = property(_get_current_redo_item)
    maxItems = property(_get_max_items, _set_max_items)


import unittest


class TestCase01(unittest.TestCase):
    """ Docstring """

    fakeScreen = ""

    class CmdDoA(Command):
        """ Docstring """

        def __init__(self):
            """ Docstring """
            self._oldstate = ""

        def execute(self):
            """ Docstring """
            # print 'doing A'
            self._oldstate = TestCase01.fakeScreen
            TestCase01.fakeScreen = "aaaaa"

        def redo(self):  # override
            """ Docstring """
            # print 'redo A'
            self.execute()

        def undo(self):  # override
            """ Docstring """
            # print 'undo A'
            TestCase01.fakeScreen = self._oldstate

    class CmdDoB(Command):
        """ Docstring """

        def __init__(self):
            """ Docstring """
            self._oldstate = ""

        def execute(self):
            """ Docstring """
            # print 'doing B'
            self._oldstate = TestCase01.fakeScreen
            TestCase01.fakeScreen = "bbbbbbbbbbbbbbbbbbb"

        def redo(self):  # override
            """ Docstring """
            # print 'redo B'
            self.execute()

        def undo(self):  # override
            """ Docstring """
            # print 'undo B'
            TestCase01.fakeScreen = self._oldstate

    def setUp(self):
        """ Docstring """
        TestCase01.fakeScreen = ""

    def check_can_create_instances(self):
        """ Docstring """
        Command()
        CommandManager(100)

    def check_BasicUndo_01(self):
        """ Docstring """
        undoStack = CommandManager(100)
        cmd = TestCase01.CmdDoA()

        assert TestCase01.fakeScreen == ""

        undoStack.run(cmd)  # cmd.execute
        assert TestCase01.fakeScreen == "aaaaa"

        undoStack.undo(1)
        assert TestCase01.fakeScreen == ""

    def check_fail_if_too_many_undos(self):
        """
        Actually no exception will be raised if you try to keep undoing...
        """
        undoStack = CommandManager(100)
        cmd = TestCase01.CmdDoA()

        assert TestCase01.fakeScreen == ""

        undoStack.run(cmd)  # cmd.execute
        assert TestCase01.fakeScreen == "aaaaa"

        undoStack.undo(1)
        assert TestCase01.fakeScreen == ""

        undoStack.undo(1)
        undoStack.undo(1)

        # self.assertRaises(EHiddenProc, undoStack.undo, 1)

    def check_Redo_01(self):
        """ Docstring """
        undoStack = CommandManager(100)
        cmd = TestCase01.CmdDoA()

        assert TestCase01.fakeScreen == ""

        undoStack.run(cmd)  # cmd.execute
        assert TestCase01.fakeScreen == "aaaaa"

        undoStack.undo(1)
        assert TestCase01.fakeScreen == ""

        undoStack.redo(1)
        assert TestCase01.fakeScreen == "aaaaa"

    def check_Redo_02(self):
        """ Docstring """
        undoStack = CommandManager(100)
        cmd = TestCase01.CmdDoA()

        assert TestCase01.fakeScreen == ""

        undoStack.run(cmd)  # cmd.execute
        assert TestCase01.fakeScreen == "aaaaa"

        undoStack.undo(1)
        assert TestCase01.fakeScreen == ""

        undoStack.redo(2)  # should only be one item on stack, though
        assert TestCase01.fakeScreen == "aaaaa"

        # these shouldn't do anything...
        undoStack.redo(2)
        undoStack.redo(2)
        assert TestCase01.fakeScreen == "aaaaa"

    def check_UndoTwoDifferentCommands(self):
        """ Docstring """
        undoStack = CommandManager(100)
        cmdA = TestCase01.CmdDoA()
        cmdB = TestCase01.CmdDoB()

        assert TestCase01.fakeScreen == ""

        undoStack.run(cmdA)  # cmd.execute
        assert TestCase01.fakeScreen == "aaaaa"

        undoStack.run(cmdB)  # cmd.execute
        assert TestCase01.fakeScreen == "bbbbbbbbbbbbbbbbbbb"

        undoStack.undo(1)
        assert TestCase01.fakeScreen == "aaaaa"

        undoStack.undo(1)
        assert TestCase01.fakeScreen == ""

        undoStack.redo(2)  # should two items on stack
        assert TestCase01.fakeScreen == "bbbbbbbbbbbbbbbbbbb"

        undoStack.undo(2)
        assert TestCase01.fakeScreen == ""

    def check_UndoThreeDifferentCommands(self):
        """ Docstring """
        undoStack = CommandManager(100)
        cmdA = TestCase01.CmdDoA()
        cmdA2 = TestCase01.CmdDoA()
        cmdB = TestCase01.CmdDoB()

        assert TestCase01.fakeScreen == ""

        undoStack.run(cmdA)  # cmd.execute
        assert TestCase01.fakeScreen == "aaaaa"

        undoStack.run(cmdB)  # cmd.execute
        assert TestCase01.fakeScreen == "bbbbbbbbbbbbbbbbbbb"

        undoStack.run(cmdA2)  # cmd.execute
        assert TestCase01.fakeScreen == "aaaaa"

        undoStack.undo(1)
        assert TestCase01.fakeScreen == "bbbbbbbbbbbbbbbbbbb"

        undoStack.undo(1)
        assert TestCase01.fakeScreen == "aaaaa"

        undoStack.undo(1)
        assert TestCase01.fakeScreen == ""


def suite():
    allchecks = []
    allchecks += list(TestCase01.__dict__.keys())
    # allchecks += TestCase02.__dict__.keys()

    def numbersuffix(x, y):
        """ Docstring """
        return cmp(x[-2:], y[-2:])

    for i in allchecks:
        if i.startswith("_check"):
            print("WARNING - only running tests prepended with underscore")
            testprefix = "_check"
            break
    else:
        testprefix = "check"

    suite1 = unittest.makeSuite(TestCase01, testprefix, sortUsing=numbersuffix)
    # suite2 = unittest.makeSuite(TestCase02, testprefix, \
    #            sortUsing=numbersuffix)

    # alltests = unittest.TestSuite((suite1, suite2))
    alltests = unittest.TestSuite((suite1,))
    # alltests = unittest.TestSuite((suite2,))
    return alltests


def main():
    """
    Run all the suites.  To run via a gui, then
        python unittestgui.py NestedDictionaryTest.suite
    Note that I run with VERBOSITY on HIGH  :-) just like in the old days
    with pyUnit for python 2.0
    Simply call
        runner = unittest.TextTestRunner(descriptions=0, verbosity=2)
    The default arguments are descriptions=1, verbosity=1
    """

    runner = unittest.TextTestRunner(descriptions=0, verbosity=2)
    # runner = unittest.TextTestRunner(descriptions=0, verbosity=1)
    runner.run(suite())


if __name__ == "__main__":
    main()
