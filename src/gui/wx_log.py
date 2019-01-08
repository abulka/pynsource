import wx


class Log:
    def WriteText(self, text):
        if text[-1:] == "\n":
            text = text[:-1]
        wx.LogMessage(text)

    write = WriteText
