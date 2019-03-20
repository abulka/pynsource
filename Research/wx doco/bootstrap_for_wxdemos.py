# -------- ANDY REPLACEMENT BOOTSTRAP FOR WX PYTHON DEMOS
#
# Just paste this after the demo code obtained from a wxpython demo source.
# Ensure you call the runTest() method which is supplied by each demo.
#
# And remove the existing:
#
# if __name__ == '__main__':
#     import sys,os
#     import run
#     run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
#
# from the demo.



class Log:
    def WriteText(self, text):
        if text[-1:] == "\n":
            text = text[:-1]
        wx.LogMessage(text)

    write = WriteText


class MainApp(wx.App):
    def OnInit(self):
        self.log = Log()

        self.frame = wx.Frame(
            None,
            -1,
            "test",
            pos=(350, 350),
            size=(640, 340),
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.DEFAULT_FRAME_STYLE,
        )
        self.frame.CreateStatusBar()

        self.demowin = runTest(self.frame, self.frame, self.log)
        self.demowin.frame = self.frame
        self.frame.Show(True)
        return True


def main():
    application = MainApp(0)
    application.MainLoop()


if __name__ == "__main__":
    main()


# ------------------------------------------------------------------------
#
# another version which adds a chunk of extra functionality in a more modular way
#
# ------------------------------------------------------------------------


class Log:
    def WriteText(self, text):
        if text[-1:] == "\n":
            text = text[:-1]
        wx.LogMessage(text)

    write = WriteText


class MainApp(wx.App):
    def OnInit(self):
        self.log = Log()

        self.frame = wx.Frame(
            None,
            -1,
            "hit m repeadedly to move shapes",
            pos=(350, 350),
            size=(640, 340),
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.DEFAULT_FRAME_STYLE,
        )
        self.frame.CreateStatusBar()

        self.demowin = runTest(self.frame, self.frame, self.log)
        self.demowin.frame = self.frame
        self.frame.Show(True)

        wx.CallAfter(self.BootStrap)  # OPTIONAL
        return True

        # Extra Injection of functionality - OPTIONAL

    def BootStrap(self):
        self.demowin.Bind(wx.EVT_CHAR, self.onKeyChar)
        self.working = False

    def onKeyChar(self, event):
        if event.GetKeyCode() >= 256:
            event.Skip()
            return
        if self.working:
            event.Skip()
            return
        self.working = True

        from ogl_redraw_f_logic import process_key

        canvas = self.demowin
        keycode = chr(event.GetKeyCode())

        process_key(keycode, self.frame, canvas, canvas.shapes)  # canvas.shapes built by the demo

        self.working = False
        event.Skip()

        # END OPTIONAL


def main():
    application = MainApp(0)
    application.MainLoop()


if __name__ == "__main__":
    main()


# -------------------------------------------------------------------
