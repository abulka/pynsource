# styled text using wxPython's
# wx.StyledTextCtrl(parent, id, pos, size, style, name)
# set up for folding and Python code highlighting
# source: Dietrich  16NOV2008

import  wx
import  wx.stc  as  stc
import  keyword

if wx.Platform == '__WXMSW__':
    # for windows OS
    faces = { 
        'times': 'Times New Roman',
        'mono' : 'Courier New',
        # try temporary switch to mono
        'helv' : 'Courier New',
        #'helv' : 'Arial',
        'other': 'Comic Sans MS',
        'size' : 10,
        'size2': 8,
        }
else:
    faces = { 
        'times': 'Times',
        'mono' : 'Courier',
        'helv' : 'Helvetica',
        'other': 'new century schoolbook',
        'size' : 12,
        'size2': 10,
        }


class MySTC(stc.StyledTextCtrl):
    """
    set up for folding and Python code highlighting
    """
    def __init__(self, parent):
        stc.StyledTextCtrl.__init__(self, parent, wx.ID_ANY)

        # use Python code highlighting
        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, " ".join(keyword.kwlist))

        # set other options ...
        self.SetProperty("fold", "1")
        self.SetMargins(0, 0)
        self.SetViewWhiteSpace(False)
        self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(78)
        self.SetCaretForeground("blue")
        
        # setup a margin to hold the fold markers
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)
        
        # fold markers use square headers
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, 
            stc.STC_MARK_BOXMINUS, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER,
            stc.STC_MARK_BOXPLUS, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,
            stc.STC_MARK_VLINE, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,
            stc.STC_MARK_LCORNER, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,
            stc.STC_MARK_BOXPLUSCONNECTED, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID,
            stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL,
            stc.STC_MARK_TCORNER, "white", "#808080")
        
        # bind some events ...
        self.Bind(stc.EVT_STC_UPDATEUI, self.onUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.onMarginClick)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPressed)

        # make some general styles ...
        # global default styles for all languages
        # set default font
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
            "face:%(helv)s,size:%(size)d" % faces)
        # set default background color
        beige = '#F5F5DC'
        self.StyleSetBackground(style=stc.STC_STYLE_DEFAULT,
            back=beige)
        # reset all to be like the default
        self.StyleClearAll()  

        # more global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,
            "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR,
            "face:%(other)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
            "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,
            "fore:#000000,back:#FF0000,bold")

        # make the Python styles ...
        # default 
        self.StyleSetSpec(stc.STC_P_DEFAULT,
            "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # comments
        self.StyleSetSpec(stc.STC_P_COMMENTLINE,
            "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        # number
        self.StyleSetSpec(stc.STC_P_NUMBER,
            "fore:#007F7F,size:%(size)d" % faces)
        # string
        self.StyleSetSpec(stc.STC_P_STRING,
            "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # single quoted string
        self.StyleSetSpec(stc.STC_P_CHARACTER,
            "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # keyword
        self.StyleSetSpec(stc.STC_P_WORD,
            "fore:#00007F,bold,size:%(size)d" % faces)
        # triple quotes
        self.StyleSetSpec(stc.STC_P_TRIPLE,
            "fore:#7F0000,size:%(size)d" % faces)
        # triple double quotes
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE,
            "fore:#7F0000,size:%(size)d" % faces)
        # class name definition
        self.StyleSetSpec(stc.STC_P_CLASSNAME,
            "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        # function or method name definition
        self.StyleSetSpec(stc.STC_P_DEFNAME,
            "fore:#007F7F,bold,size:%(size)d" % faces)
        # operators
        self.StyleSetSpec(stc.STC_P_OPERATOR,
            "bold,size:%(size)d" % faces)
        # identifiers
        self.StyleSetSpec(stc.STC_P_IDENTIFIER,
            "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # comment-blocks
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK,
            "fore:#7F7F7F,size:%(size)d" % faces)
        # end of line where string is not closed
        self.StyleSetSpec(stc.STC_P_STRINGEOL,
            "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d"\
                % faces)
        
        # register some images for use in the AutoComplete box
        self.RegisterImage(1, 
            wx.ArtProvider.GetBitmap(wx.ART_TIP, size=(16,16)))
        self.RegisterImage(2, 
            wx.ArtProvider.GetBitmap(wx.ART_NEW, size=(16,16)))
        self.RegisterImage(3, 
            wx.ArtProvider.GetBitmap(wx.ART_COPY, size=(16,16)))

    def onKeyPressed(self, event):
        if self.CallTipActive():
            self.CallTipCancel()
        key = event.GetKeyCode()
        if key == 32 and event.ControlDown():
            pos = self.GetCurrentPos()
            # tips
            if event.ShiftDown():
                self.CallTipSetBackground("yellow")
                self.CallTipShow(pos, 'show tip stuff') 
            # code completion (needs more work)
            else:
                kw = keyword.kwlist[:]
                # optionally add more ...
                kw.append("__init__?3")
                # Python sorts are case sensitive
                kw.sort()
                # so this needs to match  
                self.AutoCompSetIgnoreCase(False)  
                # registered images are specified with appended "?type"
                for i in range(len(kw)):
                    if kw[i] in keyword.kwlist:
                        kw[i] = kw[i] + "?1"
                self.AutoCompShow(0, " ".join(kw))
        else:
            event.Skip()

    def onUpdateUI(self, evt):
        """update the user interface"""
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)
        # check before
        if charBefore and chr(charBefore) in "[]{}()"\
                and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1
        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()"\
                    and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos
        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)
        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

    def onMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.foldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) &\
                        stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldexpanded(lineClicked, True)
                        self.expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldexpanded(lineClicked):
                            self.SetFoldexpanded(lineClicked, False)
                            self.expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldexpanded(lineClicked, True)
                            self.expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)

    def foldAll(self):
        """folding folds, marker - to +"""
        lineCount = self.GetLineCount()
        expanding = True
        # find out if folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) &\
                    stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldexpanded(lineNum)
                break;
        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & stc.STC_FOLDLEVELHEADERFLAG and \
               (level & stc.STC_FOLDLEVELNUMBERMASK) ==\
                    stc.STC_FOLDLEVELBASE:
                if expanding:
                    self.SetFoldexpanded(lineNum, True)
                    lineNum = self.expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldexpanded(lineNum, False)
                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)
            lineNum = lineNum + 1

    def expand(self, line, doexpand, force=False, visLevels=0, level=-1):
        """expanding folds, marker + to -"""
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doexpand:
                    self.ShowLines(line, line)
            if level == -1:
                level = self.GetFoldLevel(line)
            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldexpanded(line, True)
                    else:
                        self.SetFoldexpanded(line, False)
                    line = self.expand(line, doexpand, force, visLevels-1)
                else:
                    if doexpand and self.GetFoldexpanded(line):
                        line = self.expand(line, True, force, visLevels-1)
                    else:
                        line = self.expand(line, False, force, visLevels-1)
            else:
                line = line + 1;
        return line


class MyFrame(wx.Frame):
    def __init__(self, parent, mytitle, mysize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, mytitle, size=mysize)
        
        stc_edit = MySTC(self)
        
        # open a Python code file you have ...
        py_file = "someStyledTextCtrl3.py"
        stc_edit.SetText(open(py_file).read())
        stc_edit.EmptyUndoBuffer()
        
        # line numbers in the margin
        stc_edit.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        stc_edit.SetMarginWidth(1, 25)


app = wx.App(0)
# create a MyFrame instance and show the frame
mytitle = 'wx.StyledTextCtrl (rightclick for menu)'
MyFrame(None, mytitle, (800, 500)).Show()
app.MainLoop()