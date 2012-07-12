class SomePythonBug:
    def Do(self, param=[]):
        assert param == [], param
        param.append(1)  # appending to or extending an optional parameter affects it for next time!

b = SomePythonBug()

# Triggers the bug
b.Do()
b.Do()

# Avoids the bug by forcing param to be []
b.Do()
b.Do(param=[])

print "Done"
