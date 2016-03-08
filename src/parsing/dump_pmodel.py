"""
Old Parser results model structure:
-----------------------------------

The parse model has two properties

    class OldParseModel(object):
        def __init__(self):
            self.classlist = {}  # todo should be renamed classes or classes_dict
            self.modulemethods = []
            
where

    .classlist {classname:classentry, ...} where classname is a string, classentry is a class containing
        .ismodulenotrealclass T/F
        .classdependencytuples [(fromclass, toclass), ...]
        .classesinheritsfrom [class, ...]  # todo should be renamed classinheritsfrom (singular)
        .attrs [attrobj, ...]
                .attrname
                .attrtype []  # todo should be renamed attrtypes plural
                .compositedependencies  # todo (calculated in real time, should precalc) ?? DOESN'T EXIST?
        .defs [method, ...]
        
    .modulemethods = [method, ...]

@startuml

class OldParseModel {
    classlist : {}
    modulemethods : [method, ...]
}

class Classes <<Dict>> #Lavender {
    key
    value
}
hide Classes methods
hide ClassDependency methods
hide ClassName methods
hide MethodName methods
hide AttributeName methods
hide Attribute methods
hide OldParseModel methods

OldParseModel --> Classes : classlist
OldParseModel --> "0..*" MethodName : modulemethods
Classes --> "*" ClassEntry : value
Classes --> "*" ClassName : key
ClassEntry --> "0..*" ClassDependency : classdependencytuples
ClassEntry --> "0..*" ClassName : classesinheritsfrom
ClassEntry --> "0..*" Attribute : attrs
ClassEntry --> "0..*" MethodName : defs
ClassDependency --> ClassName : fromclass
ClassDependency --> ClassName : toclass
Attribute --> AttributeName : attrname

class ClassEntry {
    name
    ismodulenotrealclass : bool
    classdependencytuples : [tuple, ...]
    classesinheritsfrom : [class, ...]
    attrs : [attrobj, ...]
    defs : [method, ...]
    ---
    FindAttribute(attrname)
    AddAttribute(attrname, attrtype)
}
class ClassDependency <<Tuple>> #Lavender {
    fromclass : string
    toclass : string
}

class ClassName <<String>>  #DarkSeaGreen {
    name : string
}

class Attribute {
    attrname : string
    attrtype : string   'normal' | 'many'
}

class AttributeName <<String>>  #DarkSeaGreen {
    name : string
}

class MethodName <<String>>  #DarkSeaGreen {
    name : string
}

note as N1
<b><color:royalBlue>classdependencytuples</color>
is an array of ClassDependency tuples
[(fromclass, toclass), ...]
<u>fromclass</u> and <u>toclass</u> are strings
The former is the attribute name,
the latter is the class name
end note

note as N2
If <u>moduleasclass</u> on the old parser is true
then the module filenames being parsed are
also added to the 'Classes' dictionary as if they were
a class, and the module methods appear as 'defs' of
the ClassEntry.
end note

N1 .. ClassDependency

@enduml
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
    