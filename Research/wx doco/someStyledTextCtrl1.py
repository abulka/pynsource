##  StyledTextCtrl Log Window Demo
#
# Last modified: 23 July 2006
#
# Tested On:
#       Window XP with Python 2.4 and wxPython 2.6.3 (Unicode)
#       Debian GNU/Linux 3.1 (Sarge) with Python 2.3 and wxPython 2.6.3 (Unicode)
#
# The purpose of this program is to illustrate a very simple but useful
# application of a StyledTextCtrl.
#
# The StyledTextCtrl is complicated and some people find it hard to get
# started with it.  This demo, shows that programers can start to reap the
# benefits of using a StyledTextCtrl with very little effort.
#
# Normally a wx.Text control is used for log windows, however, using a
# StyledTextCtrl has the advantage of allowing the user to zoom the text
# in the control using CTRL-+ and CTRL--.  This facility is availiable by
# default, you get if for free!, and you have the option of using coloured
# messages too.
#

import wx
import wx.stc as stc

class Log(stc.StyledTextCtrl):
    """
    Subclass the StyledTextCtrl to provide  additions
    and initializations to make it useful as a log window.

    """
    def __init__(self, parent, style=wx.SIMPLE_BORDER):
        """
        Constructor
        
        """
        stc.StyledTextCtrl.__init__(self, parent, style=style)
        self._styles = [None]*32
        self._free = 1

    def getStyle(self, c='black'):
        """
        Returns a style for a given colour if one exists.  If no style
        exists for the colour, make a new style.
        
        If we run out of styles, (only 32 allowed here) we go to the top
        of the list and reuse previous styles.

        """
        free = self._free
        if c and isinstance(c, (str, unicode)):
            c = c.lower()
        else:
            c = 'black'

        try:
            style = self._styles.index(c)
            return style

        except ValueError:
            style = free
            self._styles[style] = c
            self.StyleSetForeground(style, wx.NamedColour(c))

            free += 1
            if free >31:
                free = 0
            self._free = free
            return style

    def write(self, text, c=None):
        """
        Add the text to the end of the control using colour c which
        should be suitable for feeding directly to wx.NamedColour.
        
        'text' should be a unicode string or contain only ascii data.
        """
        style = self.getStyle(c)
        lenText = len(text.encode('utf8'))
        end = self.GetLength()
        self.AddText(text)
        self.StartStyling(end, 31)
        self.SetStyling(lenText, style)
        self.EnsureCaretVisible()


    __call__ = write


class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        self.colour = 'black'
        log('Welcom to wxPython %s' % wx.VERSION_STRING, 'blue')
        log('Hi there')
        log('Ctrl-+ and Ctrl-- or Ctrl-ScrollWheel', 'blue')
        log(' to zoom text in this window.\n')
        wx.Panel.__init__(self, parent, -1)

        self.SetBackgroundColour('cyan')

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.Bind(wx.EVT_LEFT_DOWN, lambda e:self.OnMouse(e, 'Left'))
        self.Bind(wx.EVT_RIGHT_DOWN, lambda e:self.OnMouse(e, 'Right'))
        self.Bind(wx.EVT_MIDDLE_DOWN, lambda e:self.OnMouse(e, 'Middle'))

        for i in ('red', 'green', 'blue', 'cyan', 'magenta'):
            btn = wx.Button(self, -1, i)
            sizer.Add(btn, 1, wx.TOP|wx.BOTTOM, 15)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)

        self.SetSizer(sizer)

    def OnMouse(self, event, type):
        self.log('\n\n%s Mouse Button Clicked'%type, self.colour)
        event.Skip()

    def OnButton(self, event):
        btn = event.GetEventObject()
        label = btn.GetLabel()
        self.colour = label
        self.log('\n\n%s button clicked'%label, label)
        event.Skip()


class TestFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'StyledTextCtrl Log Panel Demo')

        log = Log(self)
        tp = TestPanel(self, log)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tp, 0, wx.EXPAND)
        sizer.Add(log, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetSize((400, 300))


if __name__=="__main__":
    app = wx.PySimpleApp()
    win = TestFrame()
    win.Show(True)
    app.MainLoop()
    