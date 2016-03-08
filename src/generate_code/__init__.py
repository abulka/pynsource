"""
@startuml

package "parsing/core_parser.py" {

    class AndyBasicParseEngine {
        meat
        tokens
        isfreshline
        indentlevel
        -----
        _ReadAllTokensFromFile(self, file):
        _ParseLoop()
        Parse(self, file):
    }

}

package "gen_base.py" #DDDDDD {
    AndyBasicParseEngine <|-- PynsourcePythonParser
    PynsourcePythonParser <|-- ReportGenerator

    class CmdLineGenerator {
        directories
        optionModuleAsClass
        outpath
        verbose
        --
        ExportTo
        _Process
    }

}

class ReportGenerator {
    aclass
    classentry
    embedcompositeswithattributelist
    listcompositesatend
    manymessage
    result
    staticmessage
    verbose
    --
    GetCompositeClassesForAttr
    _GetCompositeCreatedClassesFor
    _DumpAttributes
    _DumpClassHeader
    _DumpModuleMethods
    GenReportDump
    __str__
}



package gen_java.py {
    class PySourceAsJava {
        fp
        outdir
        result
        --
        _DumpClassFooter
        _DumpModuleMethods
        _OpenNextFile
        _NiceNameToPreventCompilerErrors
        _DumpAttribute
        _DumpCompositeExtraFooter
        _DumpClassNameAndGeneralisations
        _DumpMethods
        _Line
    }

    class CmdLinePythonToJava {
        p
        --
        _GenerateAuxilliaryClasses
        GenerateSourceFileForAuxClass
        _CreateParser
    }

    ReportGenerator <|- PySourceAsJava
    CmdLineGenerator <|- CmdLinePythonToJava
    CmdLinePythonToJava -> PySourceAsJava : p

}

package "gen_yuml.py" {

    class Klass {
        name
        attrs
        defs
        -
        connectorstyle
        -
        connectsto
        parent
        --
        MoveAttrsDefsInto
        IsRich
    }

    class Yuml {
        klass
        lhs
        rhs
        --
        _getrhs
        _getlhs
        --
        OneClassAlone
        __str__
    }

    class PySourceAsYuml {
        yumls : []
        enriched_yuml_classes : []
        result
        --
        +CalcYumls
        AddYuml
        FindRichYumlClass
        HasBeenEnriched
        MarkAsEnriched
        Enrich
        CompactYumls
        OptimiseAndEnrichYumls
        YumlDump
        GenReportDump
    }

    class CmdLinePythonToYuml {
        p
        --
        _GenerateAuxilliaryClasses
        _CreateParser
        _Process
        ExportTo
    }

    ReportGenerator <|- PySourceAsYuml
    CmdLineGenerator <|- CmdLinePythonToYuml
    Yuml -> Klass : self.klass
    Yuml -> Klass : self.rhs
    Yuml -> Klass : self.lhs
    Klass -> Klass : parent
    Klass -> Klass : connectsto
    PySourceAsYuml *--> "*" Yuml : yumls
    PySourceAsYuml *--> "*" Yuml : enriched_yuml_classes
    CmdLinePythonToYuml -> PySourceAsYuml : p
}

note "Represents a line of yUML which is one class (Klass) or two classes in a relationship" as N2
Yuml .. N2

note as N1
<b><color:royalBlue>TODO</color>
Need to <u>clarify</u> the parser representation
in the base class
end note

@enduml


"""