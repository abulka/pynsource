#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode wxPython tutorial

In this example, we create an
about dialog box. 

author: Jan Bodnar
website: www.zetcode.com
last modified: October 2011
"""

import wx


class Example(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)

        self.InitUI()

    def InitUI(self):

        id = wx.NewId()
        menubar = wx.MenuBar()
        help = wx.Menu()
        help.Append(id, "&About")
        self.Bind(wx.EVT_MENU, self.OnAboutBox)  # , help)
        menubar.Append(help, "&Help")
        self.SetMenuBar(menubar)

        self.SetSize((300, 200))
        self.SetTitle("About dialog box")
        self.Centre()
        self.Show(True)

    def OnAboutBox(self, e):

        description = """File Hunter is an advanced file manager for 
the Unix operating system. Features include powerful built-in editor, 
advanced search capabilities, powerful batch renaming, file comparison, 
extensive archive handling and more.
"""

        licence = """File Hunter is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

File Hunter is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""

        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon("Images\\img_uml01.png", wx.BITMAP_TYPE_PNG))
        info.SetName("File Hunter")
        info.SetVersion("1.0")
        info.SetDescription(description)
        info.SetCopyright("(C) 2007 - 2011 Jan Bodnar")
        info.SetWebSite("http://www.zetcode.com")
        info.SetLicence(licence)
        info.AddDeveloper("Jan Bodnar")
        info.AddDocWriter("Jan Bodnar")
        info.AddArtist("The Tango crew")
        info.AddTranslator("Jan Bodnar")

        wx.AboutBox(info)


def main():

    ex = wx.App()
    Example(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
