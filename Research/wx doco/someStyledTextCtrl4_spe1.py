#!usr/bin/python
# -*- coding: utf8 -*-
# (c)www.stani.be, GPL licensed

import sys, random
import wx
import wx.stc as stc

DEFAULT_ENCODING = "utf8"
STC_LANGUAGES = [x[8:] for x in dir(stc) if x.startswith("STC_LEX_")]
WHITE = 6777215
GRAY = 3388607


def value2colour(c):
    return ("#%6s" % hex(c)[2:]).replace(" ", "0").upper()


def picasso():
    c = random.randint(0, GRAY)
    return value2colour(c), value2colour((c + GRAY) % WHITE)


class Node:
    def __init__(self, level, start, end, text, parent=None, styles=[]):
        """Folding node as data for tree item."""
        self.parent = parent
        self.level = level
        self.start = start
        self.end = end
        self.text = text
        self.styles = styles  # can be useful for icon detection
        self.children = []


class Editor(stc.StyledTextCtrl):
    # ---initialize
    def __init__(self, parent, language="UNKNOWN"):
        stc.StyledTextCtrl.__init__(self, parent, -1)
        self.setFoldMargin()
        self.encoding = DEFAULT_ENCODING
        self.AndyExtra()

    def setFoldMargin(self):
        self.SetProperty("fold", "1")
        self.SetProperty("fold.html", "1")
        # MARGINS
        self.SetMargins(0, 0)
        # margin 1 for line numbers
        self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 50)
        # margin 2 for markers
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)
        # Plus for contracted folders, minus for expanded
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_MINUS, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_PLUS, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black")
        self.Bind(stc.EVT_STC_MARGINCLICK, self.onMarginClick)

    def onMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)

    # ---open
    def open(self, fileName, language, encoding=DEFAULT_ENCODING, line=0):
        self.setLanguage(language)
        self.setText(open(fileName).read(), encoding)
        wx.CallAfter(self.GotoLine, line)

    def setText(self, text, encoding=DEFAULT_ENCODING):
        self.encoding = encoding
        self.SetText(text.decode(encoding))
        self.Colourise(0, self.GetTextLength())  # make sure everything is lexed
        wx.CallAfter(self.explorer.update)

    def setLanguage(self, language):
        if language in STC_LANGUAGES:
            self.SetLexer(getattr(stc, "STC_LEX_%s" % language))
            ##for style in range(50):
            ##    self.StyleSetSpec(style,"fore:%s,back:%s"%picasso())
            return True
        return False

    # ---hierarchy
    def getHierarchy(self):
        # [(level,line,text,parent,[children]),]
        n = self.GetLineCount() + 1
        prevNode = root = Node(level=0, start=0, end=n, text="root", parent=None)
        for line in range(n - 1):
            foldBits = self.GetFoldLevel(line)
            if foldBits & stc.STC_FOLDLEVELHEADERFLAG:
                # folding point
                prevLevel = prevNode.level
                level = foldBits & stc.STC_FOLDLEVELNUMBERMASK
                text = self.GetLine(line)
                node = Node(level=level, start=line, end=n, text=text)
                if level == prevLevel:
                    # say hello to new brother or sister
                    node.parent = prevNode.parent
                    node.parent.children.append(node)
                    prevNode.end = line
                elif level > prevLevel:
                    # give birth to child (only one level deep)
                    node.parent = prevNode
                    prevNode.children.append(node)
                else:
                    # find your uncles and aunts (can be several levels up)
                    while level < prevNode.level:
                        prevNode.end = line
                        prevNode = prevNode.parent
                    node.parent = prevNode.parent
                    node.parent.children.append(node)
                    prevNode.end = line
                prevNode = node
        prevNode.end = line
        return root

    def selectNode(self, node):
        print("clciked!!!")
        """If a tree item is right clicked select the corresponding code"""
        self.GotoLine(node.start)
        self.SetSelection(self.PositionFromLine(node.start), self.PositionFromLine(node.end))

    def AndyExtra(self):
        # Line numbers in margin
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, "fore:#000000,back:#99A9C2")
        # Highlighted brace
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT, "fore:#00009D,back:#FFFF00")
        # Unmatched brace
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD, "fore:#00009D,back:#FF0000")
        # Indentation guide
        self.StyleSetSpec(wx.stc.STC_STYLE_INDENTGUIDE, "fore:#CDCDCD")

        # Python styles
        self.StyleSetSpec(wx.stc.STC_P_DEFAULT, "fore:#000000")
        # Comments
        self.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, "fore:#008000,back:#F0FFF0")
        self.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, "fore:#008000,back:#F0FFF0")
        # Numbers
        self.StyleSetSpec(wx.stc.STC_P_NUMBER, "fore:#008080")
        # Strings and characters
        self.StyleSetSpec(wx.stc.STC_P_STRING, "fore:#800080")
        self.StyleSetSpec(wx.stc.STC_P_CHARACTER, "fore:#800080")
        # Keywords
        self.StyleSetSpec(wx.stc.STC_P_WORD, "fore:#000080,bold")
        # Triple quotes
        self.StyleSetSpec(wx.stc.STC_P_TRIPLE, "fore:#800080,back:#FFFFEA")
        self.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, "fore:#800080,back:#FFFFEA")
        # Class names
        self.StyleSetSpec(wx.stc.STC_P_CLASSNAME, "fore:#0000FF,bold")
        # Function names
        self.StyleSetSpec(wx.stc.STC_P_DEFNAME, "fore:#008080,bold")
        # Operators
        self.StyleSetSpec(wx.stc.STC_P_OPERATOR, "fore:#800000,bold")
        # Identifiers. I leave this as not bold because everything seems
        # to be an identifier if it doesn't match the above criterae
        self.StyleSetSpec(wx.stc.STC_P_IDENTIFIER, "fore:#000000")

        # Caret color
        self.SetCaretForeground("BLUE")
        # Selection background
        self.SetSelBackground(1, "#66CCFF")

        self.SetSelBackground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        self.SetSelForeground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))


