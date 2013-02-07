"""
Old Parser results model structure:
-----------------------------------

The parse model has two properties

    class AbstractParseModel(object):
        def __init__(self):
            self.classlist = {}
            self.modulemethods = []
            
where

    .classlist {classname:classentry, ...} where classname is a string, classentry is a class containing
        .ismodulenotrealclass T/F
        .classdependencytuples [(fromclass, toclass), ...]
        .classesinheritsfrom [class, ...]  # todo should be renamed classinheritsfrom (singular)
        .attrs [attrobj, ...]
                .attrname
                .attrtype []  # todo should be renamed attrtypes plural
                .compositedependencies  # todo (calculated in real time, should precalc)
        .defs [method, ...]
        
    .modulemethods = [method, ...]]
"""


def dump_old_structure(pmodel):
    res = ""
    
    # TODO build this into ClassEntry
    def calc_classname(classentry):
        if classentry.name_long:
            return classentry.name_long
        else:
            return classentry.name
        
    # repair old parse models #TODO build this into the old parser so that we don't have to do this
    for classname, classentry in  pmodel.classlist.items():
        classentry.name = classname
    
    for classname, classentry in  sorted(pmodel.classlist.items(), key=lambda kv: calc_classname(kv[1])):
        res += "%s (is module=%s) inherits from %s class dependencies %s\n" % \
                                    (calc_classname(classentry),
                                     classentry.ismodulenotrealclass,
                                     classentry.classesinheritsfrom,
                                     classentry.classdependencytuples)

        if classentry.classdependencytuples:
            for tup in classentry.classdependencytuples:
                res += "%s\n" % (tup,)

        for attrobj in classentry.attrs:
            res += "    %-20s (attrtype %s)\n" % (attrobj.attrname,
                                            attrobj.attrtype) # currently skip calc of self._GetCompositeCreatedClassesFor(attrobj.attrname), arguably it should be precalculated and part of the data structure
        for adef in classentry.defs:
            res += "    %s()\n" % adef
    res += "    modulemethods %s\n" % (pmodel.modulemethods)
    return res
    