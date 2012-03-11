import System.Drawing
import System.Windows.Forms

from System.Drawing import *
from System.Windows.Forms import *

class MainForm(Form):
    def __init__(self):
        self.InitializeComponent()
    
    def InitializeComponent(self):
        self._components = System.ComponentModel.Container()
        self._btnDebug1 = System.Windows.Forms.Button()
        self._menuStrip1 = System.Windows.Forms.MenuStrip()
        self._fIleToolStripMenuItem = System.Windows.Forms.ToolStripMenuItem()
        self._newToolStripMenuItem = System.Windows.Forms.ToolStripMenuItem()
        self._statusStrip1 = System.Windows.Forms.StatusStrip()
        self._flowLayoutPanel1 = System.Windows.Forms.FlowLayoutPanel()
        self._button1 = System.Windows.Forms.Button()
        self._button2 = System.Windows.Forms.Button()
        self._button3 = System.Windows.Forms.Button()
        self._textBox1 = System.Windows.Forms.TextBox()
        self._flowLayoutPanel2 = System.Windows.Forms.FlowLayoutPanel()
        self._linkLabel1 = System.Windows.Forms.LinkLabel()
        self._linkLabel2 = System.Windows.Forms.LinkLabel()
        self._linkLabel3 = System.Windows.Forms.LinkLabel()
        self._button4 = System.Windows.Forms.Button()
        self._listBox1 = System.Windows.Forms.ListBox()
        self._button5 = System.Windows.Forms.Button()
        self._inputFieldTxt = System.Windows.Forms.TextBox()
        self._inputFieldTxtZ = System.Windows.Forms.TextBox()
        self._button6 = System.Windows.Forms.Button()
        self._button7 = System.Windows.Forms.Button()
        self._toolTip1 = System.Windows.Forms.ToolTip(self._components)
        self._linkLabel4 = System.Windows.Forms.LinkLabel()
        self._menuStrip1.SuspendLayout()
        self._flowLayoutPanel1.SuspendLayout()
        self._flowLayoutPanel2.SuspendLayout()
        self.SuspendLayout()
        # 
        # btnDebug1
        # 
        self._btnDebug1.Location = System.Drawing.Point(3, 170)
        self._btnDebug1.Name = "btnDebug1"
        self._btnDebug1.Size = System.Drawing.Size(75, 23)
        self._btnDebug1.TabIndex = 1
        self._btnDebug1.Text = "Debug1"
        self._btnDebug1.UseVisualStyleBackColor = True
        self._btnDebug1.Click += self.BtnDebug1Click
        # 
        # menuStrip1
        # 
        self._menuStrip1.Items.AddRange(System.Array[System.Windows.Forms.ToolStripItem](
            [self._fIleToolStripMenuItem]))
        self._menuStrip1.Location = System.Drawing.Point(0, 0)
        self._menuStrip1.Name = "menuStrip1"
        self._menuStrip1.Size = System.Drawing.Size(487, 24)
        self._menuStrip1.TabIndex = 2
        self._menuStrip1.Text = "menuStrip1"
        # 
        # fIleToolStripMenuItem
        # 
        self._fIleToolStripMenuItem.DropDownItems.AddRange(System.Array[System.Windows.Forms.ToolStripItem](
            [self._newToolStripMenuItem]))
        self._fIleToolStripMenuItem.Name = "fIleToolStripMenuItem"
        self._fIleToolStripMenuItem.Size = System.Drawing.Size(37, 20)
        self._fIleToolStripMenuItem.Text = "File"
        # 
        # newToolStripMenuItem
        # 
        self._newToolStripMenuItem.Name = "newToolStripMenuItem"
        self._newToolStripMenuItem.Size = System.Drawing.Size(98, 22)
        self._newToolStripMenuItem.Text = "New"
        self._newToolStripMenuItem.Click += self.OnFileNew
        # 
        # statusStrip1
        # 
        self._statusStrip1.Location = System.Drawing.Point(0, 381)
        self._statusStrip1.Name = "statusStrip1"
        self._statusStrip1.Size = System.Drawing.Size(487, 22)
        self._statusStrip1.TabIndex = 3
        self._statusStrip1.Text = "statusStrip1"
        # 
        # flowLayoutPanel1
        # 
        self._flowLayoutPanel1.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right
        self._flowLayoutPanel1.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink
        self._flowLayoutPanel1.Controls.Add(self._button1)
        self._flowLayoutPanel1.Controls.Add(self._button2)
        self._flowLayoutPanel1.Controls.Add(self._button3)
        self._flowLayoutPanel1.Location = System.Drawing.Point(0, 27)
        self._flowLayoutPanel1.Name = "flowLayoutPanel1"
        self._flowLayoutPanel1.Size = System.Drawing.Size(483, 32)
        self._flowLayoutPanel1.TabIndex = 4
        # 
        # button1
        # 
        self._button1.Location = System.Drawing.Point(3, 3)
        self._button1.Name = "button1"
        self._button1.Size = System.Drawing.Size(75, 23)
        self._button1.TabIndex = 0
        self._button1.Text = "New / Clear"
        self._button1.UseVisualStyleBackColor = True
        self._button1.Click += self.OnFileNew
        # 
        # button2
        # 
        self._button2.Location = System.Drawing.Point(84, 3)
        self._button2.Name = "button2"
        self._button2.Size = System.Drawing.Size(75, 23)
        self._button2.TabIndex = 1
        self._button2.Text = "Load"
        self._button2.UseVisualStyleBackColor = True
        self._button2.Click += self.OnLoadAll
        # 
        # button3
        # 
        self._button3.Location = System.Drawing.Point(165, 3)
        self._button3.Name = "button3"
        self._button3.Size = System.Drawing.Size(75, 23)
        self._button3.TabIndex = 2
        self._button3.Text = "Save"
        self._button3.UseVisualStyleBackColor = True
        self._button3.Click += self.OnSaveAll
        # 
        # textBox1
        # 
        self._textBox1.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right
        self._textBox1.Location = System.Drawing.Point(3, 66)
        self._textBox1.Multiline = True
        self._textBox1.Name = "textBox1"
        self._textBox1.Size = System.Drawing.Size(480, 68)
        self._textBox1.TabIndex = 5
        # 
        # flowLayoutPanel2
        # 
        self._flowLayoutPanel2.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right
        self._flowLayoutPanel2.Controls.Add(self._linkLabel1)
        self._flowLayoutPanel2.Controls.Add(self._linkLabel2)
        self._flowLayoutPanel2.Controls.Add(self._linkLabel3)
        self._flowLayoutPanel2.Controls.Add(self._linkLabel4)
        self._flowLayoutPanel2.FlowDirection = System.Windows.Forms.FlowDirection.TopDown
        self._flowLayoutPanel2.Location = System.Drawing.Point(245, 141)
        self._flowLayoutPanel2.Name = "flowLayoutPanel2"
        self._flowLayoutPanel2.Size = System.Drawing.Size(238, 73)
        self._flowLayoutPanel2.TabIndex = 6
        # 
        # linkLabel1
        # 
        self._linkLabel1.Location = System.Drawing.Point(3, 0)
        self._linkLabel1.Name = "linkLabel1"
        self._linkLabel1.Size = System.Drawing.Size(100, 23)
        self._linkLabel1.TabIndex = 0
        self._linkLabel1.TabStop = True
        self._linkLabel1.Text = "/"
        self._linkLabel1.LinkClicked += self.OnLinkClicked
        # 
        # linkLabel2
        # 
        self._linkLabel2.Location = System.Drawing.Point(3, 23)
        self._linkLabel2.Name = "linkLabel2"
        self._linkLabel2.Size = System.Drawing.Size(100, 23)
        self._linkLabel2.TabIndex = 1
        self._linkLabel2.TabStop = True
        self._linkLabel2.Text = "/modelsize"
        self._linkLabel2.LinkClicked += self.OnLinkClicked
        # 
        # linkLabel3
        # 
        self._linkLabel3.Location = System.Drawing.Point(3, 46)
        self._linkLabel3.Name = "linkLabel3"
        self._linkLabel3.Size = System.Drawing.Size(100, 23)
        self._linkLabel3.TabIndex = 2
        self._linkLabel3.TabStop = True
        self._linkLabel3.Text = "/dumpthings"
        self._linkLabel3.LinkClicked += self.OnLinkClicked
        # 
        # button4
        # 
        self._button4.Location = System.Drawing.Point(3, 141)
        self._button4.Name = "button4"
        self._button4.Size = System.Drawing.Size(75, 23)
        self._button4.TabIndex = 7
        self._button4.Text = "Dump Model"
        self._button4.UseVisualStyleBackColor = True
        self._button4.Click += self.OnDumpModel
        # 
        # listBox1
        # 
        self._listBox1.Anchor = System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left | System.Windows.Forms.AnchorStyles.Right
        self._listBox1.FormattingEnabled = True
        self._listBox1.Location = System.Drawing.Point(245, 227)
        self._listBox1.Name = "listBox1"
        self._listBox1.Size = System.Drawing.Size(238, 147)
        self._listBox1.TabIndex = 8
        # 
        # button5
        # 
        self._button5.Location = System.Drawing.Point(3, 227)
        self._button5.Name = "button5"
        self._button5.Size = System.Drawing.Size(75, 23)
        self._button5.TabIndex = 9
        self._button5.Text = "Add Thing"
        self._button5.UseVisualStyleBackColor = True
        self._button5.Click += self.OnAddThing
        # 
        # inputFieldTxt
        # 
        self._inputFieldTxt.Location = System.Drawing.Point(84, 230)
        self._inputFieldTxt.Name = "inputFieldTxt"
        self._inputFieldTxt.Size = System.Drawing.Size(117, 20)
        self._inputFieldTxt.TabIndex = 10
        # 
        # inputFieldTxtZ
        # 
        self._inputFieldTxtZ.Location = System.Drawing.Point(115, 270)
        self._inputFieldTxtZ.Name = "inputFieldTxtZ"
        self._inputFieldTxtZ.Size = System.Drawing.Size(108, 20)
        self._inputFieldTxtZ.TabIndex = 12
        # 
        # button6
        # 
        self._button6.Location = System.Drawing.Point(3, 267)
        self._button6.Name = "button6"
        self._button6.Size = System.Drawing.Size(106, 23)
        self._button6.TabIndex = 11
        self._button6.Text = "Add Info to Thing"
        self._button6.UseVisualStyleBackColor = True
        self._button6.Click += self.OnAddInfoToThing
        # 
        # button7
        # 
        self._button7.Location = System.Drawing.Point(3, 307)
        self._button7.Name = "button7"
        self._button7.Size = System.Drawing.Size(89, 23)
        self._button7.TabIndex = 13
        self._button7.Text = "Delete Thing"
        self._button7.UseVisualStyleBackColor = True
        self._button7.Click += self.OnDeleteThing
        # 
        # linkLabel4
        # 
        self._linkLabel4.Location = System.Drawing.Point(109, 0)
        self._linkLabel4.Name = "linkLabel4"
        self._linkLabel4.Size = System.Drawing.Size(100, 23)
        self._linkLabel4.TabIndex = 3
        self._linkLabel4.TabStop = True
        self._linkLabel4.Text = "/addthing"
        self._linkLabel4.LinkClicked += self.OnLinkClicked
        # 
        # MainForm
        # 
        self.BackColor = System.Drawing.SystemColors.InactiveCaption
        self.ClientSize = System.Drawing.Size(487, 403)
        self.Controls.Add(self._button7)
        self.Controls.Add(self._inputFieldTxtZ)
        self.Controls.Add(self._button6)
        self.Controls.Add(self._inputFieldTxt)
        self.Controls.Add(self._button5)
        self.Controls.Add(self._listBox1)
        self.Controls.Add(self._button4)
        self.Controls.Add(self._flowLayoutPanel2)
        self.Controls.Add(self._textBox1)
        self.Controls.Add(self._flowLayoutPanel1)
        self.Controls.Add(self._statusStrip1)
        self.Controls.Add(self._btnDebug1)
        self.Controls.Add(self._menuStrip1)
        self.MainMenuStrip = self._menuStrip1
        self.Name = "MainForm"
        self.Text = "AppMainConfigDotnet"
        self.FormClosed += self.onClosed
        self.Load += self.onLoad
        self._menuStrip1.ResumeLayout(False)
        self._menuStrip1.PerformLayout()
        self._flowLayoutPanel1.ResumeLayout(False)
        self._flowLayoutPanel2.ResumeLayout(False)
        self.ResumeLayout(False)
        self.PerformLayout()


    def BtnDebug1Click(self, sender, e):
        pass

    def OnFileNew(self, sender, e):
        pass

    def OnLoadAll(self, sender, e):
        pass

    def OnSaveAll(self, sender, e):
        pass

    def OnDumpModel(self, sender, e):
        pass

    def OnAddThing(self, sender, e):
        pass

    def OnAddInfoToThing(self, sender, e):
        pass

    def OnDeleteThing(self, sender, e):
        pass

    def OnLinkClicked(self, sender, e):
        pass

    def onClosed(self, sender, e):
        pass