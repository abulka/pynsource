# Properties

#In python, you don't need unnecessary getter and setter.
#You can get the same thing in a more beautiful way with property.
#Initially, you can code

class C(object):
  def __init__(self, x):
    self.x = x

obj = C(5)
print "x is currently", obj.x
obj.x = 6    # set
print obj.x  # get

print "-----"

#Later, you can change it to allow getter, setter
class C(object):
  def __init__(self, x):
    self._x = x

  def get_x(self):
    return self._x
  def set_x(self, x):
    print "x is being set (old style setter)"
    self._x = x
  x = property(get_x, set_x)

obj = C(5)
print "x is currently", obj.x
obj.x = 6    # set
print obj.x  # get

#You can use class C in almost the same way, but you
#can add anything else you want to do to get_x, set_x.

print "-----"

#
# new-style properties
#

class C(object):
  def __init__(self, x):
    self._x = x

  @property
  def x(self):
    return self._x
  @x.setter
  def x(self, value):
    print "x is being set (new style)"
    self._x = value

c = C(5)
print "x is currently", c.x
c.x = 6
print c.x
