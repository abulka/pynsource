# Test submitted by Antonio

class Vert:
    def __init__(self, co):
        self.prev = self
        self.next = self

class Polygon:
    def __init__(self, vlist = None):
        self.verts = []
        if vlist:
            for v in vlist:
                self.appendVert(Vert(v))

    def appendVert(self, v):
#        self.verts.append(v)
        self.verts.append(Vert())


"""
Hi again Antonio,

You wrote:
> The Polygon Class should have some sort of association with the Vert 
> class, but pynsource just detect an association with a class named V 
> that is not really present in the code... any clue?

The heart of your code is:

------------------
class Vert:
    def __init__(self, co):
        self.prev = self
        self.next = self

class Polygon:
    def __init__(self, vlist = None):
        self.verts = []
        if vlist:
            for v in vlist:
                self.appendVert(Vert(v))

    def appendVert(self, v):
        self.verts.append(v)
------------------

and what PyNSource is doing is assuming the .append(v) expression is appending a class of type v.  This is a bad guess, since the type of v is Vert.  But in a dynamically typed language, how does PyNSource figure this out?  Its very hard.  If you change the line to append Vert() then PyNSource does the right thing e.g.

    def appendVert(self, v):
#        self.verts.append(v)
        self.verts.append(Vert())

The only thing I can think of doing is doing some sort of lookahead ahead and build a list of class names.  Then since v is not a classname, it would not be accidentally created as one.  However the negative sideeffect of this proposed new behaviour is that you would have to make sure you imported every relevant module to populate the list of possible classes, in order for classes to be recognized properly.  May not be a bad thing.

So that would get rid of the erroneous 'v' class.  How do we then do the right thing and connect Polygon -->* Vert

Well, in the absence of type information, perhaps PyNSource could scan around and try to guess the type of variables, and go by that.  Is there an algorithm that could correctly guess (in the above example code) that v is of type Vert?  Let me know and I'll implement it, but it looks hard.  !

Cheers,
Andy Bulka
www.atug.com/andypatterns

"""
