# Editor.py
from Statechart import Statechart
from TopHandler import TopHandler
from GUI import GUI


class Editor:
    def __init__(self):
        self.topHandler = TopHandler()
        self.GUI = GUI(self.topHandler)
        self.topHandler.setGUI(self.GUI)
        self.statechart = Statechart(self.GUI.getStatechartHandler())
        self.statechart.setCanvas(self.GUI.getCanvas())
        self.topHandler.setStatechart(self.statechart)

    def start(self):
        self.GUI.mainloop()


if __name__ == "__main__":
    editor = Editor()
    editor.start()
