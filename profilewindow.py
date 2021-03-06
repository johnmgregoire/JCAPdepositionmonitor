# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 6/12/2013
# For JCAP

from PyQt4 import QtCore, QtGui
import sys
import graph

""" window that displays profile after loading """
class ProfileWindow(QtGui.QMainWindow):

    """ takes in name that profile was saved under and list of
        variables to be graphed """
    def __init__(self, name = "None", varsList = []):
        super(ProfileWindow, self).__init__()
        self.name = name
        self.varsList = varsList
        self.graphs = [] 
        
        self.initUI()

    """ creates graphics in window """
    def initUI(self):
        # window width is based on number of graphs in profile
        self.setGeometry(0, 50, 200*(len(self.varsList)+1)+50, 800)
        self.setWindowTitle(self.name)

        # displays graphs in a grid format
        self.main_widget = QtGui.QWidget(self)
        self.setCentralWidget(self.main_widget)
        grid = QtGui.QGridLayout(self.main_widget)

        # creates and adds graphs to appropriate row
        num_graphs = len(self.varsList)
        midpoint = (num_graphs+1)/2
        for index in range(num_graphs):
            graphLayout = QtGui.QVBoxLayout()
            newGraph = graph.Graph(parent=None, xvarname="Time",
                                   yvarname=self.varsList[index])
            toolbar = graph.NavigationToolbar(newGraph, self)
            self.graphs += [newGraph]
            
            column = 0 if index < midpoint else 1
            grid.addLayout(graphLayout, column, index%midpoint)
            graphLayout.addWidget(toolbar)
            graphLayout.addWidget(newGraph)         

    """ called whenever new data is ready to be plotted """
    def updateWindow(self, newRow):
        for graph in self.graphs:
            graph.updatePlot(newRow)

    """ called by MainMenu every second """  
    def redrawWindow(self):
        for graph in self.graphs:
            graph.draw()

""" menu that shows avaiable profiles and loads user's selection """
class LoadMenu(QtGui.QDialog):

    # these signals will be sent to MainMenu
    profileChosen = QtCore.pyqtSignal(str)
    profileToDelete = QtCore.pyqtSignal(str)

    """ takes in a list of profiles saved for the current data file """
    def __init__(self, menuList = []):
        super(LoadMenu, self).__init__()

        self.setWindowTitle('Load Profile')

        # create the main layout and add the list of profiles
        self.layout = QtGui.QVBoxLayout(self)
        self.list = QtGui.QListWidget(self)
        self.list.addItems(menuList)
        self.layout.addWidget(self.list)

        # create and activate OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.setStandardButtons(QtGui.QDialogButtonBox.Ok
                                         | QtGui.QDialogButtonBox.Cancel)
        deleteButton = QtGui.QPushButton('Delete')
        buttons.addButton(deleteButton, QtGui.QDialogButtonBox.DestructiveRole)
        buttons.accepted.connect(self.sendName)
        buttons.rejected.connect(self.close)
        deleteButton.clicked.connect(self.deleteName)
        self.layout.addWidget(buttons)

    """ sends name of selected profile to MainMenu,
        which will then load the profile in a new window """
    def sendName(self):
        name = str(self.list.currentItem().text())
        self.profileChosen.emit(name)
        self.close()

    def deleteName(self):
        name = str(self.list.currentItem().text())
        confirm = QtGui.QMessageBox.question(None, 'Delete Profile',
                                             'Are you sure you want to delete this profile?',
                                             QtGui.QMessageBox.Yes |
                                             QtGui.QMessageBox.No)
        if (confirm == QtGui.QMessageBox.Yes):
            self.profileToDelete.emit(name)
        self.close()

    """ called by MainMenu every second; nothing for this widget to do """
    def redrawWindow(self):
        pass
