class AsciiWorkspace:
    def __init__(self, margin=3):
        self.contents = ""
        self.margin = margin
        self._Init()
        
    def _Init(self):
        self.curr = []
        self.curr_height = 0
        self.curr_width = 0
        
    def _CalcMargin(self):
        if not self.curr:
            return 0
        else:
            return self.margin

    def _ExpandAndPad(self, height, maxwidth):
        height_difference = height - self.curr_height
        if height_difference > 0:
            for row in range(height_difference):
                self.curr.append(" "*self.curr_width)
            self.curr_height = height

    # Public Methods
    
    def Flush(self):
        self.contents += "\n".join(self.curr) + "\n"
        self._Init()

    def AddColumn(self, str):
        lines = str.split("\n")
        
        maxwidth = max([len(line) for line in lines])
        height = len(lines)

        margin = self._CalcMargin()

        self._ExpandAndPad(height, maxwidth)
                
        for row in range(height):
            self.curr[row] += "%s%-*s" % (margin*" ", maxwidth, lines[row])
        
        self.curr_width += maxwidth

    @property
    def Contents(self):
        return self.contents
            
    
if __name__ == '__main__':
    w = AsciiWorkspace()
    
    s = ""
    s += "hi there\n"
    s += "this is a fantastic test"
    
    w.AddColumn(s)
    
    s = ""
    s += "this is some more info\n"
    s += "which is in column 2\n"
    s += "and adds an extra line"
    
    w.AddColumn(s)

    s = "\n"
    s += "this is the third set of info\n"
    s += "which is back in column 1 again"

    w.Flush()
    w.AddColumn(s)

    w.Flush()
    print w.Contents
    
    print "done"
    