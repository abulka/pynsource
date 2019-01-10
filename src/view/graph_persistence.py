"""
Persistence

To upgrade the file format, add the latest version number n to the
PERSISTENCE_UPGRADE_SEQUENCE list and rewrite Load() and Save() to handle the
latest file format only. And then make an entry in PersistenceConvert() to
handle the n-1 to n conversion (just the one step from the previous version to
this new version n)
"""

PERSISTENCE_UPGRADE_SEQUENCE = [0.9, 1.0, 1.1, 1.2]
PERSISTENCE_CURRENT_VERSION = PERSISTENCE_UPGRADE_SEQUENCE[-1]


class GraphPersistence:
    def __init__(self, graph):
        self.graph = graph

    def RemoveDuplicatesButPreserveLineOrder(self, s):
        """
        Returns a list
        
        Adapted from http://stackoverflow.com/questions/1215208/how-might-i-remove-duplicate-lines-from-a-file
        """
        lines_seen = set()  # holds lines already seen
        result = []
        for line in s.strip().split("\n"):
            if line not in lines_seen:  # not a duplicate
                result.append(line)
                lines_seen.add(line)
            else:
                # print "DUPLICATE in incoming file detected, skipped", line  # DUPLICATE DETECTION
                pass
        # print "******\n", '\n'.join(result)  # debug point - print exact replica of s but without duplicates
        return result

    def can_I_read(self, filedata_str):
        self.prepare(filedata_str)

        if self.ori_file_version == None:
            return False, "Empty or corrupt file"

        if self.ori_file_version > PERSISTENCE_CURRENT_VERSION:
            msg = (
                "Cannot read newer pyNsource file format %1.1f - I only understand up to version %1.1f.  Please upgrade PyNSource and retry loading this file."
                % (self.ori_file_version, PERSISTENCE_CURRENT_VERSION)
            )
            return False, msg
        else:
            return True, "ok"

    def prepare(self, filedata_str):
        self.filedata_list = self.RemoveDuplicatesButPreserveLineOrder(filedata_str)

        if len(self.filedata_list) == 0 or len(filedata_str.strip()) == 0:
            self.ori_file_version = None
            return

        version_data_line = self.filedata_list[0]
        # print "version_data_line", version_data_line

        if len(version_data_line) >= len("# PynSource Version n.n") and version_data_line[0] == "#":
            version_info = version_data_line.split(" ")
            if version_info[0] != "#":
                return False  # unexpected stuff in file
            if version_info[1] != "PynSource":
                return False  # unexpected stuff in file
            if version_info[2] != "Version":
                return False  # unexpected stuff in file
            self.ori_file_version = float(version_info[3])
        else:
            self.ori_file_version = 0.9

    def UpgradeToLatestFileFormatVersion(self, filedata_str):
        """
        Expecting the first line to say something like:
        # PynSource Version 1.1
        Returns T/F as to whether can read and understand the incoming format.
        """
        # print "PERSISTENCE_CURRENT_VERSION", PERSISTENCE_CURRENT_VERSION

        self.prepare(filedata_str)

        if self.ori_file_version == None or self.ori_file_version > PERSISTENCE_CURRENT_VERSION:
            # Cannot read a future version of the file format
            return False

        elif self.ori_file_version == PERSISTENCE_CURRENT_VERSION:
            return True  # nothing to do

        elif self.ori_file_version < PERSISTENCE_CURRENT_VERSION:

            from_index = PERSISTENCE_UPGRADE_SEQUENCE.index(self.ori_file_version)
            to_index = PERSISTENCE_UPGRADE_SEQUENCE.index(PERSISTENCE_CURRENT_VERSION) + 1

            upgrade_sequence = PERSISTENCE_UPGRADE_SEQUENCE[from_index + 1 : to_index]
            for v in upgrade_sequence:
                assert self.ori_file_version < v, "Can't upgrade backwards"
                self.PersistenceConvert(to_vers=v)
            return True

    def PersistenceConvert(self, to_vers):
        if to_vers == 1.0:
            """
            Upgrade just involves adding the version string header
            """
            self.filedata_list.insert(0, "# PynSource Version 1.0")

        elif to_vers == 1.1:
            """
            Upgrade just involves adding a metadata line
            and changing all references to 'node' to 'umlshape'
            """
            self.filedata_list[0] = "# PynSource Version 1.1"
            self.filedata_list.insert(
                1,
                "{'type':'meta', 'info1':'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'}",
            )
            import re

            for i in range(2, len(self.filedata_list)):
                self.filedata_list[i] = re.sub("'node'", "'umlshape'", self.filedata_list[i])
        elif to_vers == 1.2:
            """
            No changes, just new comment shapes added, but these are currently still
            'umlshape' objects with different attributes - a bit dodgy TODO revise this approach
            """
        else:
            print("Don't know how to upgrade persistence format to %f" % to_vers)

    def Load(self, filedata_str, force=False):
        """
        Returns T/F as to whether can read and understand the incoming format.

        This code is now for reading version 1.1 persistence format.
        """
        # load from persistence
        # nodes look like:     {'type':'umlshape', 'id':'c5', 'x':230, 'y':174, 'width':60, 'height':120}
        # edges look like:     {'type':'edge', 'id':'c_to_c1', 'source':'c', 'target':'c1', 'weight':1}  weight >= 1

        if not self.UpgradeToLatestFileFormatVersion(filedata_str) and force == False:
            return False

        for data in self.filedata_list:
            data = data.strip()
            if not data:
                continue
            if data[0] == "#":
                continue
            # print data
            data = eval(data)
            if data["type"] == "meta":
                pass
            if data["type"] == "umlshape":
                if "comment" in data:
                    print("comment detected!!!!!!!")
                    node = self.graph.create_new_comment(
                        data["id"], data["x"], data["y"], data["width"], data["height"]
                    )
                else:
                    node = self.graph.create_new_node(
                        data["id"], data["x"], data["y"], data["width"], data["height"]
                    )
                self.graph.AddNode(node)
                self.graph.node_from_persistence_str(node, data)
            elif data["type"] == "edge":
                source_id = data["source"]
                target_id = data["target"]
                sourcenode = self.graph.FindNodeById(source_id)
                targetnode = self.graph.FindNodeById(target_id)
                if not sourcenode:
                    print("Couldn't load source from persistence", source_id)
                    continue
                if not targetnode:
                    print("Couldn't load target from persistence", target_id)
                    continue
                weight = data.get("weight", None)
                edge = self.graph.AddEdge(
                    sourcenode, targetnode, weight
                )  # AddEdge takes node objects as parameters
                self.graph.edge_from_persistence_str(
                    edge, data
                )  # e.g. UmlGraph class would add edge['uml_edge_type'] if it exists in data

                # At this point we may have created a duplicate entry, we don't know for sure till after the UmlGraph does it's bit. So hard to detect.
                # Enable the following asserts if you suspect anything.  Bit expensive to have these on all the time.
                #
                # assert len(set(self.nodes)) == len(self.nodes), [node.id for node in self.nodes] # ensure no duplicates nodes have been created
                # assert len(set([str(e) for e in self.edges])) == len(self.edges), data # ensure no duplicates edges have been created

        return True

    def Save(self):
        """
        This code is now for saving version 1.1 persistence format.
        """
        nodes = ""
        edges = ""

        if len(self.graph.nodes):
            nodes += "# PynSource Version %1.1f\n" % PERSISTENCE_CURRENT_VERSION
            nodes += "{'type':'meta', 'info1':'Lorem ipsum dolor sit amet, consectetur adipiscing elit is latin. Comments are saved.'}\n"

        for node in self.graph.nodes:
            subclass_persistence_str = self.graph.node_to_persistence_str(node)
            str = "{'type':'umlshape', 'id':'%s', 'x':%d, 'y':%d, 'width':%d, 'height':%d%s}\n" % (
                node.id,
                node.left,
                node.top,
                node.width,
                node.height,
                subclass_persistence_str,
            )
            nodes += str
        for edge in self.graph.edges:
            source = edge["source"].id
            target = edge["target"].id
            subclass_persistence_str = self.graph.edge_to_persistence_str(edge)
            str = "{'type':'edge', 'id':'%s_to_%s', 'source':'%s', 'target':'%s'%s}\n" % (
                source,
                target,
                source,
                target,
                subclass_persistence_str,
            )
            edges += str
        return nodes + edges
