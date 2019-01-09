"""
@startuml

package "parsing.core_parser_old.py" {

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

    class HandleClasses {
        self.classlist = {}
        self.modulemethods = []
    }

    class PynsourcePythonParser {
        pmodel
        _extract_pmodel()
    }

note as N3
<b><color:royalBlue>Note</color>
This is the old python parser based
on increased levels of parsing functionality
in a huge inheritance chain.  The result
of which is in <u>classlist</u> and <u>modulemethods</u>
which can be extracted and externalised
via the <u>pmodel</u> property.

<b>How to use the old parser:</b>
    p = PynsourcePythonParser()
    p.parse(FILE)
    print p.pmodel
end note
N3 .. PynsourcePythonParser

note as N1
<b><color:royalBlue>Note</color>
The <u>old parse model</u> is actually
a couple of attributes on one of the
middle management parsing classes in the
AndyBasicParseEngine...PynsourcePythonParser chain
and is not 'externalised' until the PynsourcePythonParser
level where a <b>pmodel</b> property is offered.
end note
N1 .. HandleClasses

}

package "parsing.core_parser_ast" {
    class "core_parser_ast" <<MODULE>> {
        parse (filename)
        _ast_parse (filename)
        _convert_ast_to_old_parser()
    }

    package ast  #0DCDFD  {
    }
    note bottom of ast: Standard Python AST parser library
}

package "parsing.api" {
    class "api" <<MODULE>> {
        old_parser (filename, options)
        new_parser (filename, options)
    }
}

package "gen_base" #DDDDDD {
    HandleClasses <|-- PynsourcePythonParser
    AndyBasicParseEngine <|- HandleClasses

    class CmdLineGenerator {
        directories
        optionModuleAsClass
        outpath
        verbose
        --
        ExportTo
        _Process
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
}



package gen_java {
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
        _CreateLanguageGenerator
    }

    ReportGenerator <|- PySourceAsJava
    CmdLineGenerator <|- CmdLinePythonToJava
    CmdLinePythonToJava -> PySourceAsJava : p

}

package "gen_yuml" {

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
        _CreateLanguageGenerator
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

api --> PynsourcePythonParser : old_parser
api --> core_parser_ast : new_parser
core_parser_ast --> ast
ReportGenerator --> api


note "Represents a line of yUML which is one class (Klass) or two classes in a relationship" as N2
Yuml .. N2


note as N4
<b>How to use the myriad report generators</b>
    p = PySourceAsText()
    p.parse(FILE)
    print p  # invokes the report printer
    print p.pmodel  # print just the parse model

If you want to 'pretty print' the old parse model
    print(dump_old_structure(p.pmodel))
end note
N4 .. ReportGenerator

@enduml


"""