class TreeCtrl(wx.TreeCtrl):
    def __init__(self, *args, **keyw):
        keyw["style"] = wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS
        wx.TreeCtrl.__init__(self, *args, **keyw)
        self.root = self.AddRoot("foldExplorer root")
        self.hierarchy = None
        self.Bind(wx.EVT_RIGHT_UP, self.onRightUp)
        self.Bind(wx.EVT_TREE_KEY_DOWN, self.update)

    def update(self, event=None):
        """Update tree with the source code of the editor"""
        hierarchy = self.editor.getHierarchy()
        if hierarchy != self.hierarchy:
            self.hierarchy = hierarchy
            self.DeleteChildren(self.root)
            self.appendChildren(self.root, self.hierarchy)

    def appendChildren(self, wxParent, nodeParent):
        for nodeItem in nodeParent.children:
            wxItem = self.AppendItem(wxParent, nodeItem.text.strip())
            self.SetPyData(wxItem, nodeItem)
            self.appendChildren(wxItem, nodeItem)

    def onRightUp(self, event):
        """If a tree item is right clicked select the corresponding code"""
        pt = event.GetPosition()
        wxItem, flags = self.HitTest(pt)
        nodeItem = self.GetPyData(wxItem)
        self.editor.selectNode(nodeItem)


import wx.lib.mixins.inspection


class MyApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.Init()  # initialize the inspection tool
        return True


class Frame(wx.Frame):
    def __init__(self, title, size=(800, 600)):
        wx.Frame.__init__(self, None, -1, title, size=size)
        splitter = wx.SplitterWindow(self)
        self.explorer = TreeCtrl(splitter)
        self.editor = Editor(splitter)
        splitter.SplitVertically(self.explorer, self.editor, int(self.GetClientSize()[1] / 3))
        self.explorer.editor = self.editor
        self.editor.explorer = self.explorer
        self.Show()


if __name__ == "__main__":
    print("This scintilla supports %d languages." % len(STC_LANGUAGES))
    print(", ".join(STC_LANGUAGES))
    # app     = wx.PySimpleApp()
    app = MyApp()
    frame = Frame("Fold Explorer Demo")

    fileName = sys.argv[-1]  # choose file
    frame.editor.open(fileName, "PYTHON", "utf8")  # choose language in caps

    app.MainLoop()
