from .base_cmd import CmdBase
import wx
from beautifultable import BeautifulTable
from termcolor import colored  # also install colorama to make this work on windows
from parsing.dump_pmodel import dump_old_structure, dump_pmodel, dump_pmodel_methods


class CmdDumpDisplayModel(CmdBase):
    def __init__(self, parse_models=False):
        self.parse_models = parse_models

    def execute(self):
        # Also called by Snapshot manager.
        # When create Snapshot manager we pass ourselves as a controller and DumpStatus() is expected to exist.
        import locale

        # http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x
        locale.setlocale(locale.LC_ALL, "")

        if self.parse_models:
            self.dump_parse_models()
        else:
            table = self.context.coordmapper.DumpCalibrationInfo(dump_nodes=False, doprint=False)
            self.dump_overlaps(into_existing_table=table)
            self.context.displaymodel.Dump()

    def dump_parse_models(self):
        for pmodel in self.context.displaymodel.pmodels_i_have_seen:
            print("\nfilename", pmodel.filename)
            # print(dump_old_structure(pmodel))
            print(dump_pmodel(pmodel))

        # Also dump as list of methods
        print("")
        print("Simple List of Methods:")
        print("")
        for pmodel in self.context.displaymodel.pmodels_i_have_seen:
            print(dump_pmodel_methods(pmodel))            

    def dump_overlaps(self, into_existing_table=None):
        if len(into_existing_table.rows) > 0:
            t = into_existing_table
        else:
            t = BeautifulTable()
            t.set_style(BeautifulTable.STYLE_BOX)  # nice ─── chars
        t.rows.append(
            [
                "bounds",
                self.context.displaymodel.graph.GetBounds()[0],
                self.context.displaymodel.graph.GetBounds()[1],
            ]
        )
        t.rows.append(["node-node overlaps", self.context.overlap_remover.CountOverlaps(), ""])
        t.rows.append(
            [
                "line-line intersections, crossings",
                len(self.context.displaymodel.graph.CountLineOverLineIntersections()),
                self.context.displaymodel.graph.CountLineOverNodeCrossings()["ALL"] / 2,
            ]
        )

        t.columns.alignment[0] = BeautifulTable.ALIGN_LEFT
        print(t)
