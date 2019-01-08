class ClassEntry:
    def __init__(self, name=""):
        self.name = name  # new and optional.
        self.name_long = ""  # new and optional.
        self.stack_functions = [
            False
        ]  # new, only used by ast parser.  can we make this empty? for init?

        self.defs = []
        self.attrs = []
        self.classdependencytuples = []
        self.classesinheritsfrom = []
        self.ismodulenotrealclass = 0

    def FindAttribute(self, attrname):
        """
        Return
           boolean hit, index pos
        """
        for attrobj in self.attrs:
            if attrname == attrobj.attrname:
                return 1, attrobj
        return 0, None

    def AddAttribute(self, attrname, attrtype):
        """
        If the new info is different to the old, and there is more info
        in it, then replace the old entry.
        e.g. oldattrtype may be ['normal'
             and new may be     ['normal', 'many']
        """
        haveEncounteredAttrBefore, attrobj = self.FindAttribute(attrname)
        if not haveEncounteredAttrBefore:
            self.attrs.append(Attribute(attrname, attrtype))
        else:
            # See if there is more info to add re this attr.
            if len(attrobj.attrtype) < len(attrtype):
                attrobj.attrtype = attrtype  # Update it.

        # OLD CODE
        # if not self.FindAttribute(attrname):
        #    self.attrs.append(Attribute(attrname, attrtype))

    def __str__(self):
        if self.name:
            return self.name
        else:
            return repr(self)


class Attribute:
    def __init__(self, attrname, attrtype="normal"):
        self.attrname = attrname
        self.attrtype = attrtype
