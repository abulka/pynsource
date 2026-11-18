"""A lightweight, scrollable view for ASCII UML output.

A native wx.TextCtrl is a poor fit for the generated ASCII art on macOS:
``ScrollLines()`` is a no-op there, and sizing one control to the full document
makes wheel scrolling expensive.  This view draws only the visible lines, so
pixel scrolling and font zoom stay cheap.
"""

import wx


class AsciiView(wx.ScrolledWindow):
    """Read-only monospace text with selection, copy and pixel scrolling."""

    MARGIN = 6

    def __init__(self, parent, font=None):
        style = wx.HSCROLL | wx.VSCROLL | wx.BORDER_NONE
        super().__init__(parent, style=style)
        self.SetScrollRate(1, 1)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetCursor(wx.Cursor(wx.CURSOR_IBEAM))

        self._text = ""
        self._lines = [""]
        self._font = font or wx.Font(
            10, wx.MODERN, wx.NORMAL, wx.NORMAL, False
        )
        self._char_width = 8
        self._line_height = 16
        self._selection_anchor = None
        self._selection_current = None
        self._selecting = False
        super().SetFont(self._font)
        self._measure_font()

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_RIGHT_UP, self._on_right_up)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)

    # -- text API used by the rest of the application ---------------------

    def SetValue(self, text):
        text = str(text).replace("\r\n", "\n").replace("\r", "\n")
        self._text = text.expandtabs(4)
        self._lines = self._text.split("\n") or [""]
        self._selection_anchor = None
        self._selection_current = None
        self._update_virtual_size()
        self.Scroll(0, 0)
        self.Refresh()

    def GetValue(self):
        return self._text

    def ShowPosition(self, position):
        if position <= 0:
            self.Scroll(0, 0)

    def SetInsertionPoint(self, position):
        # Kept for call-site compatibility; this view has no editable caret.
        if position <= 0:
            self.Scroll(0, 0)

    def SetFont(self, font):
        self._font = font
        super().SetFont(font)
        self._measure_font()
        self._update_virtual_size()
        self.Refresh()

    def GetFont(self):
        return self._font

    def select_all(self):
        if self._lines:
            self._selection_anchor = (0, 0)
            self._selection_current = (len(self._lines) - 1, len(self._lines[-1]))
            self.Refresh()

    def copy_selection(self):
        text = self._selected_text()
        if text:
            self._set_clipboard(text)

    # -- geometry ---------------------------------------------------------

    def _measure_font(self):
        dc = wx.MemoryDC(wx.Bitmap(1, 1))
        try:
            dc.SetFont(self._font)
            width, height = dc.GetTextExtent("M")
        finally:
            dc.SelectObject(wx.NullBitmap)
        self._char_width = max(1, width)
        self._line_height = max(1, height)

    def _update_virtual_size(self):
        longest = max((len(line) for line in self._lines), default=0)
        width = longest * self._char_width + 2 * self.MARGIN + self._char_width
        height = len(self._lines) * self._line_height + 2 * self.MARGIN
        self.SetVirtualSize((max(1, width), max(1, height)))

    def _visible_rows(self):
        sx, sy = self.GetViewStart()
        first = max(0, (sy - self.MARGIN) // self._line_height)
        client_h = self.GetClientSize().height
        last = min(
            len(self._lines),
            (sy + client_h - self.MARGIN) // self._line_height + 1,
        )
        return int(first), int(last)

    def _pos_from_point(self, x, y):
        sx, sy = self.GetViewStart()
        row = int((y + sy - self.MARGIN) // self._line_height)
        row = max(0, min(len(self._lines) - 1, row))
        col = int((x + sx - self.MARGIN) // self._char_width)
        col = max(0, min(len(self._lines[row]), col))
        return row, col

    # -- selection --------------------------------------------------------

    def _selection_range(self):
        if self._selection_anchor is None or self._selection_current is None:
            return None
        a, b = self._selection_anchor, self._selection_current
        return (a, b) if a <= b else (b, a)

    def _selected_text(self):
        selected = self._selection_range()
        if selected is None:
            return ""
        (r1, c1), (r2, c2) = selected
        if r1 == r2:
            return self._lines[r1][c1:c2]
        parts = [self._lines[r1][c1:]]
        parts.extend(self._lines[r1 + 1 : r2])
        parts.append(self._lines[r2][:c2])
        return "\n".join(parts)

    def _selection_for_row(self, row):
        selected = self._selection_range()
        if selected is None:
            return None
        (r1, c1), (r2, c2) = selected
        if row < r1 or row > r2:
            return None
        start = c1 if row == r1 else 0
        end = c2 if row == r2 else len(self._lines[row])
        if start == end and r1 != r2:
            return None
        return start, end

    @staticmethod
    def _set_clipboard(text):
        if not wx.TheClipboard.Open():
            return
        try:
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
        except Exception:  # noqa: BLE001 - clipboard is best-effort
            wx.TheClipboard.Close()

    # -- events -----------------------------------------------------------

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        self.PrepareDC(dc)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetFont(self._font)

        normal = self.GetForegroundColour()
        highlight = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        highlight_text = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        first, last = self._visible_rows()
        for row in range(first, last):
            line = self._lines[row]
            y = self.MARGIN + row * self._line_height
            selected = self._selection_for_row(row)
            if selected is not None:
                start, end = selected
                x1 = self.MARGIN + start * self._char_width
                x2 = self.MARGIN + end * self._char_width
                dc.SetBrush(wx.Brush(highlight))
                dc.SetPen(wx.Pen(highlight))
                dc.DrawRectangle(x1, y, max(1, x2 - x1), self._line_height)
                dc.SetTextForeground(highlight_text)
                dc.DrawText(line, self.MARGIN, y)
                dc.SetTextForeground(normal)
            else:
                dc.SetTextForeground(normal)
                dc.DrawText(line, self.MARGIN, y)

    def _on_left_down(self, event):
        self.SetFocus()
        self._selection_anchor = self._pos_from_point(event.GetX(), event.GetY())
        self._selection_current = self._selection_anchor
        self._selecting = True
        if not self.HasCapture():
            self.CaptureMouse()
        self.Refresh()
        event.Skip()

    def _on_left_up(self, event):
        self._selecting = False
        if self.HasCapture():
            self.ReleaseMouse()
        event.Skip()

    def _on_motion(self, event):
        if not event.Dragging() or not self._selecting:
            event.Skip()
            return
        self._selection_current = self._pos_from_point(event.GetX(), event.GetY())
        self.Refresh()
        event.Skip()

    def _on_key_down(self, event):
        key = event.GetKeyCode()
        command = event.CmdDown() or event.ControlDown()
        if command and key in (ord("C"), ord("c")):
            self.copy_selection()
            return
        if command and key in (ord("A"), ord("a")):
            self.select_all()
            return
        if key == wx.WXK_ESCAPE:
            self._selection_anchor = None
            self._selection_current = None
            self.Refresh()
            return
        if key in (wx.WXK_PAGEUP, wx.WXK_PAGEDOWN):
            sx, sy = self.GetViewStart()
            page = max(1, self.GetClientSize().height - self._line_height)
            self.Scroll(sx, max(0, sy + (page if key == wx.WXK_PAGEDOWN else -page)))
            return
        if key == wx.WXK_HOME:
            self.Scroll(0, 0)
            return
        if key == wx.WXK_END:
            sx, sy = self.GetViewStart()
            self.Scroll(sx, sy + len(self._lines) * self._line_height)
            return
        event.Skip()

    def _on_right_up(self, event):
        menu = wx.Menu()
        copy_item = menu.Append(wx.ID_COPY, "Copy")
        select_all_item = menu.Append(wx.ID_SELECTALL, "Select All")
        menu.Bind(wx.EVT_MENU, lambda e: self.copy_selection(), copy_item)
        menu.Bind(wx.EVT_MENU, lambda e: self.select_all(), select_all_item)
        try:
            self.PopupMenu(menu)
        finally:
            menu.Destroy()
        event.Skip()


__all__ = ["AsciiView"]
