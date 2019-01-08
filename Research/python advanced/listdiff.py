import copy


def listdiff__(list1, list2):
    list1 = copy.copy(list1)
    list2 = copy.copy(list2)
    notfound = []
    for el in list1:
        if el in list2:
            list2.remove(el)
        else:
            notfound.append(el)
    notfound.extend(list2)
    for el in list2:
        if el in list1:
            list1.remove(el)
        else:
            notfound.append(el)
    notfound.extend(list1)
    return notfound


import collections


def listdiff(list1, list2):
    """
    Difference between two lists, taking into account duplicates too
    """
    dups = []

    def finddups(lzt):
        y = collections.Counter(lzt)
        dups.extend([i for i in y if y[i] > 1])

    def realdiffs(a, b):
        """
        Now lets say you wanted to know which elements in the two lists did not
        overlap at all between them. This is sometimes referred to as the
        symmetric distance. The following code should serve this purpose and
        should give you "jkl" and "abc".
        http://code.hammerpig.com/find-the-difference-between-two-lists-with-python.html
        """
        c = set(a).union(set(b))
        d = set(a).intersection(set(b))
        return list(c - d)

    finddups(list1)
    finddups(list2)
    realdiffs = realdiffs(list1, list2)
    realdiffs.extend(dups)
    return realdiffs


def listdiff2(list1, list2):
    # UNfinished
    appearinboth = set(list1) & set(list2)


"""
a = ['One', 'Two', 'Three', 'Four']
b = ['One', 'Two']
print list(set(a) - set(b))

diff_list = [item for item in a if not item in b]
print diff_list

c = set(a).union(set(b))
d = set(a).intersection(set(b))
print list(c - d)

a = [1,2,3]
b = [2,3,4]
#print list(set(a) - set(b))
#print list(set(b) - set(a))

#diff_list = [item for item in a if not item in b]
#print diff_list

c = set(a).union(set(b))
d = set(a).intersection(set(b))
print list(c - d)
"""

a = [1, 2, 3]
b = [2, 3, 4]

res = listdiff(a, b)
print(res)
assert res == [1, 4]

res = listdiff(b, a)
print(res)
assert res == [1, 4]

c = [3, 4, 5, 6, 7]
res = listdiff(a, c)
print(res)
assert res == [1, 2, 4, 5, 6, 7]

a = [1, 2, 3]
b = [2, 3, 3, 4]
res = listdiff(a, b)
print(res)
assert res == [1, 4, 3], res

a = [
    "MainApp",
    "MainApp_Context",
    "wx.App",
    "wx.Appwx.lib.mixins.inspection.InspectionMixin",
    "object",
    "Log",
    "UmlCanvas",
    "App",
    "ConfigObj",
]
b = [
    "wx.App",
    "MainApp",
    "wx.Appwx.lib.mixins.inspection.InspectionMixin",
    "MainApp",
    "object",
    "MainApp_Context",
    "Log",
    "UmlCanvas",
    "App",
    "ConfigObj",
]
res = listdiff(a, b)
print(res)
assert res == ["MainApp"]

print("done")
