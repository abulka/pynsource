import os
import tempfile
from parsing.api import old_parser, new_parser
from generate_code.gen_plantuml import PySourceAsPlantUml
from common.logwriter import LogWriter
from parsing.core_parser_ast import set_DEBUGINFO, DEBUGINFO

"""
Useful functions to parse Python source code as strings.
"""


def parse_source(source_code, options, html_debug_root_name=""):
    old_debug_info_value = DEBUGINFO()

    # Re temporary files, win10 needs delete=False otherwise other routines cannot access.
    # Need to pass "wt" since we're writing text, not bytes - helps python3 compatibility.
    with tempfile.NamedTemporaryFile(mode="wt", delete=False) as temp:  # TODO use streams not temporary files
        temp.write(source_code)
        temp.flush()

        if html_debug_root_name:
            # Normally debug info is false for performance reasons, so turn it on temporarily and restore it later
            set_DEBUGINFO(True)

            # create a html log file to contain html info 
            log = LogWriter(html_debug_root_name, print_to_console=False)
            log.out_html_header()
        else:
            log = None

        try:
            pmodel, debuginfo = new_parser(temp.name, log=log, options=options)
        finally:
            set_DEBUGINFO(old_debug_info_value)

        if html_debug_root_name:
            log.ensure_is_open()  # file is sometimes closed, so reopen it
            log.out("<hr><h1>Errors:</h1>")
            log.out_wrap_in_html(pmodel.errors)
            log.out("<hr><h1>debuginfo:</h1>")
            log.out(debuginfo)
            log.out_html_footer()
            log.finish()
            print(f"\nHTML LOG parsing debug info is in {os.path.abspath(log.out_filename)}")

    return pmodel, debuginfo

def parse_source_gen_plantuml(source_code, optimise=False):
    # Re temporary files, win10 needs delete=False otherwise other routines cannot access.
    # Need to pass "wt" since we're writing text, not bytes - helps python3 compatibility.
    with tempfile.NamedTemporaryFile(mode="wt", delete=False) as temp:  # TODO use streams not temporary files
        temp.write(source_code)
        temp.flush()
        p = PySourceAsPlantUml()
        p.Parse(temp.name)  # this uses 'new_parser' too
        pmodel = p.pmodel
        plantuml = p.calc_plant_uml(optimise=optimise)
    return pmodel, plantuml
