# Allison Schubauer and Daisy Hernandez
# Created: 6/5/2013
# Last Updated: 6/6/2013
# For JCAP

from PyQt4 import QtGui, QtCore
from depgraph import *
import re
import sys

class DepositionWindow(QtGui.QMainWindow):

    def __init__(self):
        super(DepositionWindow, self).__init__()

        self.Lmnts = {}
        self.initUI()

    """ draws the user interface of the window """
    def initUI(self):
        # set window size and position on screen
        self.setGeometry(300, 200, 1000, 600)

        # main_widget holds all other widgets in window
        self.main_widget = QtGui.QWidget(self)

        # initialize the graph
        self.depgraph = DepositionGraph(self.main_widget)

        self.setWindowTitle("Deposition Window - Work In Progress")

        # set main_widget as center of window
        self.setCentralWidget(self.main_widget)

        # dealing with layouts and design
        self.mainlayout = QtGui.QGridLayout(self.main_widget)
        self.sidelayout = QtGui.QGridLayout(self.main_widget)

        # adding layouts to one another
        self.mainlayout.addWidget(self.depgraph,0,0)
        self.mainlayout.addLayout(self.sidelayout,0,1)

        #set the streches
        self.mainlayout.setColumnStretch(0,5)
        self.mainlayout.setColumnStretch(1,0)

        #drop down widget, text widgets, ect
        self.selectUnits = QtGui.QComboBox()
        self.chemEQ = QtGui.QLineEdit(self)
        self.procChem = QtGui.QPushButton('Enter')

        # set connections up
        self.procChem.clicked.connect(self.handleEQ)

        # labels
        self.label_chemEQ = QtGui.QLabel('Chemical equation:')
        self.unitOptions = ["A/s"]

        for unit in self.unitOptions:
            self.selectUnits.addItem(unit)

        self.selectUnits.activated[str].connect(self.selectConversion)

        self.sidelayout.setAlignment(QtCore.Qt.AlignTop)

        #adding to sidelayout
        self.sidelayout.addWidget(self.selectUnits)
        self.sidelayout.addWidget(self.label_chemEQ)
        self.sidelayout.addWidget(self.chemEQ)
        self.sidelayout.addWidget(self.procChem)


        self.show()


    def selectConversion(self, unitName):
        print unitName

    def handleEQ(self):
        formula = self.chemEQ.text()
        if not self.checkRegEx(formula):
            message = """The equation you entered is of the wrong format.
                        Some examples are: FeO and FeO1.5"""
            inputError = QtGui.QMessageBox.information(None,"Wrong Format", message)
        

    def checkRegEx(self,text):
        
        reg1 = '[A-Z]'
        reg2 = '[a-z]?'
        reg3 = '([ONBC])'
        reg4 = '[\d]*'
        reg5 = '(\.\d+)?'
        
        totalReg = '(' + reg1+reg2 + ')' + reg3 + '(' + reg4 + reg5 + ')'

        regEX = re.compile(totalReg)
        x = re.match(regEX,str(text))

        if x:
            metalName = x.group(1)
            otherElmntName = x.group(2)
            otherElmntStoich  = x.group(3)
            
            if otherElmntStoich == "":
                otherElmntStoich = 1.

            self.Lmnts["Metal Name"] = metalName
            self.Lmnts["Second Element"] = otherElmntName
            self.Lmnts["Second Element Stoich"] = otherElmntStoich
            
            return True
        
        return False

    def updateWindow(self,newRow):
        pass

    def redrawWindow(self):
        pass
