import tempfile
from parsing.api import old_parser, new_parser
from generate_code.gen_plantuml import PySourceAsPlantUml

"""
Useful functions to parse Python source code as strings.
"""


def parse_source(source_code, options):
    with tempfile.NamedTemporaryFile(mode="wt") as temp:  # TODO use streams not temporary files
        temp.write(source_code)
        temp.flush()
        pmodel, debuginfo = new_parser(temp.name, options=options)
    return pmodel, debuginfo

def parse_source_gen_plantuml(source_code, optimise=False):
    with tempfile.NamedTemporaryFile(mode="wt") as temp:  # TODO use streams not temporary files
        temp.write(source_code)
        temp.flush()
        p = PySourceAsPlantUml()
        p.Parse(temp.name)  # this uses 'new_parser' too
        pmodel = p.pmodel
        plantuml = p.calc_plant_uml(optimise=optimise)
    return pmodel, plantuml
