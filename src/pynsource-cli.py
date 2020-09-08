import os
import click
import textwrap
from parsing.dump_pmodel import dump_old_structure, dump_pmodel, dump_pmodel_methods
from parsing.api import new_parser
import common.messages
from view.display_model import DisplayModel
import glob
from gui.settings import APP_VERSION, APP_VERSION_FULL

@click.command()
@click.argument('files', nargs=-1)
@click.option('--mode', default=3, help='Python 3 or Python 2 syntax mode')
@click.option('--graph', is_flag=True, default=False, help='Build graph of nodes representing class relationships')
@click.option('--methods-list', is_flag=True, default=False, help='Dump simple list of methods')
@click.option('--prop-decorator', is_flag=True, default=False, help='Treat property decorated methods as attributes, not methods')
@click.option('--version', is_flag=True, default=False, help='Display version number')
def reverse_engineer(files, mode, graph, methods_list, prop_decorator, version):
    """Pynsource CLI - Reverse engineer python source code into UML

    This command line tool doesn't actualy generate diagrams, but it does parse Python code into the 
    underlying 'pmodel' (parse model) that the Pynsource GUI graphic diagrammer uses.  Used for debugging.
    
    Examples of use:

        python3 ./src/pynsource-cli.py a.py b.py

        python3 ./src/pynsource-cli.py --graph src/common/command_pattern.py

        python3 ./src/pynsource-cli.py --methods-list src/common/*.py

    """

    if version:
        click.echo(f"Pynsource CLI version {APP_VERSION_FULL}")

    click.echo(f"Files to parse: {files}")
    # click.echo(graph)

    # Expansion of files seems to happen magically via bash - need to check with windows
    # But if running via pycharm wildcards are not expanded, so play it safe and glob
    globbed = []
    for param in files:
        files = glob.glob(param)
        globbed += files
    click.echo(globbed)

    if graph:
        displaymodel = DisplayModel(canvas=None)

    for f in globbed:
        pmodel, debuginfo = new_parser(f, options={"mode": mode,
                                                   "TREAT_PROPERTY_DECORATOR_AS_PROP": prop_decorator})
        if pmodel.errors:
            print(pmodel.errors)

        if methods_list: # Dump simple list of methods
            click.echo(dump_pmodel_methods(pmodel))

        else:  # Dump table of underlying pmodel
            assert f == pmodel.filename
            click.echo(f"Parse model for '{pmodel.filename}':")
            click.echo(dump_pmodel(pmodel))

            if graph:  # Dump table of display model
                displaymodel.build_graphmodel(pmodel)  # will append

    if graph:
        displaymodel.Dump(msg="Final display model Graph containing all parse models:")

"""
Notes

-1 means an unlimited number of arguments is accepted:
http://click.pocoo.org/6/arguments/#variadic-arguments

The ability of the old parser to treat modules as pseudo classes is ignored,
 since the new parser does not have this mode of operation yet.
@click.option('--psuedo', is_flag=True, help='Treat module files as pseudo classes')

Arguments
type=click.File('r')
type=click.Path(exists=True) but fails with /*.py

"""

if __name__ == '__main__':
    reverse_engineer()