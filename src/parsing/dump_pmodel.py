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

class OldParseModel #AntiqueWhite/Gold {
    classlist : {}
    modulemethods : [method, ...]
}
note left #AntiqueWhite/Gold : Abstract Language Structure Model = ALSM

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

from beautifultable import BeautifulTable
from termcolor import colored  # also install colorama to make this work on windows
import os


# Util

def repair_old_pmodels(pmodel):
    # repair old parse models #TODO build this into the old parser so that we don't have to do this
    for classname, classentry in list(pmodel.classlist.items()):
        classentry.name = classname


# TODO build this into ClassEntry
def calc_classname(classentry):
    if classentry.name_long:
        return classentry.name_long
    else:
        return classentry.name


# New dump

def dump_pmodel(pmodel):
    t = BeautifulTable(maxwidth=760)
    t.set_style(BeautifulTable.STYLE_BOX)  # nice ─── chars

    # subtable = BeautifulTable()
    # subtable.columns.header = ["name", "rank", "gender"]
    # subtable.rows.append(["Jacob", 1, "boy"])
    # subtable.rows.append(["Isabella", 1, "girl"])
    # parent_table = BeautifulTable()
    # parent_table.columns.header = ["Heading 1", "Heading 2"]
    # parent_table.rows.append(["Sample text", "Another sample text"])
    # parent_table.rows.append([subtable, "More sample text"])
    # return parent_table

    repair_old_pmodels(pmodel)

    t.columns.header = ["class name", "inherits from", "attributes", "methods()", "module methods()", "is module", "class dependencies"]
    t.columns.alignment["attributes"] = BeautifulTable.ALIGN_LEFT
    t.columns.alignment["methods()"] = BeautifulTable.ALIGN_LEFT
    t.columns.alignment["module methods()"] = BeautifulTable.ALIGN_LEFT

    have_display_module_methods_once = False

    for classname, classentry in sorted(
        list(pmodel.classlist.items()), key=lambda kv: calc_classname(kv[1])
    ):
        # Work out sub-tables first

        if classentry.classdependencytuples:
            t2 = BeautifulTable()
            t2.set_style(BeautifulTable.STYLE_BOX)  # nice ─── chars
            for _from,_to in classentry.classdependencytuples:
                t2.rows.append([_from,_to])
        else:
            t2 = ""

        if classentry.attrs:
            t3 = BeautifulTable()
            t3.set_style(BeautifulTable.STYLE_BOX_DOUBLED)  # nice ─── chars
            t3.columns.header = ["name", "type"]
            t3.columns.alignment["name"] = BeautifulTable.ALIGN_LEFT
            for attrobj in classentry.attrs:
                t3.rows.append([attrobj.attrname, "\n".join(attrobj.attrtype)])
        else:
            t3 = ""

        # t4 = BeautifulTable()
        # t4.columns.header = ["of class", "of module"]
        # t4.columns.alignment["of class"] = BeautifulTable.ALIGN_LEFT
        # t4.columns.alignment["of module"] = BeautifulTable.ALIGN_LEFT
        # t4.rows.append(["\n".join(classentry.defs), "\n".join(pmodel.modulemethods)])

        t.rows.append(
            [
            calc_classname(classentry),
            "\n".join(classentry.classesinheritsfrom),
            t3,
            "\n".join(classentry.defs),
            "\n".join(pmodel.modulemethods) if not have_display_module_methods_once else "",
            bool(classentry.ismodulenotrealclass),
            t2,  #classentry.classdependencytuples,
            ])
        have_display_module_methods_once = True

    # No classes but there are module methods yet to display
    if pmodel.modulemethods and not have_display_module_methods_once:
        t.rows.append(
            [
            "",
            "",
            "",
            "",
            "\n".join(pmodel.modulemethods),
            "",
            "",
            ])

    t.columns.alignment[0] = BeautifulTable.ALIGN_LEFT
    return t


# Old (non table) dump

def dump_old_structure(pmodel):
    res = ""

    repair_old_pmodels(pmodel)

    for classname, classentry in sorted(
        list(pmodel.classlist.items()), key=lambda kv: calc_classname(kv[1])
    ):
        res += "%s (is module=%s) inherits from %s class dependencies %s\n" % (
            calc_classname(classentry),
            classentry.ismodulenotrealclass,
            classentry.classesinheritsfrom,
            classentry.classdependencytuples,
        )

        if classentry.classdependencytuples:
            for tup in classentry.classdependencytuples:
                res += "%s\n" % (tup,)

        for attrobj in classentry.attrs:
            res += "    %-20s (attrtype %s)\n" % (
                attrobj.attrname,
                attrobj.attrtype,
            )  # currently skip calc of self._GetCompositeCreatedClassesFor(attrobj.attrname), arguably it should be precalculated and part of the data structure
        for adef in classentry.defs:
            res += "    %s()\n" % adef
    res += "    modulemethods %s\n" % (pmodel.modulemethods)
    return res


# New dump all methods, as per request https://github.com/abulka/pynsource/issues/66 

def dump_pmodel_methods(pmodel):
    """
    Generate text file with all class, methods, functions signatures.
    myModule1.myClass2.mymethod(arg1, ...)
    myModule2.myClass3.mymethod(arg1, ...)
    """
    res = ""

    repair_old_pmodels(pmodel)

    module_name = os.path.basename(pmodel.filename).replace(".py", "")

    filename_msg = f"File: {pmodel.filename}"  # name of file
    res += f"{filename_msg}\n{'-'*len(filename_msg)}\n"  # underline

    # module methods (not in a class)
    was_content = False
    for adef in pmodel.modulemethods:
        res += f"{module_name}.{adef}()\n"
        was_content = True
    if was_content:
        res += "\n"

    # methods in each class
    for classname, classentry in sorted(
        list(pmodel.classlist.items()), key=lambda kv: calc_classname(kv[1])
    ):
        was_content = False
        for adef in classentry.defs:
            res += f"{module_name}.{calc_classname(classentry)}.{adef}()\n"
            was_content = True
        if was_content:
            res += "\n"

    return res
