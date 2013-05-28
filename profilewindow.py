# Allison Schubauer and Daisy Hernandez
# Created: 5/28/2013
# Last Updated: 5/28/2013
# For JCAP

from PyQt4 import QtGui
from graph import *

class ProfileWindow(QtGui.QMainWindow):

    def __init__(self, varsList = []):
        super(ProfileWindow, self).__init__()
        self.varsList = varsList
        self.graphs = []
        print self.varsList
        
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 200, 200*(len(self.varsList)+1), 600)
        self.setWindowTitle('Profile Name Here') # make option to save profile name

        self.main_widget = QtGui.QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.rows = QtGui.QVBoxLayout(self.main_widget)
        self.row1 = QtGui.QHBoxLayout()
        self.row2 = QtGui.QHBoxLayout()
        self.rows.addLayout(self.row1)
        self.rows.addLayout(self.row2)

        num_graphs = len(self.varsList)
        midpoint = (num_graphs+1)/2
        print midpoint
        first_row = self.varsList[:midpoint]
        print len(first_row)
        second_row = self.varsList[midpoint:]
        print len(second_row)
        for var in first_row:
            newGraph = Graph(parent=None, xvarname="Time", yvarname=var)
            self.graphs += [newGraph]
            self.row1.addWidget(newGraph)
        for var in second_row:
            newGraph = Graph(parent=None, xvarname="Time", yvarname=var)
            self.graphs += [newGraph]
            self.row2.addWidget(newGraph)
        if len(second_row) != midpoint:
            print "rows not same length"
            self.row2.addStretch(1)
        """for col in range((len(self.varsList)+1)/2):
            self.cols += [QtGui.QHBoxLayout()]
            self.rows.addLayout(self.cols[col])
        print len(self.cols)"""

    def updateWindow(self):
        pass
