# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 5/28/2013
# For JCAP

from PyQt4 import QtCore, QtGui
from graph import *

class ProfileWindow(QtGui.QMainWindow):

    def __init__(self, name = "None", varsList = []):
        super(ProfileWindow, self).__init__()
        self.name = name
        self.varsList = varsList
        self.graphs = [] 
        
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 200, 200*(len(self.varsList)+1)+100, 650)
        self.setWindowTitle(self.name)

        self.main_widget = QtGui.QWidget(self)
        self.setCentralWidget(self.main_widget)
        grid = QtGui.QGridLayout(self.main_widget)

        num_graphs = len(self.varsList)
        midpoint = (num_graphs+1)/2
        first_row = self.varsList[:midpoint]
        second_row = self.varsList[midpoint:]
        for index in range(len(first_row)):
            newGraph = Graph(parent=None, xvarname="Time",
                             yvarname=first_row[index])
            self.graphs += [newGraph]
            grid.addWidget(newGraph, 0, index)
        for index in range(len(second_row)):
            newGraph = Graph(parent=None, xvarname="Time",
                             yvarname=second_row[index])
            self.graphs += [newGraph]
            grid.addWidget(newGraph, 1, index)

    def updateWindow(self):
        for graph in self.graphs:
            graph.updatePlot()

class LoadMenu(QtGui.QDialog):

    profileChosen = QtCore.pyqtSignal(str)

    def __init__(self, menuList = []):
        super(LoadMenu, self).__init__()

        self.setWindowTitle('Load Profile')

        self.layout = QtGui.QVBoxLayout(self)
        self.list = QtGui.QListWidget(self)
        self.list.addItems(menuList)
        self.layout.addWidget(self.list)

        buttons = QtGui.QDialogButtonBox()
        buttons.setStandardButtons(QtGui.QDialogButtonBox.Ok
                                         | QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.sendName)
        buttons.rejected.connect(self.close)
        self.layout.addWidget(buttons)
        
    def sendName(self):
        name = str(self.list.currentItem().text())
        self.profileChosen.emit(name)
        self.close()

    def updateWindow(self):
        pass
