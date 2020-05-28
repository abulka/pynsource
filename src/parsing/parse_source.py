import tempfile
from parsing.api import old_parser, new_parser

def parse_source(source_code, options):
    with tempfile.NamedTemporaryFile(mode="wt") as temp:  # TODO use streams not temporary files
        temp.write(source_code)
        temp.flush()
        pmodel, debuginfo = new_parser(temp.name, options=options)
    return pmodel, debuginfo
