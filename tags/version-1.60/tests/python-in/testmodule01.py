class ParseMeTest:
    def __init__(self):
        self.a = 10            # class attribute
        self.b = Blah()        # class attribute COMPOSITE
        self.a.c = 20          # skip
        self.__class__.d = 30  # static class attribute
        self.e.append(10)      # class attribute (list/vector)
        self.e2.append("10")   # class attribute (list/vector)
        self.f.append(Blah())  # class attribute (list/vector) COMPOSITE
        
    def IsInBattle(self):
        if not self.tileinfo:
            return 0
        return self.tileinfo.battletriggered

    def DoA(self):
        pass
class ParseMeTest2(ParseMeTest):
    def DoB(self):
        self._secretinfo = 2

    