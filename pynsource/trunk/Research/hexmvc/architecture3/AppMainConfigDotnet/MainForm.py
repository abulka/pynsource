import System.Drawing
import System.Windows.Forms

from System.Drawing import *
from System.Windows.Forms import *

class MainForm(Form):
    def __init__(self):
        self.InitializeComponent()
    
    def InitializeComponent(self):
        self._btnBoot1 = System.Windows.Forms.Button()
        self._btnDebug1 = System.Windows.Forms.Button()
        self.SuspendLayout()
        # 
        # btnBoot1
        # 
        self._btnBoot1.Location = System.Drawing.Point(12, 23)
        self._btnBoot1.Name = "btnBoot1"
        self._btnBoot1.Size = System.Drawing.Size(113, 23)
        self._btnBoot1.TabIndex = 0
        self._btnBoot1.Text = "BOOT"
        self._btnBoot1.UseVisualStyleBackColor = True
        self._btnBoot1.Click += self.Button1Click
        # 
        # btnDebug1
        # 
        self._btnDebug1.Location = System.Drawing.Point(197, 23)
        self._btnDebug1.Name = "btnDebug1"
        self._btnDebug1.Size = System.Drawing.Size(75, 23)
        self._btnDebug1.TabIndex = 1
        self._btnDebug1.Text = "Debug1"
        self._btnDebug1.UseVisualStyleBackColor = True
        self._btnDebug1.Click += self.BtnDebug1Click
        # 
        # MainForm
        # 
        self.ClientSize = System.Drawing.Size(284, 262)
        self.Controls.Add(self._btnDebug1)
        self.Controls.Add(self._btnBoot1)
        self.Name = "MainForm"
        self.Text = "AppMainConfigDotnet"
        self.ResumeLayout(False)


    def Button1Click(self, sender, e):
        print "GOT EVENT!!!!!"

    def BtnDebug1Click(self, sender, e):
        pass