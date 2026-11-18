"""Choose which PlantUML server renders the diagram.

The chosen url is stored in the config as PlantUmlServerUrl (empty string means
the official public server) and the HiDPI scale as PlantUmlScale.
"""

import threading

import wx

# (label, url) - "" is the official public server, None is the custom entry
KNOWN_SERVERS = (
    ("PlantUML official server (www.plantuml.com)", ""),
    ("atug (plantuml.atug.com)", "https://plantuml.atug.com/uml"),
    ("dokku (plantuml-server.dokku.andytaichi.com)", "https://plantuml-server.dokku.andytaichi.com/uml"),
    ("Custom...", None),
)
CUSTOM_INDEX = len(KNOWN_SERVERS) - 1


class DialogPlantUmlServer(wx.Dialog):
    def __init__(self, parent, current_url="", current_scale=2):
        wx.Dialog.__init__(
            self, parent, id=wx.ID_ANY, title="PlantUML Server",
            pos=wx.DefaultPosition, size=wx.Size(520, 260),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.current_url = (current_url or "").strip()

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.choice = wx.Choice(self, choices=[label for label, _ in KNOWN_SERVERS])
        sizer.Add(self.choice, 0, wx.EXPAND | wx.ALL, 8)

        url_row = wx.BoxSizer(wx.HORIZONTAL)
        url_row.Add(wx.StaticText(self, label="Server url:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.txt_url = wx.TextCtrl(self)
        url_row.Add(self.txt_url, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(url_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        scale_row = wx.BoxSizer(wx.HORIZONTAL)
        scale_row.Add(wx.StaticText(self, label="Render scale (2 = crisp on Retina):"), 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.spin_scale = wx.SpinCtrl(self, min=1, max=4, initial=max(1, min(4, int(current_scale or 2))))
        scale_row.Add(self.spin_scale, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(scale_row, 0, wx.EXPAND | wx.ALL, 8)

        test_row = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_test = wx.Button(self, label="Test")
        self.lbl_test = wx.StaticText(self, label="")
        test_row.Add(self.btn_test, 0, wx.RIGHT, 8)
        test_row.Add(self.lbl_test, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(test_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        note = wx.StaticText(
            self,
            label="Note: the official server sometimes returns a diagram with no text, and "
                  "crops diagrams wider than 4096 px. Use your own server for reliability.",
        )
        note.Wrap(490)
        sizer.Add(note, 0, wx.ALL, 8)

        sizer.Add(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALIGN_CENTER | wx.ALL, 8)

        self.SetSizer(sizer)
        self.Layout()
        self.Centre(wx.BOTH)

        self._select_current()
        self.choice.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.txt_url.Bind(wx.EVT_TEXT, self.OnUrlEdited)
        self.btn_test.Bind(wx.EVT_BUTTON, self.OnTest)

    # ---------------------------------------------------------------- helpers

    def _select_current(self):
        index = 0
        for i, (_, url) in enumerate(KNOWN_SERVERS):
            if url is not None and url == self.current_url:
                index = i
                break
        else:
            if self.current_url:
                index = CUSTOM_INDEX
        self.choice.SetSelection(index)
        if index == CUSTOM_INDEX:
            self.txt_url.SetValue(self.current_url)
        else:
            self.txt_url.SetValue(KNOWN_SERVERS[index][1])
        self.txt_url.Enable(index == CUSTOM_INDEX)

    def _chosen_url(self):
        index = self.choice.GetSelection()
        if index == CUSTOM_INDEX:
            return self.txt_url.GetValue().strip()
        return KNOWN_SERVERS[max(0, index)][1]

    # ---------------------------------------------------------------- events

    def OnChoice(self, event):
        index = self.choice.GetSelection()
        if index == CUSTOM_INDEX:
            self.txt_url.SetValue(self.current_url)
            self.txt_url.Enable(True)
            self.txt_url.SetFocus()
        else:
            self.txt_url.SetValue(KNOWN_SERVERS[index][1])
            self.txt_url.Enable(False)
        self.lbl_test.SetLabel("")

    def OnUrlEdited(self, event):
        self.lbl_test.SetLabel("")

    def OnTest(self, event):
        from generate_code.gen_plantuml import plant_uml_probe_server

        url = self._chosen_url()
        self.lbl_test.SetLabel("Testing...")
        self.btn_test.Disable()
        self.Layout()

        def worker():
            try:
                ok, message = plant_uml_probe_server(url or None)
            except Exception as e:  # never let a probe exception escape the thread
                ok, message = False, f"Test failed: {e}"

            def report():
                self.lbl_test.SetLabel(message)
                self.lbl_test.SetForegroundColour(
                    wx.Colour(0, 128, 0) if ok else wx.Colour(180, 0, 0))
                self.btn_test.Enable(True)
                self.Layout()

            wx.CallAfter(report)

        threading.Thread(target=worker, daemon=True).start()

    # ---------------------------------------------------------------- results

    def GetServerUrl(self):
        return self._chosen_url()

    def GetScale(self):
        return self.spin_scale.GetValue()
