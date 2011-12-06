class AsciiWorkspace:
    def __init__(self, margin=3):
        self.contents = ""
        self.margin = margin
        self.Init()
        
    def ResetColumns(self):
        self.contents += "\n".join(self.curr) + "\n"
        self.Init()

    def Init(self):
        self.curr = []
        self.curr_height = 0
        self.curr_width = 0
        
    def AddColumn(self, str):
        lines = str.split("\n")
        
        maxwidth = max([len(line) for line in lines])
        height = len(lines)
        
        if not self.curr:
            margin = 0
        else:
            margin = self.margin

        height_difference = height - self.curr_height
        #print "height_difference", height_difference
        if height_difference > 0:
            # Need to expand num entries in curr and pad accordingly
            for row in range(height_difference):
                #print row
                self.curr.append(" "*self.curr_width)
            self.curr_height = height
                
        for row in range(height):
            self.curr[row] += "%s%-*s" % (margin*" ", maxwidth, lines[row])
        
        self.curr_width += maxwidth

        
        #if not self.curr:
        #    margin = 0
        #    for row in range(height):
        #        self.curr.append("")
        #else:
        #    margin = self.margin
        #        
        #for row in range(height-1):
        #    self.curr[row] += "%s%-*s" % (margin*" ", maxwidth, lines[row])
            
    
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

    w.ResetColumns()
    w.AddColumn(s)

    w.ResetColumns()
    print w.contents
    
    print "done"
    