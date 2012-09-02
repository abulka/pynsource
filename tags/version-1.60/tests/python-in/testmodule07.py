class ParseMeTest(undo.UndoItem):

    DEFAULT_ELEVATION = 30

    def __init__(self, map):
        self.map = map

    def PlaceTile(self, coord, terrainbmp):
        self.EnsureGraphicsSubDictAllocated(coord)
        newterraintype = self.bmpUtils.BmpToTerrainType(terrainbmp)

